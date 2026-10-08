"""Reading-only paragraph layout; source transcripts are never edited."""
import hashlib
import json
import re
from pathlib import Path

LAYOUTS = json.loads((Path(__file__).parent / 'reader/paragraphs.json').read_text())
LIST = re.compile(r'^\s*(?:[-*•]\s+|\d+[.)、]\s*|[一二三四五六七八九十]+[、．])')
STAGE = re.compile(r'^\[[^\]\n]+\]$')
END = re.compile(r'[。！？.!?][\"\'”’）)]*\s*$')
TRANSITION_ZH = re.compile(r'^(?:下面|接下来|首先|其次|然后|最后|第一步|第二步|第三步|总之|简而言之|现在[,，]|想要了解|要了解更多)')
TRANSITION_EN = re.compile(r'^(?:Next\b|First[, :]|Second[, :]|Third[, :]|Finally\b|In summary\b|To learn more\b|Now[, :]|Let[’\']s\b)', re.I)
CONTINUATION_ZH = re.compile(r'^(?:这|该|同时|此外|而|并|因此|从而|其中|以及|包括|也|有助于)')
CONTINUATION_EN = re.compile(r'^(?:This|These|That|Those|It|They|And|Or|For example|For instance|Which|Including)\b', re.I)


def join_lines(lines, locale):
    """Remove caption wrapping without running adjacent Latin words together."""
    result = ''
    for line in lines:
        line = line.strip()
        separator = ' ' if result and (locale == 'en_US' or
            (re.search(r'[A-Za-z0-9]$', result) and re.match(r'[A-Za-z0-9]', line))) else ''
        result += separator + line
    return result


def reading_paragraphs(module_id, locale, text, title):
    lines = text.splitlines()
    if lines and lines[0] == '# ' + title:
        lines.pop(0)
    layout = LAYOUTS.get(module_id + '/' + locale)
    if layout:
        if hashlib.sha256(text.encode()).hexdigest() != layout['sha256']:
            raise ValueError('Reading paragraph boundaries need review: ' + module_id + '/' + locale)
        content = [line.strip() for line in lines if line.strip()]
        starts = layout['starts'] + [len(content)]
        assert starts[0] == 0 and all(a < b for a, b in zip(starts, starts[1:]))
        return [join_lines(content[a:b], locale) for a, b in zip(starts, starts[1:])]

    chinese = locale == 'zh_CN'
    target, minimum, maximum = (90, 30, 150) if chinese else (300, 110, 460)
    transition = TRANSITION_ZH if chinese else TRANSITION_EN
    continuation = CONTINUATION_ZH if chinese else CONTINUATION_EN
    content_lines = [line.strip() for line in lines if line.strip()]
    # Some archived audio transcripts have almost no sentence punctuation.
    # Use their existing line boundaries as a fallback; do not invent punctuation
    # or collapse a whole unpunctuated course into a single reading paragraph.
    # Caption wraps often fall mid-sentence even when the text is punctuated.
    # Inspect the full text, not just line endings, before enabling the fallback.
    sentence_marks = len(re.findall(r'[。！？]|[.!?](?=\s|$)', join_lines(content_lines, locale)))
    sparse_punctuation = len(content_lines) > 1 and sentence_marks / len(content_lines) < .12
    paragraphs, units, wrapped = [], [], []

    def flush_units():
        block = []
        for unit in units:
            current = join_lines(block, locale)
            # Split only between source sentences. Discourse cues take priority;
            # length is a fallback for sources with no paragraph information.
            if block and (END.search(current) or sparse_punctuation) and (
                (len(current) >= minimum and transition.match(unit)) or
                len(block) >= 3 or
                (len(current) >= target and not continuation.match(unit)) or
                (len(current) >= minimum and len(current) + len(unit) > maximum) or
                len(current) >= maximum
            ):
                paragraphs.append(current)
                block = []
            block.append(unit)
        if block:
            paragraphs.append(join_lines(block, locale))
        units.clear()

    def flush_wrapped():
        if wrapped:
            sentence = join_lines(wrapped, locale)
            if len(sentence) > target:
                pattern = r'(?<=[。！？])(?![”’」』）》】])' if chinese else r'(?<=[.!?])\s+(?=[A-Z“\"])'
                units.extend(part for part in re.split(pattern, sentence) if part.strip())
            else:
                units.append(sentence)
            wrapped.clear()

    in_list = False
    for raw in lines:
        line = raw.strip()
        if not line:
            flush_wrapped()
            flush_units()
            in_list = False
        elif STAGE.fullmatch(line) or LIST.match(line):
            flush_wrapped()
            flush_units()
            paragraphs.append(line)
            in_list = bool(LIST.match(line))
        elif in_list and not END.search(paragraphs[-1]):
            paragraphs[-1] = join_lines([paragraphs[-1], line], locale)
        else:
            in_list = False
            wrapped.append(line)
            if chinese or END.search(line) or sparse_punctuation:
                flush_wrapped()
    flush_wrapped()
    flush_units()
    return paragraphs
