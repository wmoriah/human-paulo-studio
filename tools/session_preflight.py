#!/usr/bin/env python3
"""Session Preflight — Fast System-1 heuristic engine for WM360 workspaces.

Replaces external LLM decision layers with deterministic local checks:
- Detects project cadence (daily / weekly / sporadic)
- Inspects drop zone (@inbox/) for unclassified files
- Extracts state, deliveries and pending tasks from LATEST_STATE or latest capsule
- Evaluates governance redundancy (AGENTS.md density and change status)
- Evaluates memory graph scale and need for resume
- Recommends welcome format and skips redundant file reads
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys


def discover_workspace_root(start: Path | None = None) -> Path:
    """Walk upward to find workspace root with resilient fallbacks."""
    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent

    # Try workspace_index first if available
    try:
        from workspace_index import discover_root as idx_discover
        return idx_discover(candidate)
    except Exception:
        pass

    # Fallback heuristics
    markers = [
        Path(".wm-scaffold") / "workspace-index.json",
        Path("AI-OPERATING-SYSTEM.md"),
        Path(".agents") / "AGENTS.md",
        Path("AGENTS.md"),
        Path(".memoria"),
        Path("memoria"),
        Path(".git"),
    ]
    for directory in (candidate, *candidate.parents):
        for marker in markers:
            if (directory / marker).exists():
                return directory

    return candidate


def find_memory_dir(root: Path) -> Path | None:
    for name in (".memoria", "memoria"):
        d = root / name
        if d.is_dir():
            return d
    return None


def get_inbox_status(root: Path) -> dict:
    inbox = root / "@inbox"
    if not inbox.is_dir():
        return {"exists": False, "empty": True, "count": 0, "files": []}

    ignored = {".gitkeep", ".DS_Store", "desktop.ini", "Thumbs.db"}
    files = [
        p.name for p in inbox.iterdir()
        if p.name not in ignored and not p.name.startswith(".")
    ]
    return {
        "exists": True,
        "empty": len(files) == 0,
        "count": len(files),
        "files": sorted(files),
    }


def parse_markdown_state(content: str) -> tuple[list[str], list[str], str]:
    """Parse human markdown LATEST_STATE.md into deliveries, pending, and next action."""
    deliveries: list[str] = []
    pending: list[str] = []
    next_action: str = ""

    current_sec = None
    for line in content.splitlines():
        line_clean = line.strip()
        lower = line_clean.lower()
        if line_clean.startswith("#"):
            if any(k in lower for k in ["conquista", "entrega", "finalizad", "o que foi"]):
                current_sec = "deliveries"
            elif any(k in lower for k in ["pendênc", "pendenc", "em aberto", "progresso", "bloqueio"]):
                current_sec = "pending"
            elif any(k in lower for k in ["próxima ação", "proxima acao", "próximo passo", "proximo passo", "retomar"]):
                current_sec = "next_action"
            else:
                current_sec = None
            continue

        if current_sec == "deliveries":
            if line_clean.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.")):
                item = re.sub(r"^[-*0-9.]+\s*", "", line_clean).strip()
                if item:
                    deliveries.append(item)
        elif current_sec == "pending":
            if line_clean.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.")):
                item = re.sub(r"^[-*0-9.]+\s*", "", line_clean).strip()
                if item:
                    pending.append(item)
        elif current_sec == "next_action":
            if line_clean.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.")):
                item = re.sub(r"^[-*0-9.]+\s*", "", line_clean).strip()
                if item and not next_action:
                    next_action = item
            elif line_clean and not next_action:
                next_action = line_clean

    return deliveries, pending, next_action


def get_latest_state(root: Path, memory_dir: Path | None) -> dict:
    if not memory_dir:
        return {"found": False, "deliveries": [], "pending_tasks": [], "next_action": "", "last_modified": None}

    state_file = memory_dir / "ChatOff" / "LATEST_STATE.md"
    if not state_file.is_file():
        return {"found": False, "deliveries": [], "pending_tasks": [], "next_action": "", "last_modified": None}

    mtime_dt = datetime.fromtimestamp(state_file.stat().st_mtime, tz=timezone.utc)
    raw_text = state_file.read_text(encoding="utf-8")

    # Check if this points to a structured capsule JSON (like CTM v2)
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if json_match:
        try:
            pointer = json.loads(json_match.group(1))
            session_id = pointer.get("session_id")
            if session_id:
                capsule_file = memory_dir / "ChatOff" / "capsules" / f"{session_id}.md"
                if capsule_file.is_file():
                    capsule_text = capsule_file.read_text(encoding="utf-8")
                    c_match = re.search(r"```json\s*(\{.*?\})\s*```", capsule_text, re.DOTALL)
                    if c_match:
                        c_data = json.loads(c_match.group(1))
                        return {
                            "found": True,
                            "type": "capsule_v2",
                            "session_id": session_id,
                            "deliveries": c_data.get("deliveries", []),
                            "pending_tasks": c_data.get("pending_tasks", []),
                            "next_action": c_data.get("next_action", ""),
                            "last_modified": mtime_dt.isoformat(),
                            "last_modified_dt": mtime_dt,
                        }
        except Exception:
            pass

    # Markdown format fallback (like Reports Engine)
    deliveries, pending, next_action = parse_markdown_state(raw_text)
    return {
        "found": True,
        "type": "markdown",
        "deliveries": deliveries,
        "pending_tasks": pending,
        "next_action": next_action,
        "last_modified": mtime_dt.isoformat(),
        "last_modified_dt": mtime_dt,
    }


def detect_cadence(last_dt: datetime | None, profile_override: str | None = None) -> str:
    if profile_override and profile_override in ("daily", "weekly", "sporadic"):
        return profile_override

    if not last_dt:
        return "sporadic"

    now = datetime.now(timezone.utc)
    diff = now - last_dt
    hours = diff.total_seconds() / 3600.0

    if hours <= 36.0:
        return "daily"
    elif hours <= 168.0:  # 7 days
        return "weekly"
    return "sporadic"


def check_governance(root: Path, density_override: str | None = None) -> dict:
    agents_file = root / ".agents" / "AGENTS.md"
    if not agents_file.is_file():
        agents_file = root / "AGENTS.md"

    if not agents_file.is_file():
        return {
            "agents_md_present": False,
            "density": "none",
            "redundancy_advice": "No AGENTS.md found.",
        }

    stat = agents_file.stat()
    size = stat.st_size
    content_bytes = agents_file.read_bytes()
    sha = hashlib.sha256(content_bytes).hexdigest()

    is_dense = (density_override == "high") or (size > 6000)
    density = "high" if is_dense else "low"

    if is_dense:
        advice = "AGENTS.md contains dense, domain-specific rules. Re-read only if not already loaded in context."
    else:
        advice = "AGENTS.md is standard scaffold boilerplate. If already injected into your system prompt (e.g. Antigravity/Gemini), SKIP reading."

    return {
        "agents_md_present": True,
        "path": str(agents_file.relative_to(root)),
        "size_bytes": size,
        "sha256": sha,
        "density": density,
        "redundancy_advice": advice,
    }


def check_memory_graph(memory_dir: Path | None, budget_override: str | None = None) -> dict:
    if not memory_dir:
        return {"exists": False, "nodes": 0, "edges": 0, "resume_needed": False}

    graph_file = memory_dir / "graph" / "knowledge_graph.json"
    if not graph_file.is_file():
        return {"exists": False, "nodes": 0, "edges": 0, "resume_needed": False}

    try:
        data = json.loads(graph_file.read_text(encoding="utf-8"))
        nodes = data.get("nodes", {})
        edges = data.get("edges", [])
        node_count = len(nodes) if isinstance(nodes, (dict, list)) else 0
        edge_count = len(edges) if isinstance(edges, (dict, list)) else 0
    except Exception:
        return {"exists": True, "corrupt": True, "resume_needed": False}

    if budget_override == "lean":
        resume_needed = False
    elif budget_override == "full":
        resume_needed = node_count > 2
    else:
        # Heuristic: if graph only has 1 or 2 nodes (fresh scaffold), resume is waste
        resume_needed = node_count > 2

    return {
        "exists": True,
        "nodes": node_count,
        "edges": edge_count,
        "resume_needed": resume_needed,
        "advice": "Graph has sufficient history. Run resume." if resume_needed else "Graph has minimal data (<= 2 nodes). Skip resume to save tokens.",
    }


def load_project_profile(root: Path) -> dict:
    candidates = [
        root / ".agents" / "shared" / "config" / "project-profile.json",
        root / ".wm-scaffold" / "project-profile.json",
    ]
    for c in candidates:
        if c.is_file():
            try:
                return json.loads(c.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}


def build_preflight_plan(root: Path | None = None) -> dict:
    root = discover_workspace_root(root)
    memory_dir = find_memory_dir(root)
    profile = load_project_profile(root)

    inbox = get_inbox_status(root)
    state = get_latest_state(root, memory_dir)
    last_dt = state.get("last_modified_dt")

    cadence = detect_cadence(last_dt, profile.get("cadence"))
    governance = check_governance(root, profile.get("domain_density"))
    graph = check_memory_graph(memory_dir, profile.get("memory_budget"))

    # Welcome mode determination
    welcome = profile.get("welcome")
    if not welcome:
        welcome = "pipeline" if cadence == "daily" else "menu"

    # Clean serializable state
    serializable_state = {k: v for k, v in state.items() if k != "last_modified_dt"}

    return {
        "workspace_root": str(root),
        "cadence": cadence,
        "welcome_mode": welcome,
        "inbox": inbox,
        "latest_state": serializable_state,
        "governance": governance,
        "memory_graph": graph,
        "skip_recommendations": {
            "skip_ai_operating_system": True,
            "skip_taxonomy": True,
            "skip_agents_md": governance.get("density") == "low",
            "skip_inbox_ls": True,
            "skip_memory_graph_resume": not graph.get("resume_needed", False),
        }
    }


def format_markdown_summary(plan: dict) -> str:
    cadence = plan["cadence"].upper()
    state = plan["latest_state"]
    inbox = plan["inbox"]
    gov = plan["governance"]
    graph = plan["memory_graph"]

    inbox_desc = "Limpo (0 pendências)" if inbox["empty"] else f"{inbox['count']} arquivo(s) aguardando triagem: " + ", ".join(inbox["files"])
    lines = [
        f"### ⚡ Pre-Flight WM360 (`{cadence}` mode)",
        "",
        f"- **Drop Zone (`@inbox/`):** {inbox_desc}",
    ]

    if state.get("found"):
        deliveries = state.get("deliveries", [])
        if deliveries:
            top_delivery = deliveries[0]
            lines.append(f"- **Última Sessão:** {top_delivery}")
        pending = state.get("pending_tasks", [])
        lines.append(f"- **Pendências:** {', '.join(pending) if pending else 'Nenhuma pendência crítica'}")
        next_act = state.get("next_action")
        if next_act:
            lines.append(f"- **Próxima Ação Imediata:** {next_act}")
    else:
        lines.append("- **Última Sessão:** Projeto recém-iniciado (sem histórico registrado).")

    lines.append("")
    lines.append("**Diretrizes de Economia de Tokens:**")
    skips = plan["skip_recommendations"]
    recs = []
    if skips.get("skip_agents_md"):
        recs.append("`AGENTS.md` (boilerplate já em contexto)")
    if skips.get("skip_ai_operating_system"):
        recs.append("`AI-OPERATING-SYSTEM.md` (estático)")
    if skips.get("skip_taxonomy"):
        recs.append("`taxonomy.md` (estático)")
    if skips.get("skip_memory_graph_resume"):
        recs.append("`memory_graph resume` (grafo inicial)")

    if recs:
        lines.append(f"- Pular leituras redundantes: {', '.join(recs)}.")
    lines.append(f"- Modo de recepção sugerido: `{plan['welcome_mode']}`.")

    return "\n".join(lines)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=None, help="Caminho raiz do workspace")
    cli.add_argument("--json", action="store_true", help="Imprime plano em JSON bruto (padrão)")
    cli.add_argument("--markdown", action="store_true", help="Imprime sumário em Markdown formatado")
    args = cli.parse_args()

    plan = build_preflight_plan(args.root)

    if args.markdown:
        print(format_markdown_summary(plan))
    else:
        print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
