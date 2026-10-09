#!/usr/bin/env python3
"""Build a deterministic standalone Skill ZIP outside the repository."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/seller-university-skill'

def build(output):
    output=output.resolve()
    if output==ROOT or ROOT in output.parents:raise ValueError('Choose an output directory outside the repository')
    output.mkdir(parents=True,exist_ok=True)
    release=json.loads((SKILL/'references/release.json').read_text())
    dest=output/f"seller-university-skill-{release['version']}.zip"
    if dest.exists():raise ValueError('Archive already exists; use a fresh output directory')
    files=[p for p in sorted(SKILL.rglob('*')) if p.is_file() and not any(x in {'__pycache__','.DS_Store'} for x in p.parts) and p.suffix!='.pyc']
    for p in SKILL.rglob('*'):
        if p.is_symlink():raise ValueError('Symlinks are not allowed')
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            info=zipfile.ZipInfo('seller-university-skill/'+p.relative_to(SKILL).as_posix(),date_time=(2026,10,9,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes())
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    (output/'SHA256SUMS.txt').write_text(f'{digest}  {dest.name}\n')
    return {'archive':dest.name,'bytes':dest.stat().st_size,'sha256':digest,'files':len(files)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try: print(json.dumps(build(a.output),ensure_ascii=False))
    except ValueError as e:p.error(str(e))
