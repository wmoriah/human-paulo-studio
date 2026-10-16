"""Explicit, conservative historical references; never extract facts from prose."""
from __future__ import annotations

from project_memory import (CAPSULE_PREFIX, MemoryError, atomic, decode, digest, encode,
                        generated_node, immutable, now, safe_path, sanitize, upgrade,
                        upsert_edge)


def inventory(store):
    records = []
    folder = store.capsules
    paths = sorted(folder.glob("*.md")) if folder.is_dir() else []
    state = store.latest_state
    if state.is_file():
        paths.append(state)
    for path in paths:
        relative = path.relative_to(store.root).as_posix()
        record = {"path": relative}
        try:
            raw = safe_path(store.root, relative).read_bytes()
            record.update(sha256=digest(raw), bytes=len(raw))
            sanitize(raw.decode("utf-8"))
            if path.name == "README.md":
                record.update(action="excluded", reason="directory documentation, not session")
            elif raw.startswith(CAPSULE_PREFIX.encode()) or raw.startswith(b"# CTM resume v2"):
                record.update(action="excluded", reason="v2 document: use capsule index or published state")
            else:
                record.update(action="legacy_reference", reason="unstructured history: no facts, dates or validation inferred")
                if relative == store.relative(store.latest_state):
                    record["reference_path"] = store.relative(store.chat_off / "legacy" / (digest(raw) + ".md"))
        except (MemoryError, UnicodeDecodeError, OSError):
            record.update(action="excluded", reason="unsafe, unreadable or potentially sensitive: manual review")
        records.append(record)
    return {"files": records, "selection_hash": digest(encode(records)),
            "state_policy": "preserve state and capsules as independent legacy references; no date-based precedence",
            "excluded_areas": ["auth", "admin", "cache", "logs", "handoff", "raw conversation history"]}


def migrate_history(store, apply=False, expected=0, expected_selection=None):
    if not apply:
        store.ensure_no_pending()
        return {"dry_run": True, **inventory(store), "graph": store.load()}
    if not expected_selection:
        raise MemoryError("history apply requires --selection-hash from reviewed dry-run")
    report = None
    def transform(graph):
        nonlocal report
        report = inventory(store)
        if report["selection_hash"] != expected_selection:
            raise MemoryError("history inventory changed; review dry-run again")
        stamp = now()
        for item in report["files"]:
            if item["action"] != "legacy_reference":
                continue
            path = item.get("reference_path", item["path"])
            if path != item["path"]:
                immutable(safe_path(store.root, path), safe_path(store.root, item["path"]).read_bytes())
            key = "legacy-" + digest(item["path"].encode())[:24]
            ev = [{"path": path, "sha256": item["sha256"]}]
            existing = graph["nodes"].get(key)
            if existing:
                if existing["type"] != "artifact" or existing["evidence"] != ev:
                    raise MemoryError("legacy historical reference changed; correction requires review")
                continue
            node = generated_node(key, "artifact", "Legacy reference: " + item["path"], stamp, ev,
                {"source_path": item["path"], "legacy_reference": True,
                 "unknown": ["session identity", "validation results", "decision status", "dependencies"]}, status="legacy")
            graph["nodes"][key] = node
            if "ctm" in graph["nodes"]:
                upsert_edge(graph, {"source": "ctm", "target": key, "relation": "registra", "evidence": ev})
        return graph
    result = store.mutate(expected, transform, migrate=True)
    return {**result, "inventory": report, "graph_sha256": digest(store.path.read_bytes())}


def rollback(store, backup, expected, expected_hash):
    with store.locked():
        store.ensure_no_pending()
        file = safe_path(store.root, backup)
        if file.parent != (store.runtime / "backups").resolve() or file.suffix != ".json":
            raise MemoryError("rollback accepts only canonical content-addressed backups")
        raw = file.read_bytes()
        if file.stem != digest(raw):
            raise MemoryError("backup hash mismatch")
        current = store.path.read_bytes()
        if digest(current) != expected_hash or store.load()["revision"] != expected:
            raise MemoryError("rollback target changed; refuse to overwrite newer work")
        upgrade(decode(raw), store.root)
        state = store.latest_state
        if state.is_file() and state.read_bytes().startswith(b"# CTM resume v2"):
            raise MemoryError("published closures exist; graph-only rollback would break state")
        atomic(store.runtime / "backups" / (digest(current) + ".json"), current)
        atomic(store.path, raw)
        return {"restored": True, "sha256": digest(raw), "retained": "immutable history and legacy reference copies"}
