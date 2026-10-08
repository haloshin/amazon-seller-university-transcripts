#!/usr/bin/env python3
"""Retain old GitHub Markdown bookmarks without duplicating course text."""
import argparse
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def pages():
    catalog=json.loads((ROOT/'amazon/catalog.json').read_text())
    names=['学习导航.md','LEARNING_GUIDE.md','课程目录.md','docs/SOURCES.md']
    for course in catalog:
        names += [v['transcript'] for v in course['variants']]
        names += [v['transcript'] for v in course.get('translations',[])]
        names += [v['notes'] for v in course['variants'] if v.get('notes')]
    for name in names:
        target=ROOT/'amazon'/name
        assert target.is_file()
        link=os.path.relpath(target,(ROOT/name).parent)
        yield name, f'# 内容已迁移 · Moved\n\n[打开 Amazon 专区中的正式文件 / Open the current file]({link})\n\n此页仅保留旧链接。课程正文统一保存在 `amazon/`，请更新收藏。\n'
    for folder in ('courses','translations'):
        yield folder+'/README.md',f'# 旧链接兼容目录\n\n正文已移至 [amazon/{folder}](../amazon/{folder})。本目录只保留旧 Markdown 链接的迁移提示，不保存第二套正文。\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    count=0
    for name,body in pages():
        path=ROOT/name
        if args.check: assert path.read_text()==body, name
        else: path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body)
        count+=1
    print(f'Legacy Markdown pointers: {count}')
