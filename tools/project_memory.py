"""Validated local memory storage for the existing CTM memory_graph CLI.

No network access or third-party dependencies. Persisted v1 is readable; writes
require an explicit migration and an expected revision. POSIX flock protects
read-modify-write operations shared by CTM's local CLIs.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from workspace_index import path as indexed_path

VERSION = "2.0.0"
NODE_TYPES = ["workspace", "workflow", "session", "objective", "decision", "artifact", "validation", "task", "conflict"]
RELATIONS = ["produziu", "pertence_a", "depende_de", "bloqueia", "validado_por", "evidencia_de", "substitui", "retoma", "utiliza", "registra"]
STATES = ["active", "pending", "in_progress", "blocked", "completed", "superseded", "needs_review", "open", "resolved", "legacy"]
ID = {"type": "string", "pattern": r"^[a-z0-9][a-z0-9._-]{0,159}$"}
TEXT = {"type": "string", "minLength": 1}
STAMP = {"type": "string", "format": "date-time"}
STRINGS = {"type": "array", "items": TEXT}


class MemoryError(ValueError):
    """Safe error message; never echo untrusted payloads or secret values."""


def now():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise MemoryError("duplicate JSON key")
        result[key] = value
    return result


def decode(data):
    try:
        return json.loads(data, object_pairs_hook=_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(MemoryError("non-finite JSON number")))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise MemoryError("invalid JSON") from exc


def obj(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False}


EVIDENCE = obj({"path": TEXT, "sha256": {"type": "string", "pattern": r"^[a-f0-9]{64}$"}})
EVIDENCES = {"type": "array", "items": EVIDENCE}
NODE = obj({
    "id": ID, "label": TEXT, "type": {"enum": NODE_TYPES}, "description": {"type": "string"},
    "status": {"enum": STATES}, "scope": TEXT, "revision": {"type": "integer", "minimum": 1},
    "created_at": STAMP, "updated_at": STAMP, "evidence": EVIDENCES, "metadata": {"type": "object"},
    "valid_from": STAMP, "valid_until": STAMP,
}, ["id", "label", "type", "description", "status", "scope", "revision", "created_at", "updated_at", "evidence", "metadata"])
EDGE = obj({
    "source": ID, "target": ID, "relation": {"enum": RELATIONS}, "evidence": EVIDENCES,
})
GRAPH_SCHEMA = obj({
    "version": {"enum": [VERSION]}, "revision": {"type": "integer", "minimum": 0},
    "updated_at": STAMP, "nodes": {"type": "object", "additionalProperties": NODE},
    "edges": {"type": "array", "items": EDGE},
})
CAPSULE_SCHEMA = obj({
    "version": {"enum": [VERSION]}, "id": ID, "timestamp": STAMP, "cli": TEXT,
    "objective": TEXT, "deliveries": STRINGS, "decisions": STRINGS,
    "modified_files": STRINGS, "preexisting_changes": STRINGS,
    "validations": {"type": "array", "items": obj({
        "command": TEXT, "result": {"enum": ["passed", "failed", "not_run"]},
        "evidence": EVIDENCES,
    })},
    "blockers": STRINGS, "pending_tasks": STRINGS, "next_action": TEXT,
    "nodes": {"type": "array", "items": NODE}, "edges": {"type": "array", "items": EDGE},
})


def check(value, schema, where="document"):
    """Validate the subset of JSON Schema used by the exported contracts."""
    kinds = {"object": dict, "array": list, "string": str, "integer": int}
    kind = schema.get("type")
    if kind and (not isinstance(value, kinds[kind]) or kind == "integer" and isinstance(value, bool)):
        raise MemoryError(f"{where}: invalid type")
    if "enum" in schema and value not in schema["enum"]:
        raise MemoryError(f"{where}: unsupported value")
    if isinstance(value, dict):
        if set(schema.get("required", [])) - value.keys():
            raise MemoryError(f"{where}: missing required fields")
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in props:
                check(item, props[key], f"{where}.{key}")
            elif extra is False:
                raise MemoryError(f"{where}: unknown fields")
            elif isinstance(extra, dict):
                check(item, extra, f"{where}.item")
    if isinstance(value, list):
        for item in value:
            check(item, schema.get("items", {}), f"{where}.item")
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            raise MemoryError(f"{where}: empty text")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            raise MemoryError(f"{where}: invalid format")
        if schema.get("format") == "date-time":
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.utcoffset() is None:
                    raise ValueError()
            except ValueError as exc:
                raise MemoryError(f"{where}: timestamp requires timezone") from exc
    if isinstance(value, int) and value < schema.get("minimum", value):
        raise MemoryError(f"{where}: below minimum")


def sanitize(value):
    fragments = []
    def collect(item):
        if isinstance(item, dict):
            for key, nested in item.items():
                if isinstance(key, str) and isinstance(nested, str):
                    fragments.append(key + ":" + nested)
                collect(key)
                collect(nested)
        elif isinstance(item, list):
            for nested in item:
                collect(nested)
        elif isinstance(item, str):
            fragments.append(item)
    collect(value)
    text = "\n".join(fragments)
    patterns = [
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"(?i)\b(?:bearer|basic)\s+[a-z0-9+/._~=-]{8,}",
        r"(?i)\b(?:authorization|proxy[-_ ]authorization)\s*[\"']?\s*[:=]\s*[\"']?\s*(?:bearer|basic)\s+[a-z0-9+/._~=-]{8,}",
        r"(?i)(?:password|passwd|pwd|senha|cookie|set[-_]?cookie|secret|client[-_]?secret|access[-_]?token|refresh[-_]?token|id[-_]?token|api[-_]?key|token)\s*[\"']?\s*[:=]\s*[\"']?[^\s\"',}]{6,}",
        r"\b(?:gh[pousr]_[a-zA-Z0-9]{20,}|github_pat_[a-zA-Z0-9_]{20,}|sk-(?:proj-)?[a-zA-Z0-9_-]{20,}|AKIA[A-Z0-9]{16}|AIza[a-zA-Z0-9_-]{20,}|xox[baprs]-[a-zA-Z0-9-]{10,})\b",
        r"\beyJ[a-zA-Z0-9_-]{12,}\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
        r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}",
    ]
    if any(re.search(pattern, text) for pattern in patterns):
        raise MemoryError("potential secret or personal data: review required")


def safe_path(root, value):
    """References stay inside the workspace and exclude sensitive areas."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise MemoryError("invalid local path")
    path = PurePosixPath(value)
    parts = tuple(part.casefold() for part in path.parts)
    sensitive = ("..", ".git", "auth", "credentials", "admin", "temp", "cache", "logs",
                 "handoff", ".codex-local", ".notebooklm", "conteudo", "raw",
                 "dados-brutos", "dados_brutos")
    if path.is_absolute() or any(part in sensitive or part.startswith(".env") for part in parts):
        raise MemoryError("unsafe evidence path")
    sensitive_suffixes = (".pem", ".key", ".pickle", ".secret", ".csv", ".tsv",
                          ".xls", ".xlsx", ".parquet", ".db", ".sqlite", ".sqlite3")
    if path.suffix.lower() in sensitive_suffixes or ":" in value:
        raise MemoryError("unsafe evidence path")
    workspace = root.resolve()
    resolved = (workspace / value).resolve()
    if not resolved.is_relative_to(workspace):
        raise MemoryError("evidence path escapes workspace")
    resolved_parts = tuple(part.casefold() for part in resolved.relative_to(workspace).parts)
    if any(part in sensitive or part.startswith(".env") for part in resolved_parts):
        raise MemoryError("unsafe evidence path")
    if resolved.suffix.lower() in sensitive_suffixes:
        raise MemoryError("unsafe evidence path")
    return resolved


def evidence(root, path):
    file = safe_path(root, path)
    if not file.is_file():
        raise MemoryError("evidence file missing")
    return {"path": path, "sha256": digest(file.read_bytes())}


def edge_key(edge):
    return (edge["source"], edge["relation"], edge["target"])


def validate_graph(graph, root):
    check(graph, GRAPH_SCHEMA)
    sanitize(graph)
    nodes = graph["nodes"]
    for key, node in nodes.items():
        if key != node["id"]:
            raise MemoryError("node key does not match id")
        for e in node["evidence"]:
            safe_path(root, e["path"])
        if node["type"] == "decision" and node["status"] == "active" and not node["evidence"]:
            raise MemoryError("active decision requires evidence")
        if node["type"] == "decision" and node["status"] == "active":
            if not isinstance(node["metadata"].get("key"), str) or "value" not in node["metadata"]:
                raise MemoryError("active decision requires structured key and value")
        for field in ("required_validations", "decision_ids"):
            if field in node["metadata"]:
                check(node["metadata"][field], {"type": "array", "items": ID}, field)
        if "valid_from" in node and "valid_until" in node:
            if datetime.fromisoformat(node["valid_from"]) >= datetime.fromisoformat(node["valid_until"]):
                raise MemoryError("empty validity interval")
    keys = set()
    for edge in graph["edges"]:
        key = edge_key(edge)
        if key in keys:
            raise MemoryError("duplicate edge")
        keys.add(key)
        if edge["source"] not in nodes or edge["target"] not in nodes:
            raise MemoryError("dangling edge")
        if edge["relation"] == "substitui":
            source, target = nodes[edge["source"]], nodes[edge["target"]]
            if source["type"] != "decision" or target["type"] != "decision" or source["scope"] != target["scope"]:
                raise MemoryError("substitution requires decisions in the same scope")
            if source["metadata"].get("key") != target["metadata"].get("key") or target["status"] != "superseded":
                raise MemoryError("substitution requires matching key and explicitly superseded target")
        for e in edge["evidence"]:
            safe_path(root, e["path"])
        if not edge["evidence"]:
            raise MemoryError("edge requires evidence")
    for relation in ("depende_de", "substitui"):
        adjacency = {k: [] for k in nodes}
        for edge in graph["edges"]:
            if edge["relation"] == relation:
                adjacency[edge["source"]].append(edge["target"])
        visiting, visited = set(), set()
        def visit(key):
            if key in visiting:
                raise MemoryError(f"cycle in {relation}")
            if key in visited:
                return
            visiting.add(key)
            for target in adjacency[key]:
                visit(target)
            visiting.remove(key)
            visited.add(key)
        for key in nodes:
            visit(key)
    return graph


def upgrade(graph, root):
    """Explicit conservative v1 conversion: legacy assertions stay legacy."""
    if graph.get("version") == VERSION:
        return validate_graph(copy.deepcopy(graph), root)
    if graph.get("version") != "1.0.0" or not isinstance(graph.get("nodes"), dict) or not isinstance(graph.get("edges"), list):
        raise MemoryError("unsupported graph version")
    result = {"version": VERSION, "revision": 0, "updated_at": graph["updated_at"], "nodes": {}, "edges": []}
    for key, old in graph["nodes"].items():
        if old.get("id") != key:
            raise MemoryError("legacy node id mismatch")
        result["nodes"][key] = {
            "id": key, "label": old["label"], "type": old["type"], "description": old.get("description", ""),
            "status": "legacy", "scope": "workspace", "revision": 1,
            "created_at": graph["updated_at"], "updated_at": graph["updated_at"],
            "evidence": [evidence(root, p) for p in old.get("evidence", [])],
            "metadata": {**old.get("metadata", {}), "migrated_from": "1.0.0"},
        }
    for old in graph["edges"]:
        result["edges"].append({**old, "evidence": [evidence(root, p) for p in old.get("evidence", [])]})
    return validate_graph(result, root)


def resolve(graph, value):
    if value in graph["nodes"]:
        return value
    matches = [key for key, node in graph["nodes"].items() if value.lower() in key.lower() or value.lower() in node["label"].lower()]
    if len(matches) != 1:
        raise MemoryError("node not found" if not matches else "ambiguous node; use exact ID: " + ", ".join(sorted(matches)))
    return matches[0]


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".memory-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.path = indexed_path(self.root, "memory_graph")
        self.memory_root = indexed_path(self.root, "memory")
        self.chat_off = indexed_path(self.root, "memory_chat_off")
        self.capsules = indexed_path(self.root, "memory_capsules")
        self.latest_state = self.chat_off / "LATEST_STATE.md"
        self.runtime = self.path.parent / ".runtime"
        for item in (self.path, self.runtime, self.latest_state, self.capsules):
            if not item.is_relative_to(self.root):
                raise MemoryError("workspace index path escapes root")

    def relative(self, item):
        return Path(item).resolve().relative_to(self.root).as_posix()

    def load(self):
        self.ensure_no_pending()
        return upgrade(decode(self.path.read_bytes()), self.root)

    def ensure_no_pending(self):
        pointer = self.runtime / "pending.json"
        if pointer.exists() and decode(pointer.read_bytes()).get("status") != "done":
            raise MemoryError("unfinished memory transaction; run recover before reading or writing")

    @contextmanager
    def locked(self):
        # Never unlink a lock file: existing waiters must lock the same inode.
        self.runtime.mkdir(parents=True, exist_ok=True)
        with (self.runtime / "write.lock").open("a+b") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def mutate(self, expected, transform, migrate=False):
        with self.locked():
            self.ensure_no_pending()
            raw = self.path.read_bytes()
            old = decode(raw)
            if old.get("version") != VERSION and not migrate:
                raise MemoryError("explicit migration required before writing")
            graph = upgrade(old, self.root)
            if graph["revision"] != expected:
                raise MemoryError("revision conflict; reload before updating")
            updated = transform(copy.deepcopy(graph))
            validate_graph(updated, self.root)
            from memory_analysis import completion_gate, sync_conflicts
            completion_gate(updated, self.root, graph)
            sync_conflicts(updated)
            validate_graph(updated, self.root)
            if updated == graph and old.get("version") == VERSION:
                return {"changed": False, "revision": graph["revision"]}
            updated["revision"] = graph["revision"] + 1
            updated["updated_at"] = now()
            backup = self.runtime / "backups" / (digest(raw) + ".json")
            if not backup.exists():
                atomic(backup, raw)
            atomic(self.path, encode(updated))
            return {"changed": True, "revision": updated["revision"], "backup": str(backup.relative_to(self.root))}


def upsert_node(graph, node):
    check(node, NODE)
    old = graph["nodes"].get(node["id"])
    if old:
        if node == old:
            return graph
        if old["type"] == "session":
            raise MemoryError("indexed session is immutable; create a new correction capsule linked by retoma")
        if old["type"] != node["type"] or old["created_at"] != node["created_at"]:
            raise MemoryError("node identity is immutable")
        if node["revision"] != old["revision"] + 1:
            raise MemoryError("node revision must increase by one")
    elif node["revision"] != 1:
        raise MemoryError("new node revision must be one")
    graph["nodes"][node["id"]] = node
    return graph


def upsert_edge(graph, edge):
    check(edge, EDGE)
    graph["edges"] = [e for e in graph["edges"] if edge_key(e) != edge_key(edge)] + [edge]
    graph["edges"].sort(key=edge_key)
    return graph


CAPSULE_PREFIX = "# Memory capsule v2\n\n```json\n"
CAPSULE_PREFIX_LEGACY = "# CTM capsule v2\n\n```json\n"
CAPSULE_SUFFIX = "```\n"


def capsule_bytes(capsule):
    return CAPSULE_PREFIX.encode() + encode(capsule) + CAPSULE_SUFFIX.encode()


def validate_capsule(capsule, root):
    check(capsule, CAPSULE_SCHEMA)
    sanitize(capsule)
    ids = [n["id"] for n in capsule["nodes"]]
    if len(set(ids)) != len(ids) or capsule["id"] in ids:
        raise MemoryError("duplicate or reserved capsule node id")
    edges = [edge_key(e) for e in capsule["edges"]]
    if len(set(edges)) != len(edges):
        raise MemoryError("duplicate capsule edge")
    for path in capsule["modified_files"] + capsule["preexisting_changes"]:
        safe_path(root, path)
    for item in capsule["validations"] + capsule["nodes"] + capsule["edges"]:
        for e in item["evidence"]:
            if evidence(root, e["path"]) != e:
                raise MemoryError("capsule evidence changed; review before saving")
    for result in capsule["validations"]:
        if result["result"] == "passed" and not result["evidence"]:
            raise MemoryError("passed validation requires recorded evidence")
    for field in ("decisions", "pending_tasks", "blockers"):
        for key in capsule[field]:
            check(key, ID, field)
    return capsule


def read_capsule(root, path, fresh=True):
    file = safe_path(root, path)
    if file.parent != indexed_path(root, "memory_capsules") or file.suffix != ".md":
        raise MemoryError("capsule must be in canonical capsules directory")
    raw = file.read_bytes()
    prefix_len = None
    if raw.startswith(CAPSULE_PREFIX.encode()):
        prefix_len = len(CAPSULE_PREFIX.encode())
    elif raw.startswith(CAPSULE_PREFIX_LEGACY.encode()):
        prefix_len = len(CAPSULE_PREFIX_LEGACY.encode())
    else:
        raise MemoryError("legacy capsule: requires explicit reference-only migration")
    if not raw.endswith(CAPSULE_SUFFIX.encode()):
        raise MemoryError("capsule format error: missing closing fence")
    capsule = decode(raw[prefix_len:-len(CAPSULE_SUFFIX.encode())])
    if fresh:
        validate_capsule(capsule, root)
    else:
        check(capsule, CAPSULE_SCHEMA)
    if file.name != capsule["id"] + ".md":
        raise MemoryError("capsule filename must match id")
    return capsule, raw


def immutable(path, data):
    """Publish a complete file with link(), which refuses an existing target."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".capsule-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(tmp, path)
        except FileExistsError:
            if path.read_bytes() != data:
                raise MemoryError("immutable capsule already exists with different content") from None
            return False
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return True
    finally:
        os.unlink(tmp)


def create_capsule(store, capsule):
    validate_capsule(capsule, store.root)
    path = store.relative(store.capsules / (capsule["id"] + ".md"))
    with store.locked():
        store.ensure_no_pending()
        changed = immutable(safe_path(store.root, path), capsule_bytes(capsule))
    return {"path": path, "created": changed, "indexed": False}


def generated_node(key, kind, label, stamp, ev, metadata=None, status="active"):
    return {"id": key, "label": label, "type": kind, "description": "",
            "status": status, "scope": "workspace", "revision": 1, "created_at": stamp,
            "updated_at": stamp, "evidence": ev, "metadata": metadata or {}}


def indexed_capsule(graph, capsule, raw, path, root):
    """Only explicit structured assertions are indexed; never extract prose facts."""
    previous = graph["nodes"].get(capsule["id"])
    sha = digest(raw)
    if previous:
        if previous["type"] != "session" or previous["metadata"].get("capsule_sha256") != sha:
            raise MemoryError("capsule identity or historical hash conflict")
        return graph
    validate_capsule(capsule, root)
    ev = [{"path": path, "sha256": sha}]
    stamp, sid = capsule["timestamp"], capsule["id"]
    session = generated_node(sid, "session", capsule["objective"], stamp, ev, {
        "capsule_path": path, "capsule_sha256": sha, "cli": capsule["cli"],
        "next_action": capsule["next_action"], "pending_tasks": capsule["pending_tasks"],
        "blockers": capsule["blockers"], "decisions": capsule["decisions"],
        "deliveries": capsule["deliveries"],
    })
    upsert_node(graph, session)
    ws_target = next((nid for nid, n in graph["nodes"].items() if n.get("type") == "workspace"), None)
    if ws_target:
        upsert_edge(graph, {"source": sid, "target": ws_target, "relation": "pertence_a", "evidence": ev})
    # Generated IDs use a bounded digest; user-defined IDs can never overwrite them.
    def add(kind, suffix, label, metadata=None, status="active", record_evidence=None):
        key = kind + "-" + digest((sid + ":" + suffix).encode())[:24]
        if key in graph["nodes"]:
            raise MemoryError("generated node identity collision")
        n = generated_node(key, kind, label, stamp, record_evidence or ev, metadata, status)
        upsert_node(graph, n)
        upsert_edge(graph, {"source": sid, "target": key, "relation": "produziu", "evidence": ev})
        return key
    add("objective", "objective", capsule["objective"])
    for n in capsule["nodes"]:
        upsert_node(graph, n)
        upsert_edge(graph, {"source": sid, "target": n["id"], "relation": "produziu", "evidence": ev})
    for field, kind in (("decisions", "decision"), ("pending_tasks", "task")):
        for key in capsule[field]:
            if key not in graph["nodes"] or graph["nodes"][key]["type"] != kind:
                raise MemoryError(f"{field}: missing typed node")
            upsert_edge(graph, {"source": sid, "target": key, "relation": "registra", "evidence": ev})
    for key in capsule["blockers"]:
        if key not in graph["nodes"]:
            raise MemoryError("blocker not registered")
        upsert_edge(graph, {"source": key, "target": sid, "relation": "bloqueia", "evidence": ev})
    for file in sorted(set(capsule["modified_files"])):
        local = safe_path(root, file)
        observed = evidence(root, file) if local.is_file() else None
        add("artifact", file, file, {"path": file, "missing": observed is None},
            status="active" if observed else "needs_review", record_evidence=[observed] if observed else ev)
    for i, validation in enumerate(capsule["validations"]):
        add("validation", str(i), validation["command"],
            {"result": validation["result"], "command": validation["command"]},
            status="completed" if validation["result"] == "passed" else "needs_review",
            record_evidence=validation["evidence"] or ev)
    for edge in capsule["edges"]:
        upsert_edge(graph, edge)
    return validate_graph(graph, root)


def index_capsule(store, path, expected):
    # Read under Store.mutate's lock; recheck content on every attempt.
    def transform(graph):
        capsule, raw = read_capsule(store.root, path, fresh=False)
        return indexed_capsule(graph, capsule, raw, path, store.root)
    return store.mutate(expected, transform)
