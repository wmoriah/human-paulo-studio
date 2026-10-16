#!/usr/bin/env python3
"""Read-only local capability hints; never authenticates, uploads or generates."""
import importlib.util
import json
import shutil
import sys

if __name__ == '__main__':
    print(json.dumps({
        'python': sys.version.split()[0],
        'python_supported': sys.version_info >= (3, 9),
        'pillow_available': importlib.util.find_spec('PIL') is not None,
        'cli_paths': {name: shutil.which(name) for name in ('codex', 'claude', 'higgsfield', 'magnific')},
        'connection_status': 'unknown: verify with an authenticated read',
        'native_generation': 'unknown: inspect tools exposed in the active chat',
        'models': 'unknown: inspect the selected provider catalog'
    }, ensure_ascii=False, indent=2))
