#!/usr/bin/env python3
"""Check lossless course inclusion, safe embedding and offline dependencies."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
import build_reader

ROOT = Path(__file__).resolve().parents[1]


class ReaderHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_data = False
        self.data = ''
        self.dependencies = []
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.scripts += 1
            self.in_data = attrs.get('id') == 'reader-data'
        if tag in ('script', 'img', 'link'):
            path = attrs.get('src') or attrs.get('href')
            if path:
                self.dependencies.append(path)

    def handle_data(self, value):
        if self.in_data:
            self.data += value

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_data = False


class ReaderTests(unittest.TestCase):
    def test_every_published_transcript_is_included_without_text_changes(self):
        page = ReaderHTML()
        page.feed((ROOT / 'index.html').read_text())
        data = json.loads(page.data)
        catalog = json.loads((ROOT / 'catalog.json').read_text())
        expected = {(c['moduleId'], v['locale']): (c,v) for c in catalog for v in c['variants']}
        actual = {(c['moduleId'], v['locale']): (c,v) for c in data['courses'] for v in c['variants']}
        self.assertEqual(set(expected), set(actual))
        self.assertEqual(len(actual), data['release']['transcriptCount'])
        self.assertEqual(len(data['courses']), data['release']['courseCount'])
        for key, (course, variant) in actual.items():
            ec, ev = expected[key]
            with self.subTest(course=key):
                self.assertEqual(course['title'], ec['title'])
                self.assertEqual(course['navigationTitleZh'], ec['navigationTitleZh'])
                directory = (ROOT / ev['transcript']).parent
                self.assertEqual(variant['text'], (directory / 'transcript.txt').read_text())
                self.assertEqual(variant['notes'], (ROOT / ev['notes']).read_text() if ev.get('notes') else '')
                self.assertEqual(variant['path'], directory.relative_to(ROOT).as_posix())
                for name in ('transcript.txt','transcript.md','captions.vtt'):
                    self.assertTrue((ROOT / variant['path'] / name).is_file())
        self.assertEqual(data['notice'], (ROOT / 'NOTICE.md').read_text())
        self.assertEqual(data['license'], (ROOT / 'LICENSE').read_text())
        self.assertEqual(data['release'], json.loads((ROOT / 'release.json').read_text()))
        self.assertEqual(page.scripts, 2)

    def test_no_network_dependency_for_reader_startup(self):
        page = ReaderHTML()
        page.feed((ROOT / 'index.html').read_text())
        for path in page.dependencies:
            self.assertNotIn('://', path)
            self.assertTrue((ROOT / path).is_file(), path)
        js = (ROOT / 'scripts/reader/app.js').read_text()
        for dependency in ('fetch(', 'XMLHttpRequest', 'import(', 'serviceWorker'):
            self.assertNotIn(dependency, js)
        css = (ROOT / 'scripts/reader/style.css').read_text()
        self.assertNotIn('@import', css)
        self.assertNotIn('url(', css)

    def test_future_html_like_text_cannot_escape_the_json_element(self):
        sample = {'course': '</script><script>alert("x")</script>', 'text': '<&>中文'}
        with patch.object(build_reader, 'reader_data', return_value=sample):
            page = ReaderHTML()
            page.feed(build_reader.render())
        self.assertEqual(page.scripts, 2)
        self.assertEqual(json.loads(page.data), sample)


if __name__ == '__main__':
    unittest.main()
