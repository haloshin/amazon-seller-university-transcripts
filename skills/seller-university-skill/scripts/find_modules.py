#!/usr/bin/env python3
"""Read-only local course search. Python 3.10+; no network or account access."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    '库存积压': ['excess inventory', 'aged inventory', 'inventory management', '积压', '库存'],
    '积压': ['excess', 'overstock', '积压', '库存'], '清仓': ['clearance', 'promotion', '库存'],
    '冗余': ['excess', '库存'], '库龄': ['aged', '库存'], '库存': ['inventory'],
    'listing': ['list products', 'add products', 'listing'],
    '滞销': ['excess inventory', 'inventory management'],
    '补货': ['restock', 'inventory planning', 'inventory'],
    '入库': ['send to amazon', 'shipment', 'inbound'],
    '上架': ['listing', 'list products', 'add products'],
    '变体': ['variation'], '商品编码': ['product id', 'gtin'],
    'gtin': ['product id', 'gtin exemption'],
    '报错': ['error', 'suppressed', 'inactive'],
    '广告': ['advertising', 'sponsored'], '广告预算': ['budget'],
    '预算': ['budget'], '关键词': ['keyword'], '否定': ['negative'],
    '商品推广': ['sponsored products'], '品牌推广': ['sponsored brands'],
    '展示型推广': ['sponsored display', 'display ads'],
    'a+': ['a+ content'], '图片': ['image'],
    '优惠券': ['coupon'], '促销': ['deal', 'promotion', 'discount'],
    '品牌注册': ['brand registry', 'enroll your brand'],
    '商标': ['trademark'], '假货': ['counterfeit', 'transparency'],
    '侵权': ['intellectual property', 'infringement'],
    '封号': ['account health', 'deactivation'],
    '账户健康': ['account health'], '账户状况': ['account health'],
    'get paid': ['payments dashboard', 'payment'],
    'sessions': ['business reports'], 'page views': ['business reports'],
    '会话次数': ['business reports'], '页面浏览量': ['business reports'],
    '业务报告': ['business reports'], '转化率': ['conversion', 'business reports'],
    '品牌分析': ['brand analytics'], '退货': ['return'], '退款': ['refund'],
    '客服': ['customer service', 'buyer seller'],
    '回款': ['payment', 'get paid', 'disbursement'], '税务': ['tax'],
    '欧洲': ['europe'], '全球开店': ['sell globally', 'global selling'],
    '加拿大': ['canada'], '双重验证': ['two-step verification'],
    '两步验证': ['two-step verification'], '子账号': ['user permissions'],
    '新手': ['beginners', 'new seller', 'start selling'],
    '推荐报价': ['featured offer'], '购物车': ['featured offer'], 'buy box': ['featured offer'],
    '自动定价': ['automate pricing', 'automated pricing'],
}
OTHER_PLATFORMS = re.compile(r'(?<![a-z])(?:tiktok(?:\s*shop)?|shopify|walmart|tk)(?![a-z])|沃尔玛|抖音', re.I)
AMAZON_PLATFORM = re.compile(r'(?<![a-z])amazon(?![a-z])|亚马逊', re.I)


def search(query, limit=5, pack=None):
    query = query.strip().lower()
    # Mixed-platform questions may still need Amazon sources. The Agent scopes
    # the question first; a hit here never supplies another platform's policy.
    if not query or (OTHER_PLATFORMS.search(query) and not AMAZON_PLATFORM.search(query)):
        return []
    rows = json.loads((ROOT / 'references/catalog.json').read_text(encoding='utf-8'))
    if re.fullmatch(r'[a-f0-9-]{36}', query):
        return [r for r in rows if r['module_id'] == query]
    words = [w for w in re.findall(r'[a-z0-9][a-z0-9+_-]*', query) if w not in {'how','to','a','an','the','my','i','can','do','is','with','for','and','of','create','what'}]
    phrases = {a for k, values in ALIASES.items() if k in query for a in values}
    # Chinese bigrams allow queries beyond the curated vocabulary.
    bigrams = {s[i:i+2] for s in re.findall(r'[\u4e00-\u9fff]+', query) for i in range(len(s)-1)}
    bigrams -= {'怎么','么办','如何','帮我','一下','什么','我的','需要','可以','问题'}
    hits=[]
    for row in rows:
        if pack and row['pack_id'] != pack:
            continue
        title=(row['title']+' '+row['title_zh']).lower()
        body=row['search_text'].lower()
        score=sum(25 if p in title else 8 if p in body else 0 for p in phrases)
        score+=sum(8 if re.search(r'(?<!\w)'+re.escape(w)+r'(?!\w)', title) else 1 if re.search(r'(?<!\w)'+re.escape(w)+r'(?!\w)',body) else 0 for w in words)
        score+=sum(5 if p in title else 0.5 if p in body else 0 for p in bigrams)
        if query in title:score+=60
        if score>=5:
            item={k:v for k,v in row.items() if k!='search_text'}
            item['score']=score;hits.append(item)
    return sorted(hits,key=lambda x:(-x['score'],x['module_id']))[:limit]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('query');p.add_argument('--limit',type=int,default=5)
    p.add_argument('--pack');p.add_argument('--json',action='store_true')
    a=p.parse_args()
    if not 1<=a.limit<=20:p.error('--limit must be 1..20')
    hits=search(a.query,a.limit,a.pack)
    if a.json:print(json.dumps(hits,ensure_ascii=False,indent=2))
    elif not hits:print('没有匹配课程。此 Skill 仅覆盖 Amazon；可换用具体工具名、英文术语或 Module ID。')
    else:
        for r in hits:
            print(f"{r['module_id']} | {r['title_zh'] or r['title']} | {r['pack_id']}")
            print('  内容：'+r['knowledge_file'])
            print('  阅读：'+(r['reader_url'] or '暂无公开转写页'))
            print('  官方：'+r['official_url']+' ['+r['official_link_status']+']')

if __name__=='__main__':main()
