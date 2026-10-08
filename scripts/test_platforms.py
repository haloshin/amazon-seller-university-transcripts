"""Regression tests for collection isolation and safe platform registration."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import build_reader
from platforms import platforms

ROOT=Path(__file__).resolve().parents[1]

def fixture(root):
    for name in ('NOTICE.md','LICENSE'):
        shutil.copy2(ROOT/name,root/name)
    course=next(c for c in json.loads((ROOT/'amazon/catalog.json').read_text()) if len(c['variants'])==2)
    for key in ('first','second'):
        base=root/key;base.mkdir()
        shutil.copytree(ROOT/'amazon/courses'/course['moduleId'],base/'courses'/course['moduleId'])
        c=json.loads(json.dumps(course));c['title']=key+' course';c['navigationTitleZh']=key+' 课程';c['navigationTopic']='topic'
        (base/'catalog.json').write_text(json.dumps([c]))
        for v in c['variants']:
            (base/v['transcript']).with_suffix('.txt').write_text(key+'独立全文 Unique '+key)
        (base/'release.json').write_text(json.dumps({'version':'test','archiveDate':'2026-01-01'}))
        config=json.loads((ROOT/'amazon/platform.json').read_text());config.update(id=key,name=[key,key],sourceName=key+' Academy',topics={'topic':['主题','Topic']},topicDescriptions={'topic':['描述','Description']},starters=[c['moduleId']],starterNames=[[key],[key]],starterDescriptions=[['描述'],['Description']],heroTitle=[key,key])
        (base/'platform.json').write_text(json.dumps(config))
    (root/'platforms.json').write_text(json.dumps({'version':'test','defaultPlatform':'first','platforms':[{'id':k,'directory':k} for k in ('first','second')]}))
    return course['moduleId']

class PlatformTests(unittest.TestCase):
    def test_equal_course_ids_remain_separate_and_counts_are_derived(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);mid=fixture(root);data=build_reader.reader_bundle(root)
            self.assertEqual(set(data['platforms']),{'first','second'})
            for key,collection in data['platforms'].items():
                self.assertEqual(collection['stats']['courses'],1)
                self.assertEqual(collection['stats']['transcripts'],2)
                self.assertEqual(collection['stats']['translations'],0)
                self.assertEqual(collection['courses'][0]['moduleId'],mid)
                for v in collection['courses'][0]['variants']:
                    self.assertTrue(v['path'].startswith(key+'/'))
                    self.assertIn('Unique '+key,v['text'])
                    self.assertNotIn('Unique '+('second' if key=='first' else 'first'),v['text'])
    def test_invalid_registry_paths_duplicates_and_default_fail(self):
        for mutate in ('traversal','duplicate','default'):
            with self.subTest(mutate=mutate),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);fixture(root);p=root/'platforms.json';d=json.loads(p.read_text())
                if mutate=='traversal':d['platforms'][0]['directory']='../outside'
                elif mutate=='duplicate':d['platforms'].append(d['platforms'][0])
                else:d['defaultPlatform']='unknown'
                p.write_text(json.dumps(d))
                with self.assertRaises(AssertionError):platforms(root)
    def test_unknown_platform_does_not_select_default_content(self):
        with self.assertRaises(KeyError):build_reader.reader_data('unknown')
    def test_official_links_match_every_archived_variant_or_are_explicit_fallbacks(self):
        data=build_reader.reader_data();matched=missing=0
        for course in data['courses']:
            for v in course['variants']:
                if v['kind']=='translation':
                    source=next(x for x in course['variants'] if x['locale']==v['sourceLocale'])
                    self.assertEqual(v['source'],source['source']);continue
                if v['sourceStatus']=='archive_match':
                    self.assertIn(course['moduleId'],v['source']);self.assertIn(v['locale'],v['source']);matched+=1
                else:
                    self.assertEqual(v['sourceStatus'],'official_module_unavailable');missing+=1
        self.assertEqual((matched,missing),(435,20))

if __name__=='__main__':unittest.main()
