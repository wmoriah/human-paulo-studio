#!/usr/bin/env python3
"""Package only reusable skill files, never sessions, outputs or user photos."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from install import NAME, payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent
    manifest = payload(source)
    for name in ('COMECE-AQUI.md', 'AGENTS.md', 'CLAUDE.md'):
        path = source / name
        if path.is_symlink():
            raise ValueError('Symlinked guide is not supported.')
        manifest[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    # Only distributable source formats may enter the archive.
    allowed = {'.md', '.py', '.txt', '.yaml'}
    for rel in manifest:
        if Path(rel).suffix not in allowed:
            raise ValueError(f'Unexpected payload format: {rel}')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.out, 'x', compression=ZIP_DEFLATED) as archive:
        for rel, sha in sorted(manifest.items()):
            data = (source / rel).read_bytes()
            if hashlib.sha256(data).hexdigest() != sha:
                raise ValueError(f'Source changed while packaging: {rel}')
            archive.writestr(f'{NAME}/{rel}', data)
        archive.writestr(f'{NAME}/MANIFEST.json', json.dumps(
            {'name': NAME, 'files': manifest}, indent=2, ensure_ascii=False) + '\n')
    with ZipFile(args.out) as archive:
        for rel, sha in manifest.items():
            assert hashlib.sha256(archive.read(f'{NAME}/{rel}')).hexdigest() == sha
        assert archive.testzip() is None
    print(f'Verified {len(manifest)} source files: {args.out.resolve()}')


if __name__ == '__main__':
    main()
