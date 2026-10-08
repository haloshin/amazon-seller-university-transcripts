"""Load separately attributed Chinese translations without inventing audio tracks."""
import hashlib
import json
import re
from pathlib import Path
from reading_paragraphs import reading_paragraphs

from platforms import platforms
_registry, _configs = platforms()
ROOT = _configs[_registry["defaultPlatform"]]["root"]


def load_translation(course, entry, ROOT=ROOT):
    path = ROOT / entry['metadata']
    data = json.loads(path.read_text())
    source = next(v for v in course['variants'] if v['locale'] == 'en_US')
    source_path = (ROOT / source['transcript']).with_suffix('.txt')
    assert data['moduleId'] == course['moduleId'], 'Translation belongs to another course'
    assert data['kind'] == entry['kind'] == 'translation'
    assert data['locale'] == entry['locale'] == 'zh_CN'
    assert data['sourceLocale'] == entry['sourceLocale'] == 'en_US'
    assert data['sourcePath'] == source_path.relative_to(ROOT).as_posix()
    assert data['sourceSha256'] == hashlib.sha256(source_path.read_bytes()).hexdigest(), 'Translation source changed'
    assert not any(v['locale'] == 'zh_CN' for v in course['variants']), 'Chinese audio already available'
    assert entry['text'] == str(path.with_name('translation.txt').relative_to(ROOT))
    assert entry['transcript'] == str(path.with_name('translation.md').relative_to(ROOT))
    paragraphs = data['paragraphs']
    assert isinstance(paragraphs, list) and len(paragraphs) == data['sourceParagraphCount'] > 0
    assert len(paragraphs) == len(reading_paragraphs(course['moduleId'], 'en_US', source_path.read_text(), course['title'])), 'Missing source paragraph alignment'
    assert all(isinstance(p, str) and p.strip() and re.search('[\u4e00-\u9fff]', p) for p in paragraphs)
    text = '\n\n'.join(paragraphs) + '\n'
    assert (ROOT / entry['text']).read_text() == text, 'Translation TXT mismatch'
    return data


def render_translation(course, entry, data, source_name=None, root=ROOT, official_home=None):
    config=json.loads((root/'platform.json').read_text())
    source_name=source_name or config['sourceName']
    official_home=official_home or config['officialHome']
    english = next(v for v in course['variants'] if v['locale'] == 'en_US')
    prefix = '../../../'
    lines = [f'[学习导航]({prefix}学习导航.md) · [英文原文]({prefix}{english["transcript"]})', '',
             '# ' + data['title'], '', course['title'], '',
             '> 中文译文 · 依据英文转写稿，经 AI 辅助翻译与校对；非官方中文音轨转写。',
             '> 参照本库中文音轨稿统一术语，保留原课的步骤、案例和历史语境。', '',
             f'课程来源：{source_name} · SHIN 整理维护。',
             f'分享请保留来源、署名和[原仓库链接](https://github.com/haloshin/seller-university)。[使用条件]({prefix}../NOTICE.md)', '',
             *[p + '\n' for p in data['paragraphs']], '---', '',
             '[下载中文 TXT](translation.txt) · ' + f'[对照英文原文]({prefix}{english["transcript"]})', '']
    if english.get('notes'):
        lines += [f'英文原稿附有[阅读说明]({prefix}{english["notes"]})，译文保留对应的不确定性。', '']
    from official_links import markdown_link
    lines += [markdown_link(root, course['moduleId'], data['sourceLocale'], official_home), '']
    lines += ['费用、政策及界面均反映原课归档时的内容，请核对当前官方信息。', '']
    return '\n'.join(lines)


def validate_translations(catalog, release, ROOT=ROOT, source_name=None):
    expected = set()
    count = 0
    for course in catalog:
        entries = course.get('translations', [])
        needs_chinese = not any(v['locale'] == 'zh_CN' for v in course['variants'])
        assert len(entries) <= int(needs_chinese), 'Duplicate translation or Chinese audio already exists'
        for entry in entries:
            data = load_translation(course, entry, ROOT)
            assert data['releaseVersion'] == release['version'], 'Translation version mismatch'
            assert (ROOT / entry['transcript']).read_text() == render_translation(course, entry, data, source_name, ROOT)
            expected.update(ROOT / entry[key] for key in ('transcript', 'text', 'metadata'))
            count += 1
    actual = {p for p in (ROOT / 'translations').rglob('*') if p.is_file()}
    assert actual == expected, 'Unregistered translation files'
    assert count == release['translationCount'] == release['translationLocales']['zh_CN']
    assert release['chineseReadableCourses'] == sum(bool(c.get('translations')) or any(v['locale']=='zh_CN' for v in c['variants']) for c in catalog)
    return count
