#!/usr/bin/env python3
"""Check lossless course inclusion, safe embedding and offline dependencies."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
import build_reader
import translations
from reading_paragraphs import reading_paragraphs

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "amazon"


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
    def test_all_courses_are_readable_in_chinese_without_fabricated_audio(self):
        data = build_reader.reader_data()
        catalog = {c['moduleId']: c for c in json.loads((CONTENT / 'catalog.json').read_text())}
        translated = 0
        for course in data['courses']:
            chinese = [v for v in course['variants'] if v['locale'].startswith('zh_CN')]
            self.assertEqual(len(chinese), 1)
            variant = chinese[0]
            if variant['kind'] != 'translation':
                continue
            translated += 1
            source = catalog[course['moduleId']]
            self.assertEqual([v['locale'] for v in source['variants']], ['en_US'])
            self.assertEqual(variant['locale'], 'zh_CN_translation')
            self.assertEqual(variant['sourceLocale'], 'en_US')
            self.assertFalse((ROOT / variant['path'] / 'captions.vtt').exists())
            metadata = translations.load_translation(source, source['translations'][0])
            self.assertEqual(re.sub(r'\s+', '', ''.join(variant['paragraphs'])), re.sub(r'\s+', '', ''.join(metadata['paragraphs'])))
        self.assertEqual(translated, data['release']['translationCount'])
        self.assertEqual(translated, 85)

    def test_translation_rejects_stale_source_and_missing_paragraph(self):
        course = next(c for c in json.loads((CONTENT / 'catalog.json').read_text()) if c.get('translations'))
        entry = course['translations'][0]
        original = json.loads((CONTENT / entry['metadata']).read_text())
        for changed in ({**original, 'sourceSha256': '0' * 64},
                        {**original, 'paragraphs': original['paragraphs'][:-1]},
                        {**original, 'kind': 'transcript'}):
            with self.subTest(change=changed), patch.object(translations.json, 'loads', return_value=changed):
                with self.assertRaises(AssertionError):
                    translations.load_translation(course, entry)

    def test_every_published_transcript_is_included_without_text_changes(self):
        page = ReaderHTML()
        page.feed((ROOT / 'index.html').read_text())
        data = json.loads(page.data)
        catalog = json.loads((CONTENT / 'catalog.json').read_text())
        expected = {(c['moduleId'], v['locale']): (c,v) for c in catalog for v in c['variants']}
        actual = {(c['moduleId'], v['locale']): (c,v) for c in data['courses'] for v in c['variants'] if v['kind'] == 'transcript'}
        self.assertEqual(set(expected), set(actual))
        self.assertEqual(len(actual), data['release']['transcriptCount'])
        self.assertEqual(len(data['courses']), data['release']['courseCount'])
        for key, (course, variant) in actual.items():
            ec, ev = expected[key]
            with self.subTest(course=key):
                self.assertEqual(course['title'], ec['title'])
                self.assertEqual(course['navigationTitleZh'], ec['navigationTitleZh'])
                directory = (CONTENT / ev['transcript']).parent
                self.assertEqual(variant['text'], (directory / 'transcript.txt').read_text())
                source = variant['text']
                if source.startswith('# ' + course['title'] + '\n'):
                    source = source.split('\n', 1)[1]
                normalize = (lambda s: re.sub(r'\s+', '', s)) if variant['locale'] == 'zh_CN' else (lambda s: re.sub(r'\s+', ' ', s).strip())
                self.assertEqual(normalize(' '.join(variant['paragraphs'])), normalize(source))
                self.assertEqual(variant['notes'], (CONTENT / ev['notes']).read_text() if ev.get('notes') else '')
                self.assertEqual(variant['path'], directory.relative_to(ROOT).as_posix())
                for name in ('transcript.txt','transcript.md','captions.vtt'):
                    self.assertTrue((ROOT / variant['path'] / name).is_file())
        self.assertEqual(data['notice'], (ROOT / 'NOTICE.md').read_text())
        self.assertEqual(data['license'], (ROOT / 'LICENSE').read_text())
        self.assertEqual(data['release'], json.loads((CONTENT / 'release.json').read_text()))
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

    def test_fba_benefits_keep_topic_boundaries_with_shorter_paragraphs(self):
        course = 'cfb5e67a-a4bc-4e68-b561-8d4cbd3ad167'
        source = (CONTENT / 'courses' / course / 'zh_CN/transcript.txt').read_text()
        paragraphs = reading_paragraphs(course, 'zh_CN', source, 'FBA benefits and costs')
        self.assertEqual(len(paragraphs), 6)
        self.assertTrue(paragraphs[1].endswith('从而最大限度地提高商品在亚马逊商城的曝光度和销量。'))
        self.assertTrue(any(p.startswith('新加入亚马逊物流的卖家') for p in paragraphs))
        self.assertTrue(any(p.startswith('您的亚马逊物流费用') for p in paragraphs))
        self.assertTrue(any(p.startswith('您可以通过卖家平台中的三种工具') for p in paragraphs))

    def test_dashboard_access_and_functions_have_separate_short_paragraphs(self):
        course = '1b57f3d1-0016-4f40-a7d3-6aa44d962482'
        source = (CONTENT / 'courses' / course / 'zh_CN/transcript.txt').read_text()
        paragraphs = reading_paragraphs(course, 'zh_CN', source, 'FBA dashboard overview')
        self.assertEqual(len(paragraphs), 17)
        self.assertNotIn('要找到亚马逊物流控制面板', paragraphs[0])
        self.assertTrue(paragraphs[1].startswith('要找到亚马逊物流控制面板'))
        self.assertTrue(any(p.startswith('最后一个菜单选项是分析') for p in paragraphs))
        self.assertLess(max(map(len, paragraphs)), 170)

    def test_shorter_layout_keeps_closing_quotes_with_their_sentence(self):
        source = '为了说明这项设置，我们先阅读页面上的提示。' * 3 + '页面显示：“请确认信息准确无误。”' + '然后再继续完成下一步操作。' * 5
        paragraphs = reading_paragraphs('test', 'zh_CN', source, 'Test')
        self.assertEqual(''.join(paragraphs), source)
        self.assertFalse(any(p.startswith('”') for p in paragraphs))
        self.assertGreater(len(paragraphs), 1)

    def test_explicit_paragraphs_lists_and_stage_notes_are_preserved(self):
        source = '[MUSIC PLAYING]\nRead the original\ncourse text.\n\n1. Prepare the goods.\n2. Ship the\norder.\n\nKeep the receipt.'
        paragraphs = reading_paragraphs('test', 'en_US', source, 'Test')
        self.assertEqual(paragraphs, ['[MUSIC PLAYING]', 'Read the original course text.', '1. Prepare the goods.', '2. Ship the order.', 'Keep the receipt.'])

    def test_chinese_wraps_keep_latin_word_boundaries(self):
        source = '使用 Seller\nCentral 完成操作。\n然后检查结果。'
        self.assertEqual(reading_paragraphs('test', 'zh_CN', source, 'Test'), ['使用 Seller Central 完成操作。然后检查结果。'])

    def test_changed_source_cannot_silently_reuse_curated_boundaries(self):
        with self.assertRaisesRegex(ValueError, 'need review'):
            reading_paragraphs('cfb5e67a-a4bc-4e68-b561-8d4cbd3ad167', 'zh_CN', 'Updated source.', 'FBA benefits and costs')

    def test_unpunctuated_caption_lines_do_not_become_a_wall_of_text(self):
        source = '\n'.join(['Read the original course text and keep its wording unchanged'] * 30)
        paragraphs = reading_paragraphs('test', 'en_US', source, 'Test')
        self.assertGreater(len(paragraphs), 1)
        self.assertLess(max(map(len, paragraphs)), 800)
        self.assertEqual(' '.join(paragraphs), source.replace('\n', ' '))

    def test_english_caption_wraps_are_not_used_as_sentence_boundaries(self):
        course = '472d8e74-3402-4871-88d2-0ebaeb3263eb'
        source = (CONTENT / 'courses' / course / 'en_US/transcript.txt').read_text()
        paragraphs = reading_paragraphs(course, 'en_US', source, 'Intro to Fulfillment by Amazon (FBA)')
        self.assertGreater(len(paragraphs), 1)
        for paragraph in paragraphs:
            self.assertRegex(paragraph, r'[.!?]$')
        self.assertIn('maximize exposure', ' '.join(paragraphs))


if __name__ == '__main__':
    unittest.main()
