#!/usr/bin/env python3
"""Compile the online/offline reader from the published, unchanged transcripts."""
import argparse
import json
from pathlib import Path
from platforms import REPO, platforms
from reading_paragraphs import reading_paragraphs
from translations import load_translation




def reader_data(platform_id=None, repo=REPO):
    repo = Path(repo).resolve()
    registry, configs = platforms(repo)
    config = configs[platform_id or registry['defaultPlatform']]
    ROOT = config['root']
    links_path = ROOT / 'official-links.json'
    links = json.loads(links_path.read_text())['courses'] if links_path.exists() else {}
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
                'path': directory.relative_to(repo).as_posix(),
                'notes': (ROOT / variant['notes']).read_text(encoding='utf-8') if variant.get('notes') else '',
                'duration': metadata['sourceVideoDurationSeconds'],
                'source': links.get(course['moduleId'], {}).get('variants', {}).get(variant['locale'], {}).get('url', config['officialHome']),
                'sourceStatus': links.get(course['moduleId'], {}).get('variants', {}).get(variant['locale'], {}).get('status', 'general_portal'),
                'sourceAlternative': links.get(course['moduleId'], {}).get('variants', {}).get(variant['locale'], {}).get('alternative'),
            })
        for translation in course.get('translations', []):
            translated = load_translation(course, translation, ROOT)
            source = next(v for v in item['variants'] if v['locale'] == translated['sourceLocale'])
            text = (ROOT / translation['text']).read_text()
            item['variants'].insert(0, {
                'locale': 'zh_CN_translation', 'kind': 'translation',
                'title': translated['title'], 'sourceLocale': translated['sourceLocale'],
                'text': text,
                'paragraphs': reading_paragraphs(course['moduleId'], 'zh_CN', text, translated['title']),
                'path': (Path(config['directory']) / translation['text']).parent.as_posix(),
                'notes': source['notes'], 'duration': source['duration'], 'source': source['source'], 'sourceStatus': source['sourceStatus'], 'sourceAlternative': source.get('sourceAlternative'),
            })
        courses.append(item)
    return {'release': json.loads((ROOT / 'release.json').read_text()),
            'topics': config['topics'], 'starters': config['starters'], 'courses': courses,
            'config': {k:v for k,v in config.items() if k != 'root'},
            'stats': {'courses': len(courses), 'transcripts': sum(v['kind']=='transcript' for c in courses for v in c['variants']),
                      'translations': sum(v['kind']=='translation' for c in courses for v in c['variants']),
                      'chineseAudio': sum(any(v['locale']=='zh_CN' for v in c['variants']) for c in courses),
                      'englishAudio': sum(any(v['locale']=='en_US' for v in c['variants']) for c in courses),
                      'chineseReadable': sum(any(v['locale'].startswith('zh_CN') for v in c['variants']) for c in courses)},
            'notice': (repo / 'NOTICE.md').read_text(), 'license': (repo / 'LICENSE').read_text()}


def reader_bundle(repo=REPO):
    repo = Path(repo).resolve()
    registry, configs = platforms(repo)
    return {'version': registry['version'], 'defaultPlatform': registry['defaultPlatform'],
            'plannedPlatforms': registry.get('plannedPlatforms', []),
            'platforms': {key: reader_data(key, repo) for key in configs}}


def render():
    template = (REPO / 'scripts/reader/template.html').read_text()
    data = json.dumps(reader_bundle(), ensure_ascii=False, separators=(',', ':'))
    # JSON lives in a non-executing script element. Escape HTML delimiters even
    # when a future transcript contains markup, preventing premature closure.
    data = data.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    replacements = {'@@DATA@@': data, '@@CSS@@': (REPO / 'scripts/reader/style.css').read_text(),
                    '@@JS@@': (REPO / 'scripts/reader/app.js').read_text()}
    for marker, value in replacements.items():
        assert template.count(marker) == 1, marker
        template = template.replace(marker, value)
    return template


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = REPO / 'index.html'
    html = render()
    if args.check:
        if not output.is_file() or output.read_text() != html:
            parser.exit(1, 'Reader differs from source; run scripts/build_reader.py\n')
    else:
        output.write_text(html, encoding='utf-8')
    print(json.dumps({'reader': 'PASS', 'bytes': len(html.encode()), 'mode': 'check' if args.check else 'build'}))
