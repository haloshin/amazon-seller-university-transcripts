#!/usr/bin/env python3
"""Compile the online/offline reader from the published, unchanged transcripts."""
import argparse
import json
from pathlib import Path
from build_navigation import ROOT, TOPICS, STARTER_IDS
from reading_paragraphs import reading_paragraphs
from translations import load_translation


def reader_data():
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    courses = []
    for course in catalog:
        item = {k: course[k] for k in ('moduleId', 'title', 'navigationTitleZh', 'navigationTopic')}
        item['variants'] = []
        for variant in course['variants']:
            directory = (ROOT / variant['transcript']).parent
            metadata = json.loads((directory / 'course.json').read_text())
            text = (directory / 'transcript.txt').read_text(encoding='utf-8')
            item['variants'].append({
                'locale': variant['locale'],
                'kind': 'transcript',
                'text': text,
                'paragraphs': reading_paragraphs(course['moduleId'], variant['locale'], text, course['title']),
                'path': directory.relative_to(ROOT).as_posix(),
                'notes': (ROOT / variant['notes']).read_text(encoding='utf-8') if variant.get('notes') else '',
                'duration': metadata['sourceVideoDurationSeconds'],
                'source': metadata['officialLearningEntry'],
            })
        for translation in course.get('translations', []):
            translated = load_translation(course, translation)
            source = next(v for v in item['variants'] if v['locale'] == translated['sourceLocale'])
            text = (ROOT / translation['text']).read_text()
            item['variants'].insert(0, {
                'locale': 'zh_CN_translation', 'kind': 'translation',
                'title': translated['title'], 'sourceLocale': translated['sourceLocale'],
                'text': text,
                'paragraphs': reading_paragraphs(course['moduleId'], 'zh_CN', text, translated['title']),
                'path': str(Path(translation['text']).parent),
                'notes': source['notes'], 'duration': source['duration'], 'source': source['source'],
            })
        courses.append(item)
    return {'release': json.loads((ROOT / 'release.json').read_text()),
            'topics': TOPICS, 'starters': STARTER_IDS, 'courses': courses,
            'notice': (ROOT / 'NOTICE.md').read_text(), 'license': (ROOT / 'LICENSE').read_text()}


def render():
    template = (ROOT / 'scripts/reader/template.html').read_text()
    data = json.dumps(reader_data(), ensure_ascii=False, separators=(',', ':'))
    # JSON lives in a non-executing script element. Escape HTML delimiters even
    # when a future transcript contains markup, preventing premature closure.
    data = data.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    replacements = {'@@DATA@@': data, '@@CSS@@': (ROOT / 'scripts/reader/style.css').read_text(),
                    '@@JS@@': (ROOT / 'scripts/reader/app.js').read_text()}
    for marker, value in replacements.items():
        assert template.count(marker) == 1, marker
        template = template.replace(marker, value)
    return template


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = ROOT / 'index.html'
    html = render()
    if args.check:
        if not output.is_file() or output.read_text() != html:
            parser.exit(1, 'Reader differs from source; run scripts/build_reader.py\n')
    else:
        output.write_text(html, encoding='utf-8')
    print(json.dumps({'reader': 'PASS', 'bytes': len(html.encode()), 'mode': 'check' if args.check else 'build'}))
