#!/usr/bin/env python3
"""Install only the reusable skill payload. No credentials, network or image dependencies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

NAME = 'character-sheet-studio'


def payload(source):
    files = [source / 'SKILL.md', source / 'requirements.txt']
    for folder in ('scripts', 'references', 'agents'):
        files.extend(p for p in sorted((source / folder).rglob('*'))
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    if any(p.is_symlink() for p in files):
        raise ValueError('Symlinked payload is not supported.')
    return {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', choices=('codex', 'claude', 'both'), required=True)
    parser.add_argument('--scope', choices=('user', 'project'), default='user')
    parser.add_argument('--project', type=Path)
    parser.add_argument('--skills-root', type=Path, help='Explicit skills directory for one app only')
    args = parser.parse_args()
    if args.skills_root and args.app == 'both':
        parser.error('--skills-root requires one app')
    if args.scope == 'project' and not args.project:
        parser.error('--project is required for project scope')
    source = Path(__file__).resolve().parent.parent
    manifest = payload(source)
    base = args.project.expanduser().resolve() if args.scope == 'project' else Path.home()
    apps = ('codex', 'claude') if args.app == 'both' else (args.app,)
    targets = []
    # Check all conflicts before any install, including both-app requests.
    for app in apps:
        root = args.skills_root.expanduser().resolve() if args.skills_root else base / ('.agents' if app == 'codex' else '.claude') / 'skills'
        dest = root / NAME
        if dest.is_symlink():
            raise ValueError(f'Refusing symlink destination: {dest}')
        if dest.exists():
            if not dest.is_dir():
                raise ValueError(f'Destination is not a folder: {dest}')
            identical = all((dest / rel).is_file() and hashlib.sha256((dest / rel).read_bytes()).hexdigest() == sha
                            for rel, sha in manifest.items())
            actual = {str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()
                      and '__pycache__' not in p.parts and p.suffix != '.pyc'}
            if not identical or actual != set(manifest):
                raise ValueError(f'Different version exists; preserve it and request an explicit update: {dest}')
        targets.append((app, root, dest))
    results = []
    for app, root, dest in targets:
        if dest.exists():
            results.append({'app': app, 'path': str(dest), 'status': 'already_identical'})
            continue
        root.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='.character-sheet-install-', dir=root))
        try:
            for rel in manifest:
                target = stage / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / rel, target)
            if payload(stage) != manifest:
                raise ValueError('Copied payload failed integrity verification')
            if dest.exists():
                raise FileExistsError(dest)
            os.rename(stage, dest)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        results.append({'app': app, 'path': str(dest), 'status': 'installed_and_verified'})
    print(json.dumps({'results': results, 'note': 'Files installed; app discovery must be checked in the client.'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
