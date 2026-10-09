"""Skill package regression tests: retrieval, source routes, installation and ZIP."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/seller-university-skill'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
search=load('su_search',SKILL/'scripts/find_modules.py')
installer=load('su_install',SKILL/'scripts/install.py')
builder=load('su_build',ROOT/'scripts/build_skill_release.py')

class SkillTests(unittest.TestCase):
    def test_multilingual_retrieval(self):
        cases=[('新手开店','pack-01-growth'),('How to create a listing','pack-02-listing'),('A+ 图片','pack-03-content'),('商品推广预算','pack-04-ads'),('优惠券促销','pack-05-pricing'),('FBA库存积压','pack-06-fulfillment'),('品牌注册商标','pack-07-brand'),('账户健康封号','pack-08-account-health'),('Sessions 和 Page views 有什么区别','pack-09-insights'),('customer service','pack-10-orders'),('get paid','pack-11-finance'),('sell globally','pack-12-expansion'),('two-step verification','pack-13-tools')]
        for q,pack in cases:
            with self.subTest(q=q):self.assertIn(pack,{r['pack_id'] for r in search.search(q,5)})
    def test_inventory_multitopic(self):
        for q in ['美国站 FBA 库存积压，不知道该清仓还是继续打广告，你帮我定个方案。','积压 冗余 库龄 清仓']:
            self.assertTrue({r['pack_id'] for r in search.search(q,5)} & {'pack-06-fulfillment','pack-05-pricing'})
    def test_no_match_and_platform(self):
        for q in ['','   ','zzqxx_unrelated_928','Shopify 上架','沃尔玛广告']:
            self.assertEqual(search.search(q),[])
    def test_coverage_routes_and_scope(self):
        rows=json.loads((SKILL/'references/catalog.json').read_text());courses={x['moduleId']:x for x in json.loads((ROOT/'amazon/catalog.json').read_text())}
        self.assertEqual(len(rows),356);self.assertEqual(len({r['module_id'] for r in rows}),356)
        self.assertEqual(len({r['pack_id'] for r in rows}),13)
        self.assertEqual(sum(bool(r['reader_url']) for r in rows),270)
        for r in rows:
            self.assertTrue((SKILL/r['knowledge_file']).is_file())
            content=(SKILL/r['knowledge_file']).read_text()
            self.assertEqual(content.count('**来源：'),5)
            if r['reader_url']:
                params=parse_qs(urlsplit(r['reader_url']).fragment)
                self.assertEqual(params['id'],[r['module_id']]);c=courses[r['module_id']]
                has_zh=any(v['locale']=='zh_CN' for v in c['variants'])
                self.assertEqual(params['lang'],['zh_CN' if has_zh else 'zh_CN_translation'])
            self.assertNotIn('release_batch',r);self.assertNotIn('quiz',r)
        for p in SKILL.rglob('*'):
            if p.is_file() and p.suffix in {'.md','.json'}:
                t=p.read_text()
                for unwanted in ['planned_coverage','release-05','Project synthesis','"quiz":','"self_test":']:
                    self.assertNotIn(unwanted,t,str(p))
    def test_known_editorial_fixes(self):
        p=SKILL/'references/modules'
        self.assertIn('500 个',(p/'c7bf5534-c5fb-4bc0-a6f8-549ac4b3aafc.md').read_text())
        t=(p/'155f35ac-295f-46a0-bc01-2423a9d62936.md').read_text()
        self.assertNotIn('退货地址',t);self.assertIn('回信地址',t)
    def test_official_youtube_routes(self):
        rows=json.loads((SKILL/'references/catalog.json').read_text())
        ys=[r for r in rows if r['official_link_status']=='archived_official_youtube']
        self.assertEqual(len(ys),7)
        self.assertTrue(all('youtu' in urlsplit(r['official_url']).hostname for r in ys))
    def test_install_preview_copy_collision_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent=Path(tmp).resolve()/'skills'
            target=installer.install(parent)
            self.assertFalse(parent.exists())
            installer.install(parent,True)
            for p in SKILL.rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
                    self.assertEqual(p.read_bytes(),(target/p.relative_to(SKILL)).read_bytes())
            with self.assertRaises(ValueError):installer.install(parent,True)
            link=Path(tmp).resolve()/'linked';link.symlink_to(parent,target_is_directory=True)
            with self.assertRaises(ValueError):installer.install(link,True)
            with self.assertRaises(ValueError):installer.install(SKILL/'nested',True)
    def test_reproducible_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=builder.build(Path(tmp)/'a');b=builder.build(Path(tmp)/'b')
            self.assertEqual(a['sha256'],b['sha256'])
            with zipfile.ZipFile(Path(tmp)/'a'/a['archive']) as z:
                self.assertIsNone(z.testzip())
                self.assertTrue(all(n.startswith('seller-university-skill/') for n in z.namelist()))
                self.assertFalse(any('__pycache__' in n or n.endswith(('.zip','.png','.jpg','.mp4','.pdf')) for n in z.namelist()))

if __name__=='__main__':unittest.main()
