"""Deterministic context retrieval and byte-bounded pagination for CTM."""
from __future__ import annotations

import base64
import copy
from datetime import datetime

from project_memory import MemoryError, decode, digest, encode, sanitize


def page(result, graph, options, context=None):
    limit, count_limit = options.max_bytes, options.max_nodes
    capsule_limit = options.max_capsules
    if limit < 1024 or count_limit < 1 or not 1 <= capsule_limit <= 5:
        raise MemoryError("limits require bytes >= 1024, nodes >= 1 and capsules between 1 and 5")
    signature = digest(encode({"result": result, "graph": graph, "context": context}))
    offset = 0
    if options.cursor:
        try:
            cursor = decode(base64.urlsafe_b64decode(options.cursor.encode()))
            if cursor["signature"] != signature or not isinstance(cursor["offset"], int):
                raise MemoryError("cursor snapshot changed; restart query")
            offset = cursor["offset"]
        except (ValueError, KeyError, TypeError) as exc:
            raise MemoryError("invalid or stale cursor") from exc
    root = result["root"]
    # Stable categories, not relevance scores or weighted ranking.
    def order(key):
        node = result["nodes"][key]
        return (key != root, node["type"] != "task", node["type"] != "decision", key)
    records = [("node", key, result["nodes"][key]) for key in sorted(result["nodes"], key=order)]
    records += [("edge", str(i), edge) for i, edge in enumerate(result["edges"])]
    if not 0 <= offset <= len(records):
        raise MemoryError("cursor offset out of range")
    pending = {k for k, n in result["nodes"].items() if n["type"] == "task" and n["status"] != "completed"}
    packet = {"root": root, "hops": result["hops"], "revision": graph["revision"],
              "nodes": {}, "edges": [], "truncated": False, "next_cursor": None,
              "omitted_pending_tasks": len(pending), "oversized_records": [],
              "total_nodes": len(result["nodes"]), "total_edges": len(result["edges"]),
              "references_may_require_other_pages": True}
    if context:
        packet["context"] = context
    def finish(candidate, position):
        candidate["truncated"] = position < len(records) or bool(candidate["oversized_records"])
        candidate["next_cursor"] = base64.urlsafe_b64encode(encode({"signature": signature, "offset": position})).decode() if position < len(records) else None
        candidate["omitted_pending_tasks"] = len(pending - candidate["nodes"].keys())
        return candidate
    if len(encode(finish(copy.deepcopy(packet), offset))) > limit:
        # Keep an explicit reference when even the optional state preview is too big.
        packet["context"].pop("state_preview", None)
        packet["context"]["preview_omitted"] = True
    if len(encode(finish(copy.deepcopy(packet), offset))) > limit:
        raise MemoryError("budget too small for response envelope")
    position, capsules = offset, 0
    while position < len(records):
        kind, key, value = records[position]
        is_capsule = kind == "node" and value["type"] == "session"
        if kind == "node" and (len(packet["nodes"]) >= count_limit or is_capsule and capsules >= capsule_limit):
            break
        candidate = copy.deepcopy(packet)
        if kind == "node":
            candidate["nodes"][key] = value
        else:
            candidate["edges"].append(value)
        finish(candidate, position + 1)
        if len(encode(candidate)) > limit:
            if position > offset:
                break
            # Do not loop forever on a single huge node/edge. Emit a reference and
            # tell the caller to request that ID with a larger explicit budget.
            stub = {"kind": kind, "id": key, "action": "query exact node ID with larger --max-bytes"}
            if kind == "edge":
                stub.update(source=value["source"], target=value["target"], relation=value["relation"])
            candidate = copy.deepcopy(packet)
            candidate["oversized_records"].append(stub)
            finish(candidate, position + 1)
            if len(encode(candidate)) > limit:
                raise MemoryError("budget too small for oversized-record reference")
        packet = candidate
        capsules += int(is_capsule)
        position += 1
    return finish(packet, position)


def resume_context(store, graph, requested):
    sessions = [n for n in graph["nodes"].values() if n["type"] == "session"]
    sessions.sort(key=lambda n: (datetime.fromisoformat(n["created_at"]), n["id"]), reverse=True)
    fallback_workspace = next((k for k, n in graph.get("nodes", {}).items() if n.get("type") == "workspace"), "workspace")
    chosen = requested or (sessions[0]["id"] if sessions else fallback_workspace)
    state = store.latest_state
    context = {"state_path": store.relative(state), "state_missing": not state.is_file(),
               "selection": "explicit node" if requested else "latest indexed session" if sessions else "workspace fallback",
               "raw_history_loaded": False, "warnings": []}
    if state.is_file():
        with state.open("rb") as stream:
            raw = stream.read(2049)
        if raw.startswith(b"# CTM resume v2"):
            from memory_transactions import verify_state
            if len(raw) > 2048:
                raise MemoryError("v2 state pointer exceeds expected size")
            pointer = verify_state(store, graph, raw)
            if not requested:
                chosen = pointer["session_id"]
                context["selection"] = "published closure"
            context["published_session"] = pointer["session_id"]
            context["published_revision"] = pointer["graph_revision"]
        context["state_preview_truncated"] = len(raw) > 2048
        if len(raw) > 2048:
            context["state_preview_omitted"] = True
            context["warnings"].append("state preview withheld: oversized content requires local review")
        else:
            context["state_preview"] = raw.decode("utf-8", errors="ignore")
            try:
                sanitize(context["state_preview"])
            except MemoryError:
                context.pop("state_preview")
                context["warnings"].append("state preview withheld: potential sensitive content requires local review")
        if not raw.startswith(b"# CTM resume v2"):
            context["warnings"].append("legacy state: not transactionally linked to graph; review pending handoff")
    elif not sessions:
        context["warnings"].append("no indexed session or current state; choose an existing node")
    return chosen, context
