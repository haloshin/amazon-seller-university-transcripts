#!/usr/bin/env python3
"""Build reader navigation from catalog metadata, without editing TXT or VTT."""

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPOSITORY = "https://github.com/haloshin/amazon-seller-university-transcripts"
TOPICS = {
    "start": ("入门与账户", "Getting started and accounts"),
    "listings": ("商品发布与定价", "Listings and pricing"),
    "fulfillment": ("物流与配送", "Fulfillment and shipping"),
    "ads": ("广告与促销", "Advertising and promotions"),
    "brands": ("品牌与买家体验", "Brands and customer experience"),
    "compliance": ("合规与账户健康", "Compliance and account health"),
    "global": ("全球开店", "Global selling"),
    "business": ("企业购与经营分析", "Amazon Business and business insights"),
}
STARTER_IDS = [
    "eaf6dccf-18fd-49ee-9b08-988472334a0b",
    "7656f83f-df7c-4a3f-93e6-84c7a1358cf9",
    "84fea35b-c5c6-4ae3-999b-1cea1b3a6d96",
    "a33f0b1d-5508-4db1-bd53-e24a3d9fb9b3",
    "472d8e74-3402-4871-88d2-0ebaeb3263eb",
]


def topic_link(topic, english=False):
    name = TOPICS[topic][int(english)]
    anchor = name.lower().replace(" ", "-") if english else name
    guide = "LEARNING_GUIDE.md" if english else "学习导航.md"
    return guide + "#" + quote(anchor)


def variant(course, locale):
    return next((v for v in course["variants"] if v["locale"] == locale), None)


def language_links(course):
    links = []
    for locale, label in [("zh_CN", "中文音轨"), ("en_US", "English")]:
        v = variant(course, locale)
        if v:
            links.append(f'[{label}]({v["transcript"]})')
        elif locale == 'zh_CN' and course.get('translations'):
            links.append(f'[中文译文]({course["translations"][0]["transcript"]})')
        else:
            links.append('—')
    return links


def label(course, english, duplicates):
    name = course["title"] if english else course["navigationTitleZh"]
    if course["title"] in duplicates:
        name += " · " + course["moduleId"][:8]
    return name.replace("|", "\\|")


def validate_catalog(catalog):
    ids = {c["moduleId"] for c in catalog}
    if len(ids) != len(catalog) or not set(STARTER_IDS) <= ids:
        raise ValueError("Missing/duplicate course or starter course")
    if {c.get("navigationTopic") for c in catalog} != set(TOPICS):
        raise ValueError("Unknown or empty navigation topic")
    for c in catalog:
        title = c.get("navigationTitleZh", "")
        if not title.strip() or "\n" in title or "|" in title:
            raise ValueError("Missing or invalid Chinese navigation title")
    for module in STARTER_IDS:
        c = next(c for c in catalog if c["moduleId"] == module)
        if not variant(c, "zh_CN") or not variant(c, "en_US"):
            raise ValueError("Starter course must provide both languages")


def attribution_block(prefix="", english=False):
    if english:
        return [
            f"> Compiled and maintained by [SHIN](https://github.com/haloshin) · [Original repository and updates]({SOURCE_REPOSITORY}) · [Attribution and use]({prefix}NOTICE.md)",
            "> Course source: Amazon Seller University. Please retain the source and editorial credit; do not claim SHIN's work as your own or imply official endorsement.",
            "",
        ]
    return [
        f"> [SHIN](https://github.com/haloshin) 整理校准 · [原仓库与更新]({SOURCE_REPOSITORY}) · [署名与使用说明]({prefix}NOTICE.md)",
        "> 课程来源：Amazon Seller University。分享请保留来源与整理署名，勿冒充原创或官方发布。",
        "",
    ]


def render_guide(catalog, english=False):
    duplicates = {t for t, n in Counter(c["title"] for c in catalog).items() if n > 1}
    by_id = {c["moduleId"]: c for c in catalog}
    lines = (["# Learning guide", "", "Browse all 270 courses by topic, or start with the five courses below.", "",
              "Topic groups and the suggested sequence are editorial navigation, not an official Amazon syllabus. Original course titles and transcripts are retained. All 270 courses can be read in Chinese: 185 Chinese-audio transcripts and 85 separately labeled Chinese translations from English. Translations are AI-assisted and are not official Chinese audio transcripts.", "",
              "[Home](README.en.md) · [All courses by original title](课程目录.md) · [中文导航](学习导航.md)", "", "## Start here", "",
              "| Order | Course | 中文 | English |", "| --- | --- | --- | --- |"] if english else
             ["# 学习导航", "", "270 门课程，按 8 个主题查找。第一次来，可以先读下面 5 门课。", "",
              "主题分类和推荐顺序是本项目的阅读建议。中文导航名为编辑译名，官方原标题与转写正文保留。270 门均可中文阅读：185 门为中文音轨稿，另 85 门为依据英文稿的 AI 辅助中文译文，分别标明来源。", "",
              "[返回首页](README.md) · [按官方原标题查看全部课程](课程目录.md) · [English guide](LEARNING_GUIDE.md)", "", "## 第一次来，从这里读", "",
              "| 顺序 | 课程 | 中文 | English |", "| --- | --- | --- | --- |"])
    for i, module in enumerate(STARTER_IDS, 1):
        c = by_id[module]
        lines.append("| " + " | ".join([str(i), label(c, english, duplicates), *language_links(c)]) + " |")
    fbm = next(c for c in catalog if c["title"] == "Intro to Fulfillment by Merchant (FBM)")
    fbm_path = variant(fbm, "en_US" if english else "zh_CN")["transcript"]
    lines += ["", (f"The FBA course introduces Amazon fulfillment. For seller fulfillment, see [Intro to FBM]({fbm_path}). Choose other topics according to your needs." if english else
                    f"FBA 课程介绍亚马逊配送方式；自行配送订单可接着读[卖家自配送（FBM）入门]({fbm_path})。其他内容按自己的需要选择主题。"), "",
              "## Browse by topic" if english else "## 按主题找课", "",
              "| Topic | Courses | Chinese audio | Chinese translations |" if english else "| 主题 | 课程数 | 中文音轨 | 中文译文 |",
              "| --- | ---: | ---: | ---: |"]
    for topic, names in TOPICS.items():
        group = [c for c in catalog if c["navigationTopic"] == topic]
        zh_count = sum(variant(c, "zh_CN") is not None for c in group)
        lines.append(f"| [{names[int(english)]}]({topic_link(topic, english)}) | {len(group)} | {zh_count} | {sum(bool(c.get('translations')) for c in group)} |")
    lines += ["", ("Each course appears in one primary topic. Courses sharing an original title show a short course ID to distinguish them; it is not a version number." if english else
                    "每门课按主要内容归入一个主题。同名课程附短课程编号用于区分，不表示版本先后。"), ""]
    for topic, names in TOPICS.items():
        lines += [f"## {names[int(english)]}", "",
                  "| Course | 中文 | English |" if english else "| 中文导航名 | 官方原标题 | 中文 | English |",
                  "| --- | --- | --- |" if english else "| --- | --- | --- | --- |"]
        for c in catalog:
            if c["navigationTopic"] == topic:
                cells = [label(c, english, duplicates)]
                if not english:
                    cells.append(c["title"].replace("|", "\\|"))
                lines.append("| " + " | ".join(cells + language_links(c)) + " |")
        lines += ["", "[Back to topics](#browse-by-topic)" if english else "[返回主题索引](#按主题找课)", ""]
    lines += attribution_block(english=english)
    return "\n".join(lines)


def render_course(course, current, catalog):
    english = current["locale"] == "en_US"
    prefix = "../../../"
    home = "README.en.md" if english else "README.md"
    topic = topic_link(course["navigationTopic"], english)
    other_locale = "zh_CN" if english else "en_US"
    other = variant(course, other_locale)
    nav = [f'[{"Home" if english else "首页"}]({prefix}{home})',
           f'[{"Topic guide" if english else "本主题课程"}]({prefix}{topic})',
           f'[{"All courses" if english else "全部课程"}]({prefix}课程目录.md)']
    if other:
        nav.append(f'[{"中文" if english else "English"}](../{other_locale}/transcript.md)')
    elif english and course.get('translations'):
        nav.append(f'[中文译文]({prefix}{course["translations"][0]["transcript"]})')
    text = (ROOT / current["transcript"]).with_suffix(".txt").read_text(encoding="utf-8").strip()
    header = "# " + course["title"]
    body = text if text.startswith(header + "\n") else header + "\n\n" + text
    lines = [" · ".join(nav), "", *attribution_block(prefix, english)]
    if not english:
        lines += ["中文导航名：" + course["navigationTitleZh"], ""]
    lines += [body, "", "---", ""]
    downloads = [f'[{"Plain text" if english else "TXT 全文"}](transcript.txt)',
                 f'[{"Captions" if english else "VTT 字幕"}](captions.vtt)']
    if current.get("notes"):
        downloads.append(f'[{"Reading notes" if english else "阅读说明"}](校注.md)')
    lines += [" · ".join(downloads), ""]
    group = [c for c in catalog if c["navigationTopic"] == course["navigationTopic"]]
    at = next(i for i, c in enumerate(group) if c["moduleId"] == course["moduleId"])
    adjacent = []
    for offset, zh, en in [(-1, "同主题上一篇", "Previous in topic"), (1, "同主题下一篇", "Next in topic")]:
        if 0 <= at + offset < len(group):
            c = group[at + offset]
            v = variant(c, current["locale"]) or variant(c, "en_US")
            title = c["title"] if english else c["navigationTitleZh"]
            if not english and v["locale"] != "zh_CN":
                if c.get('translations'):
                    v = c['translations'][0]
                    title += "（中文译文）"
                else:
                    title += "（英文）"
            adjacent.append(f'[{en if english else zh}：{title}]({prefix}{v["transcript"]})')
    lines += [" · ".join(adjacent), ""]
    return "\n".join(lines)


def generated_pages(catalog):
    from translations import load_translation, render_translation
    validate_catalog(catalog)
    pages = {"学习导航.md": render_guide(catalog), "LEARNING_GUIDE.md": render_guide(catalog, True)}
    for course in catalog:
        for current in course["variants"]:
            pages[current["transcript"]] = render_course(course, current, catalog)
        for entry in course.get('translations', []):
            pages[entry['transcript']] = render_translation(course, entry, load_translation(course, entry))
    return pages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated pages without writing")
    args = parser.parse_args()
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    for name, content in generated_pages(catalog).items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Navigation mismatch: {name}")
        else:
            path.write_text(content, encoding="utf-8")
    print("Navigation pages checked" if args.check else "Navigation pages built; TXT and VTT unchanged")
