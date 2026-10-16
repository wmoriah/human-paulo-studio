"""Recoverable close: immutable capsule -> graph -> state -> durable receipt.

The journal contains exact before/after bytes. Recovery is roll-forward only and
refuses to overwrite an unexpected external edit. A lock covers the whole flow.
"""
from __future__ import annotations

import base64
import copy
import os

from project_memory import (ID, VERSION, MemoryError, atomic, capsule_bytes, check,
                        decode, digest, encode, immutable, indexed_capsule, now,
                        safe_path, validate_capsule, validate_graph)
from memory_analysis import completion_gate, sync_conflicts

STATE_PREFIX = b"# CTM resume v2\n\n```json\n"
STATE_SUFFIX = b"```\n"


def optional_bytes(path):
    return path.read_bytes() if path.exists() else None


def pack(raw):
    return base64.b64encode(raw).decode() if raw is not None else None


def unpack(value):
    try:
        return base64.b64decode(value, validate=True) if value is not None else None
    except (ValueError, TypeError) as exc:
        raise MemoryError("invalid transaction snapshot") from exc


def state_pointer(raw):
    if not raw.startswith(STATE_PREFIX) or not raw.endswith(STATE_SUFFIX):
        raise MemoryError("invalid v2 state pointer")
    pointer = decode(raw[len(STATE_PREFIX):-len(STATE_SUFFIX)])
    check(pointer["session_id"], ID)
    if type(pointer["graph_revision"]) is not int or pointer["graph_revision"] < 0:
        raise MemoryError("invalid state revision")
    return pointer


def verify_state(store, graph, raw):
    pointer = state_pointer(raw)
    node = graph["nodes"].get(pointer["session_id"])
    if not node or node["type"] != "session" or pointer["graph_revision"] > graph["revision"]:
        raise MemoryError("state and graph are inconsistent")
    path = store.relative(store.capsules / (pointer["session_id"] + ".md"))
    if node["metadata"].get("capsule_path") != path or node["metadata"].get("capsule_sha256") != pointer["capsule_sha256"]:
        raise MemoryError("state and session capsule are inconsistent")
    if digest(safe_path(store.root, path).read_bytes()) != pointer["capsule_sha256"]:
        raise MemoryError("published capsule changed; create a correction capsule")
    return pointer


def inject(store, phase):
    # Explicit opt-in fixture only; never enabled on CTM's real workspace.
    if (store.root / ".memory-test-root").is_file() and os.environ.get("CTM_MEMORY_TEST_FAIL_AFTER") == phase:
        os._exit(91)


def pending_journal(store):
    pointer = optional_bytes(store.runtime / "pending.json")
    if pointer is None:
        return None
    pointer = decode(pointer)
    if pointer.get("status") == "done":
        return None
    tx = pointer.get("transaction")
    if not isinstance(tx, str) or len(tx) != 64 or any(c not in "0123456789abcdef" for c in tx):
        raise MemoryError("invalid pending transaction ID")
    return decode((store.runtime / "transactions" / tx / "journal.json").read_bytes())


def recover_locked(store, journal):
    sid = journal["session_id"]
    check(sid, ID)
    paths = {"capsule": store.capsules / (sid + ".md"),
             "graph": store.path, "state": store.latest_state}
    snapshots = journal["files"]
    if set(snapshots) != set(paths):
        raise MemoryError("invalid transaction files")
    if digest(unpack(snapshots["capsule"]["after"])) != journal["transaction"]:
        raise MemoryError("transaction capsule hash mismatch")
    # Preflight ALL targets before writing any; retain journal on disagreement.
    for kind, path in paths.items():
        entry = snapshots[kind]
        if optional_bytes(path) not in (unpack(entry["before"]), unpack(entry["after"])):
            raise MemoryError("transaction target changed externally; manual review required")
    new_graph = decode(unpack(snapshots["graph"]["after"]))
    validate_graph(new_graph, store.root)
    for kind, path in paths.items():
        raw = unpack(snapshots[kind]["after"])
        if kind == "capsule":
            immutable(path, raw)
        elif optional_bytes(path) != raw:
            atomic(path, raw)
        inject(store, kind)
    verify_state(store, new_graph, paths["state"].read_bytes())
    atomic(store.runtime / "pending.json", encode({"status": "done", "transaction": journal["transaction"]}))
    inject(store, "receipt")
    return {"closed": True, "session_id": sid, "revision": new_graph["revision"],
            "transaction": journal["transaction"], "state_path": store.relative(store.latest_state)}


def recover(store):
    with store.locked():
        journal = pending_journal(store)
        return recover_locked(store, journal) if journal else {"recovered": False, "pending": False}


def close_session(store, capsule, expected):
    raw = capsule_bytes(capsule)
    tx = digest(raw)
    with store.locked():
        journal = pending_journal(store)
        if journal:
            if journal["transaction"] != tx:
                raise MemoryError("another closure is pending; run recover first")
            return recover_locked(store, journal)
        graph = store.load()
        if decode(store.path.read_bytes())["version"] != VERSION:
            raise MemoryError("explicit migration required before closing")
        receipt = store.runtime / "transactions" / tx / "journal.json"
        if receipt.exists():
            saved = decode(receipt.read_bytes())
            path = store.capsules / (saved["session_id"] + ".md")
            if optional_bytes(path) != raw or graph["nodes"].get(saved["session_id"], {}).get("metadata", {}).get("capsule_sha256") != tx:
                # Crash after journal fsync but before pending-pointer publication.
                if store.path.read_bytes() != unpack(saved["files"]["graph"]["before"]):
                    raise MemoryError("closed history changed; review required")
                atomic(store.runtime / "pending.json", encode({"status": "pending", "transaction": tx}))
                return recover_locked(store, saved)
            verify_state(store, graph, store.latest_state.read_bytes())
            return {"closed": True, "already_closed": True, "session_id": saved["session_id"], "revision": graph["revision"]}
        validate_capsule(capsule, store.root)
        if graph["revision"] != expected:
            raise MemoryError("revision conflict; reload before closing")
        path = store.relative(store.capsules / (capsule["id"] + ".md"))
        previous_capsule = optional_bytes(safe_path(store.root, path))
        if previous_capsule is not None and previous_capsule != raw:
            raise MemoryError("immutable capsule already exists with different content")
        updated = indexed_capsule(copy.deepcopy(graph), capsule, raw, path, store.root)
        completion_gate(updated, store.root, graph)
        sync_conflicts(updated)
        updated["revision"] = graph["revision"] + 1
        updated["updated_at"] = now()
        validate_graph(updated, store.root)
        pointer = {"session_id": capsule["id"], "capsule_sha256": tx,
                   "graph_revision": updated["revision"], "transaction": tx}
        state = STATE_PREFIX + encode(pointer) + STATE_SUFFIX
        journal = {"version": 1, "transaction": tx, "session_id": capsule["id"], "files": {
            "capsule": {"before": pack(previous_capsule), "after": pack(raw)},
            "graph": {"before": pack(store.path.read_bytes()), "after": pack(encode(updated))},
            "state": {"before": pack(optional_bytes(store.latest_state)), "after": pack(state)},
        }}
        atomic(receipt, encode(journal))
        inject(store, "prepared")
        atomic(store.runtime / "pending.json", encode({"status": "pending", "transaction": tx}))
        inject(store, "journal")
        return recover_locked(store, journal)
