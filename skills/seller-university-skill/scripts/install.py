#!/usr/bin/env python3
"""Install this Skill by copying it. Default: preview only, no files changed."""
import argparse
import shutil
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]

def install(parent, apply=False):
    parent=parent.expanduser().absolute()
    for p in (parent,*parent.parents):
        if p.is_symlink():raise ValueError('Refusing a symlink in the target path')
    target=parent/SOURCE.name
    if target.exists() or target.is_symlink():raise ValueError('Target already exists; back it up or choose another directory')
    if parent==SOURCE or SOURCE in parent.parents:raise ValueError('Target cannot be inside this Skill')
    for p in SOURCE.rglob('*'):
        if p.is_symlink():raise ValueError('Refusing symlinks in the source package')
    if apply:
        parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(SOURCE,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
    return target

def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--agent',choices=['codex','claude']);g.add_argument('--target',type=Path,help='Skills parent directory')
    p.add_argument('--apply',action='store_true',help='Actually copy files')
    a=p.parse_args();parent=a.target if a.target else Path.home()/('.codex/skills' if a.agent=='codex' else '.claude/skills')
    try:t=install(parent,a.apply)
    except ValueError as e:p.error(str(e))
    print(('INSTALLED: ' if a.apply else 'PREVIEW (no files changed): ')+str(t))
    if a.apply:print('Start a new Agent session and ask it to use seller-university-skill.')

if __name__=='__main__':main()
