#!/usr/bin/env python3
"""
Universal Suite Installer & Packager for Human Paulo Studio Skills.
- Installs all 6 skills into the workspace (.agents/skills/) or globally (Antigravity, Codex, Claude Code).
- Packages all 6 skills into clean, verifiable ZIP archives in output/entregaveis/ for community release.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

SKILLS = (
    "creative-pipeline-director",
    "character-sheet-studio",
    "experimental-angles-studio",
    "editorial-photoshoot-studio",
    "seedance-commercial-director",
    "cinema-vfx-supervisor",
)


def collect_skill_files(skill_dir: Path) -> dict[str, str]:
    files = []
    for p in sorted(skill_dir.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix in {".pyc", ".DS_Store"} or p.name == ".DS_Store":
            continue
        if p.name == "MANIFEST.json":
            continue
        files.append(p)
    return {str(p.relative_to(skill_dir)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def install_skills(skills_source_root: Path, target_roots: list[Path]) -> list[str]:
    installed = []
    for root in target_roots:
        root.mkdir(parents=True, exist_ok=True)
        for name in SKILLS:
            src = skills_source_root / name
            dst = root / name
            if dst.is_symlink() or dst.exists():
                if dst.is_symlink():
                    dst.unlink()
                else:
                    shutil.rmtree(dst)
            shutil.copytree(
                src,
                dst,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
            manifest = collect_skill_files(dst)
            (dst / "MANIFEST.json").write_text(
                json.dumps({"name": name, "files": manifest}, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            installed.append(str(dst))
    return installed


def package_skills(skills_source_root: Path, out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    archives = []
    bundle_zip = out_dir / "human-paulo-studio-suite-completa.zip"
    if bundle_zip.exists():
        bundle_zip.unlink()

    with ZipFile(bundle_zip, "w", compression=ZIP_DEFLATED) as master_zip:
        for name in SKILLS:
            src = skills_source_root / name
            manifest = collect_skill_files(src)
            single_zip = out_dir / f"{name}.zip"
            if single_zip.exists():
                single_zip.unlink()
            with ZipFile(single_zip, "w", compression=ZIP_DEFLATED) as sz:
                for rel, sha in sorted(manifest.items()):
                    data = (src / rel).read_bytes()
                    sz.writestr(f"{name}/{rel}", data)
                    master_zip.writestr(f"human-paulo-studio/{name}/{rel}", data)
                manifest_bytes = (
                    json.dumps({"name": name, "files": manifest}, indent=2, ensure_ascii=False) + "\n"
                ).encode("utf-8")
                sz.writestr(f"{name}/MANIFEST.json", manifest_bytes)
                master_zip.writestr(f"human-paulo-studio/{name}/MANIFEST.json", manifest_bytes)
            archives.append(str(single_zip))
    archives.append(str(bundle_zip))
    return archives


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Path to the human-paulo-studio workspace",
    )
    parser.add_argument(
        "--install-workspace",
        action="store_true",
        help="Install all 6 skills into workspace .agents/skills/",
    )
    parser.add_argument(
        "--install-global",
        action="store_true",
        help="Install all 6 skills into ~/.gemini/config/skills, ~/.codex/skills, and ~/.claude/skills",
    )
    parser.add_argument(
        "--package",
        action="store_true",
        help="Build distributable ZIP packages in output/entregaveis/",
    )
    args = parser.parse_args()

    ws = args.workspace.expanduser().resolve()
    src_root = ws / "output" / "sistema" / "skills"
    result = {"installed": [], "packaged": []}

    targets = []
    if args.install_workspace:
        targets.append(ws / ".agents" / "skills")
    if args.install_global:
        home = Path.home()
        targets.extend([
            home / ".gemini" / "config" / "skills",
            home / ".codex" / "skills",
            home / ".claude" / "skills",
        ])

    if targets:
        result["installed"] = install_skills(src_root, targets)
    if args.package:
        result["packaged"] = package_skills(src_root, ws / "output" / "entregaveis")

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
