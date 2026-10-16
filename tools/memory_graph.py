#!/usr/bin/env python3
"""Public CLI for CTM's shared session memory."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from workspace_index import discover_root

from project_memory import (CAPSULE_SCHEMA, GRAPH_SCHEMA, MemoryError, Store, decode,
                        create_capsule, edge_key, encode, index_capsule, read_capsule,
                        resolve, upsert_edge, upsert_node, validate_capsule)
from memory_queries import page, resume_context
from memory_analysis import analysis, evidence_issues, impacted, task_issues, temporal_state
from memory_transactions import close_session, recover
from memory_migration import migrate_history, rollback


def neighbourhood(graph, node_id, hops, direction="both", relation=None, status=None, expand_workspace=True):
    if hops < 0:
        raise MemoryError("hops must be nonnegative")
    root = resolve(graph, node_id)
    seen, frontier, edges = {root}, {root}, []
    for _ in range(hops):
        nxt = set()
        for edge in graph["edges"]:
            if relation and edge["relation"] != relation:
                continue
            outgoing = direction in ("out", "both") and edge["source"] in frontier
            incoming = direction in ("in", "both") and edge["target"] in frontier
            if not (outgoing or incoming):
                continue
            targets = {edge["source"], edge["target"]}
            if status and any(graph["nodes"][k]["status"] != status for k in targets - {root}):
                continue
            if edge not in edges:
                edges.append(edge)
            nxt.update(targets - seen)
        seen.update(nxt)
        frontier = nxt if expand_workspace else {k for k in nxt if graph["nodes"][k]["type"] != "workspace"}
    return {"root": root, "hops": hops,
            "nodes": {k: graph["nodes"][k] for k in sorted(seen)},
            "edges": sorted(edges, key=edge_key)}


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=discover_root(Path(__file__)))
    subs = cli.add_subparsers(dest="command", required=True)
    for name in ("stats", "validate", "mermaid", "blocked", "stale", "conflicts", "recover"):
        subs.add_parser(name)
    q = subs.add_parser("query")
    q.add_argument("node_id")
    q.add_argument("--hops", type=int, default=1)
    q.add_argument("--direction", choices=["in", "out", "both"], default="both")
    q.add_argument("--relation")
    q.add_argument("--status")
    q.add_argument("--mermaid", action="store_true")
    def budget(command):
        command.add_argument("--max-bytes", type=int, default=12000)
        command.add_argument("--max-nodes", type=int, default=30)
        command.add_argument("--max-capsules", type=int, default=5)
        command.add_argument("--cursor")
    budget(q)
    for name in ("resume", "context"):
        command = subs.add_parser(name)
        command.add_argument("--node")
        command.add_argument("--hops", type=int, default=2)
        budget(command)
    subs.add_parser("search").add_argument("term")
    subs.add_parser("impact").add_argument("node_id")
    schema = subs.add_parser("schema")
    schema.add_argument("kind", choices=["graph", "capsule"])
    for kind in ("node", "edge"):
        group = subs.add_parser(kind).add_subparsers(dest="action", required=True)
        upsert = group.add_parser("upsert")
        upsert.add_argument("--file", type=Path, required=True)
        upsert.add_argument("--expected-revision", type=int, required=True)
    migrate = subs.add_parser("migrate")
    migrate.add_argument("--apply", action="store_true")
    migrate.add_argument("--expected-revision", type=int, default=0)
    migrate.add_argument("--history", action="store_true")
    migrate.add_argument("--selection-hash")
    restore = subs.add_parser("rollback")
    restore.add_argument("--backup", required=True)
    restore.add_argument("--expected-revision", type=int, required=True)
    restore.add_argument("--expected-hash", required=True)
    capsule = subs.add_parser("capsule").add_subparsers(dest="action", required=True)
    close = subs.add_parser("close")
    close.add_argument("--file", type=Path, required=True)
    close.add_argument("--expected-revision", type=int, required=True)
    for action in ("create", "validate", "index"):
        command = capsule.add_parser(action)
        command.add_argument("--file", required=True)
        if action == "index":
            command.add_argument("--expected-revision", type=int, required=True)
    return cli


def execute(args):
    store = Store(args.root)
    if args.command == "close":
        return close_session(store, decode(args.file.read_bytes()), args.expected_revision)
    if args.command == "recover":
        return recover(store)
    if args.command == "rollback":
        return rollback(store, args.backup, args.expected_revision, args.expected_hash)
    if args.command == "capsule":
        if args.action == "index":
            return index_capsule(store, args.file, args.expected_revision)
        if args.action == "create":
            return create_capsule(store, decode(Path(args.file).read_bytes()))
        if args.file.endswith(".md"):
            capsule, _ = read_capsule(store.root, args.file)
        else:
            capsule = decode(Path(args.file).read_bytes())
        validate_capsule(capsule, store.root)
        return {"valid": True, "id": capsule["id"]}
    if args.command == "schema":
        return {"$schema": "https://json-schema.org/draft/2020-12/schema", **(GRAPH_SCHEMA if args.kind == "graph" else CAPSULE_SCHEMA)}
    if args.command in ("node", "edge"):
        value = decode(args.file.read_bytes())
        fn = upsert_node if args.command == "node" else upsert_edge
        return store.mutate(args.expected_revision, lambda graph: fn(graph, value))
    if args.command == "migrate":
        if args.history:
            return migrate_history(store, args.apply, args.expected_revision, args.selection_hash)
        if args.apply:
            return store.mutate(args.expected_revision, lambda graph: graph, migrate=True)
        return {"dry_run": True, "graph": store.load()}
    with store.locked():
        return execute_read(args, store)


def execute_read(args, store):
    graph = store.load()
    if args.command in ("blocked", "stale", "conflicts"):
        result = analysis(graph, store.root)
        if args.command == "blocked":
            return [task for task in result["tasks"] if task["issues"]]
        return result[args.command]
    if args.command in ("resume", "context"):
        chosen, context = resume_context(store, graph, args.node)
        result = neighbourhood(graph, chosen, args.hops, expand_workspace=False)
        excluded = []
        for key, node in list(result["nodes"].items()):
            state = temporal_state(node)
            if node["type"] == "decision" and state in ("expired", "future", "superseded") and key != result["root"]:
                excluded.append({"id": key, "state": state})
                del result["nodes"][key]
                continue
            result["nodes"][key] = {**node, "memory_state": state,
                                     "review_issues": task_issues(graph, key, store.root) if node["type"] == "task" else evidence_issues(node, store.root)}
        visible_edges = [e for e in result["edges"] if e["source"] in result["nodes"] and e["target"] in result["nodes"]]
        result["edges"] = []
        for edge in visible_edges:
            issues = evidence_issues(edge, store.root)
            result["edges"].append({**edge, "review_issues": issues} if issues else edge)
        if excluded:
            context["excluded_decisions"] = excluded
        return page(result, graph, args, context)
    if args.command == "stats":
        return {"total_nodes": len(graph["nodes"]), "total_edges": len(graph["edges"]),
                "updated_at": graph["updated_at"], "revision": graph["revision"], "version": graph["version"],
                "persisted_version": decode(store.path.read_bytes())["version"]}
    if args.command == "validate":
        version = decode(store.path.read_bytes())["version"]
        return {"valid": True, "persisted_version": version, "read_version": graph["version"]}
    if args.command == "search":
        return [n for _, n in sorted(graph["nodes"].items()) if args.term.lower() in json.dumps(n, ensure_ascii=False).lower()]
    if args.command == "impact":
        key = resolve(graph, args.node_id)
        return {"node": graph["nodes"][key], "transitive_dependents": impacted(graph, key),
                "incoming": [e for e in graph["edges"] if e["target"] == key],
                "outgoing": [e for e in graph["edges"] if e["source"] == key]}
    if args.command == "mermaid":
        return neighbourhood(graph, "ctm", 2)
    result = neighbourhood(graph, args.node_id, args.hops, args.direction, args.relation, args.status)
    return result if args.mermaid else page(result, graph, args)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = execute(args)
        if args.command == "mermaid" or getattr(args, "mermaid", False):
            # Synthetic identifiers and HTML entities prevent Mermaid injection.
            ids = {key: f"n{i}" for i, key in enumerate(result["nodes"])}
            def label(value):
                return "".join(ch if ch.isalnum() or ch in " ._-" else f"&#{ord(ch)};" for ch in value)
            print("graph TD")
            for key, node in result["nodes"].items():
                print(f'    {ids[key]}["{label(node["label"])}"]')
            for edge in result["edges"]:
                print(f'    {ids[edge["source"]]} -->|"{edge["relation"]}"| {ids[edge["target"]]}')
        else:
            sys.stdout.buffer.write(encode(result))
        return 0
    except (MemoryError, OSError, KeyError, TypeError, RecursionError) as exc:
        message = str(exc) if isinstance(exc, MemoryError) else f"memory operation failed ({type(exc).__name__})"
        sys.stderr.buffer.write(encode({"error": message}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
