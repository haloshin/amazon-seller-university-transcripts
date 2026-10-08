#!/usr/bin/env python3
"""Stage public reading assets for GitHub Pages, outside the repository."""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
output = args.output.resolve()
if output == ROOT or output.is_relative_to(ROOT):
    parser.error('Output must be outside the repository')
if output.exists() and any(output.iterdir()):
    parser.error('Output must be empty; existing files are never removed')
output.mkdir(parents=True, exist_ok=True)
manifest = json.loads((ROOT / 'manifest.json').read_text())
count = total = 0
for entry in manifest['files']:
    name = entry['path']
    if name.startswith('.') or name.startswith('scripts/'):
        continue
    source = (ROOT / name).resolve()
    if not source.is_relative_to(ROOT) or not source.is_file():
        parser.error('Unexpected manifest path')
    dest = output / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    count += 1
    total += dest.stat().st_size
print(json.dumps({'stagedFiles': count, 'bytes': total}))
