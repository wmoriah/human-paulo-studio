"""Resolve canonical workspace locations from the generated workspace index."""
from __future__ import annotations

import json
from pathlib import Path

INDEX_RELATIVE_PATH = Path(".wm-scaffold/workspace-index.json")


class WorkspaceIndexError(ValueError):
    """The workspace index is absent or invalid."""


def discover_root(start: Path | None = None) -> Path:
    """Walk upward until a generated workspace index is found."""
    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / INDEX_RELATIVE_PATH).is_file():
            return directory
    raise WorkspaceIndexError("workspace index not found; run wm-scaffold init or adopt first")


def load_index(root: Path | None = None) -> dict:
    root = discover_root(root)
    try:
        index = json.loads((root / INDEX_RELATIVE_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkspaceIndexError("workspace index is unreadable") from exc
    if index.get("schema") != 1 or not isinstance(index.get("paths"), dict):
        raise WorkspaceIndexError("workspace index has an unsupported format")
    return index


def path(root: Path, name: str) -> Path:
    """Return a canonical location and reject values escaping the workspace."""
    value = load_index(root)["paths"].get(name)
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
        raise WorkspaceIndexError(f"invalid workspace path: {name}")
    resolved_root = discover_root(root)
    resolved = (resolved_root / value).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise WorkspaceIndexError(f"workspace path escapes root: {name}")
    return resolved


def relative(root: Path, name: str) -> str:
    return str(path(root, name).relative_to(discover_root(root)))
