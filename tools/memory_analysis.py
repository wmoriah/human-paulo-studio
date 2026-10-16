"""Explicit dependencies and structured conflicts; no semantic inference."""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import combinations

from project_memory import MemoryError, digest, edge_key, encode, evidence, generated_node, now


def evidence_issues(record, root):
    issues = []
    for e in record["evidence"]:
        try:
            observed = evidence(root, e["path"])
            if observed != e:
                issues.append({"kind": "evidence_changed", "path": e["path"]})
        except (MemoryError, OSError):
            issues.append({"kind": "evidence_missing_or_unsafe", "path": e["path"]})
    return issues


def edge_identity(edge):
    return {"source": edge["source"], "relation": edge["relation"], "target": edge["target"]}


def edge_review_issue(edge, root):
    issues = evidence_issues(edge, root)
    if not issues:
        return None
    return {"kind": "edge_evidence_not_current", "edge": edge_identity(edge), "issues": issues}


def temporal_state(node, clock=None):
    clock = clock or datetime.now(timezone.utc)
    if node["status"] == "superseded":
        return "superseded"
    if "valid_from" in node and clock < datetime.fromisoformat(node["valid_from"]):
        return "future"
    if "valid_until" in node and clock >= datetime.fromisoformat(node["valid_until"]):
        return "expired"
    return node["status"]


def overlap(left, right):
    minimum, maximum = datetime.min.replace(tzinfo=timezone.utc), datetime.max.replace(tzinfo=timezone.utc)
    def bounds(n):
        return (datetime.fromisoformat(n["valid_from"]) if "valid_from" in n else minimum,
                datetime.fromisoformat(n["valid_until"]) if "valid_until" in n else maximum)
    a, b = bounds(left), bounds(right)
    return max(a[0], b[0]) < min(a[1], b[1])


def conflict_pairs(graph):
    groups = {}
    for node in graph["nodes"].values():
        if node["type"] == "decision" and node["status"] == "active":
            key = node["metadata"].get("key")
            if isinstance(key, str):
                groups.setdefault((node["scope"], key), []).append(node)
    pairs = []
    for group, nodes in sorted(groups.items()):
        for a, b in combinations(sorted(nodes, key=lambda n: n["id"]), 2):
            if encode(a["metadata"].get("value")) != encode(b["metadata"].get("value")) and overlap(a, b):
                pairs.append((group, a, b))
    return pairs


def sync_conflicts(graph):
    for (scope, key), a, b in conflict_pairs(graph):
        conflict_id = "conflict-" + digest(encode([scope, key, a["id"], b["id"]]))[:24]
        old = graph["nodes"].get(conflict_id)
        if old and old["type"] != "conflict":
            raise MemoryError("reserved conflict ID collision")
        if old and old["status"] == "open":
            continue
        ev = list({(e["path"], e["sha256"]): e for e in a["evidence"] + b["evidence"]}.values())
        node = generated_node(conflict_id, "conflict", "Structured decision conflict", now(), ev,
                              {"key": key, "decision_ids": [a["id"], b["id"]]}, status="open")
        node["scope"] = scope
        if old:
            node["revision"] = old["revision"] + 1
            node["created_at"] = old["created_at"]
        graph["nodes"][conflict_id] = node
        for target in (a["id"], b["id"]):
            edge = {"source": conflict_id, "target": target, "relation": "bloqueia", "evidence": ev}
            if not any(e["source"] == conflict_id and e["target"] == target and e["relation"] == "bloqueia" for e in graph["edges"]):
                graph["edges"].append(edge)
    return graph


def task_issues(graph, key, root, trail=None):
    trail = set() if trail is None else trail
    if key in trail:
        return [{"kind": "dependency_cycle", "node": key}]
    trail = trail | {key}
    node = graph["nodes"][key]
    issues = evidence_issues(node, root)
    if node["status"] in ("blocked", "needs_review", "superseded"):
        issues.append({"kind": "task_state_requires_review", "state": node["status"]})
    for edge in graph["edges"]:
        if edge["relation"] == "depende_de" and edge["source"] == key:
            edge_issue = edge_review_issue(edge, root)
            if edge_issue:
                issues.append(edge_issue)
            predecessor = graph["nodes"][edge["target"]]
            if predecessor["status"] != "completed":
                issues.append({"kind": "predecessor_pending", "node": predecessor["id"]})
            if predecessor["type"] == "task":
                if task_issues(graph, predecessor["id"], root, trail):
                    issues.append({"kind": "predecessor_requires_review", "node": predecessor["id"]})
        if edge["relation"] == "bloqueia" and edge["target"] == key:
            edge_issue = edge_review_issue(edge, root)
            if edge_issue:
                issues.append(edge_issue)
            blocker = graph["nodes"][edge["source"]]
            if blocker["status"] not in ("resolved", "completed", "superseded"):
                issues.append({"kind": "explicit_blocker", "node": blocker["id"]})
        if edge["relation"] == "validado_por" and edge["source"] == key:
            edge_issue = edge_review_issue(edge, root)
            if edge_issue:
                issues.append(edge_issue)
    required = node["metadata"].get("required_validations", [])
    if not isinstance(required, list) or any(not isinstance(k, str) for k in required):
        raise MemoryError("required_validations must be an array of IDs")
    if not required:
        issues.append({"kind": "acceptance_criteria_missing"})
    for validation_id in required:
        validation = graph["nodes"].get(validation_id)
        if not validation or validation["type"] != "validation":
            issues.append({"kind": "validation_missing", "node": validation_id})
        elif validation["metadata"].get("result") != "passed" or not validation["evidence"] or evidence_issues(validation, root):
            issues.append({"kind": "validation_not_proven", "node": validation_id})
    return issues


def completion_gate(graph, root, previous=None):
    """Gate transitions, not historical reads after external evidence changes."""
    previous = previous or {"nodes": {}}
    for key, node in graph["nodes"].items():
        old = previous["nodes"].get(key)
        if old == node:
            continue
        if node["type"] == "task" and node["status"] == "completed":
            if task_issues(graph, key, root):
                raise MemoryError("task completion lacks current evidence or dependencies")
        if node["type"] == "conflict" and node["status"] == "resolved":
            resolution = node["metadata"].get("resolution")
            if not isinstance(resolution, str) or not resolution.strip() or not node["evidence"] or evidence_issues(node, root):
                raise MemoryError("conflict resolution requires explanation and current evidence")
            members = set(node["metadata"].get("decision_ids", []))
            if any({a["id"], b["id"]} <= members for _, a, b in conflict_pairs(graph)):
                raise MemoryError("conflicting active decisions remain; explicit reconciliation required")


def analysis(graph, root):
    stale, tasks, stale_edges = [], [], []
    for key, node in sorted(graph["nodes"].items()):
        issues = evidence_issues(node, root)
        state = temporal_state(node)
        if issues or state in ("superseded", "expired", "future", "needs_review"):
            stale.append({"id": key, "state": state, "issues": issues})
        if node["type"] == "task":
            problems = task_issues(graph, key, root)
            tasks.append({"id": key, "status": node["status"], "ready_to_complete": not problems, "issues": problems})
    for edge in sorted(graph["edges"], key=edge_key):
        issue = edge_review_issue(edge, root)
        if issue:
            item = {"edge": issue["edge"], "state": "needs_review", "issues": issue["issues"]}
            stale.append(item)
            stale_edges.append(item)
    return {"stale": stale, "tasks": tasks,
            "stale_edges": stale_edges,
            "conflicts": [n for n in graph["nodes"].values() if n["type"] == "conflict" and n["status"] == "open"],
            "limitation": "structured conflicts only; prose contradictions require review"}


def impacted(graph, key):
    found, frontier = {key}, {key}
    while frontier:
        nxt = set()
        for node in graph["nodes"].values():
            if node["type"] == "task" and set(node["metadata"].get("required_validations", [])) & frontier:
                nxt.add(node["id"])
        for e in graph["edges"]:
            if e["relation"] in ("depende_de", "validado_por") and e["target"] in frontier:
                nxt.add(e["source"])
            if e["relation"] in ("evidencia_de", "bloqueia") and e["source"] in frontier:
                nxt.add(e["target"])
        frontier = nxt - found
        found.update(frontier)
    return sorted(found - {key})
