"""Read verified official references without distributing video media."""
import json

def link_for(root, module, locale, fallback):
    path=root/'official-links.json'
    if not path.exists(): return {'url':fallback,'status':'general_portal'}
    return json.loads(path.read_text())['courses'].get(module,{}).get('variants',{}).get(locale,{'url':fallback,'status':'general_portal'})

def markdown_link(root, module, locale, fallback, english=False):
    link=link_for(root,module,locale,fallback)
    matched=link['status']=='archive_match'
    label=('Watch this official course' if english else '观看本课原视频') if matched else ('Official learning portal' if english else '官方学习总入口')
    note=('Course ID, audio language and archived version matched; availability may change.' if english else '已核对课程 ID、音轨与归档版本；可用性可能随官方调整。') if matched else ('The archived course page could not be confirmed. Search by its original title.' if english else '暂未确认归档课程的有效页面，请按原标题查找；不将总入口视作本课视频。')
    return f"[{label}]({link['url']}) · {note}"
