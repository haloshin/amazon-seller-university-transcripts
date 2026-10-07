#!/usr/bin/env python3
"""Verify local release structure and integrity; no network or semantic review.

--refresh updates transcript/caption hashes and the file manifest after edits.
It never edits course text or grants content rights.
"""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
COURSE_FILES = {
    "transcript.md", "transcript.txt", "captions.vtt", "course.json",
}
IGNORED = {".git", "__pycache__", ".venv", ".DS_Store"}
MEDIA = {".mp4", ".mp3", ".wav", ".m4a", ".mov", ".pdf", ".zip"}
TIMING = re.compile(r"^(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text):
    return re.sub(r"\s+", "", text)


def seconds(stamp):
    hours, minutes, secs = stamp.split(":")
    require(int(minutes) < 60 and float(secs) < 60, "Invalid VTT timestamp")
    return int(hours) * 3600 + int(minutes) * 60 + float(secs)


def validate_captions(path, text, duration):
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip())
    require(blocks[0] == "WEBVTT", f"Invalid VTT header: {path.relative_to(ROOT)}")
    previous_end = 0
    words = []
    for block in blocks[1:]:
        lines = block.splitlines()
        timing = TIMING.fullmatch(lines[0])
        require(timing and len(lines) > 1, f"Invalid VTT cue: {path.relative_to(ROOT)}")
        start, end = map(seconds, timing.groups())
        require(previous_end <= start < end <= duration + 0.001,
                f"VTT bounds/overlap: {path.relative_to(ROOT)}")
        previous_end = end
        words.extend(lines[1:])
    require(words and compact("".join(words)) == compact(text),
            f"VTT text differs from TXT: {path.relative_to(ROOT)}")


def public_files():
    paths = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in IGNORED for part in relative.parts):
            continue
        require(not path.is_symlink(), f"Symlink is not allowed: {relative}")
        if not path.is_file() or relative.as_posix() == "manifest.json":
            continue
        require(path.suffix.lower() not in MEDIA, f"Unexpected media/archive: {relative}")
        require(not path.name.startswith(".env"), f"Environment file is not allowed: {relative}")
        paths.append(path)
    return sorted(paths)


def validate_links_and_privacy(paths):
    forbidden = [
        r"/(?:Users|Volumes|home)/[^\s]+", r"file://", r"https?://(?:localhost|127\.0\.0\.1)",
        r"https?://[^\s)]*\.cloudfront\.net", r"五批", r"幸哥",
        r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{40,}",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    ]
    for path in paths:
        if path.suffix.lower() == ".png":
            data = path.read_bytes()
            require(data.startswith(b"\x89PNG\r\n\x1a\n") and b"IEND" in data[-12:],
                    f"Invalid PNG: {path.relative_to(ROOT)}")
            continue
        content = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        # Detection expressions in this script are not publication content.
        if relative.parts[0] != "scripts":
            for pattern in forbidden:
                require(not re.search(pattern, content), f"Privacy/source-link check failed: {relative}")
        if path.suffix != ".md":
            continue
        for target in re.findall(r"\]\(([^\s)]+)\)", content):
            url = urlsplit(target.strip("<>"))
            if url.scheme or url.netloc or not url.path:
                continue
            destination = (path.parent / unquote(url.path)).resolve()
            require(destination.is_relative_to(ROOT) and destination.exists(),
                    f"Broken/local-external link in {relative}: {target}")


def verify(refresh=False):
    catalog = read_json(ROOT / "catalog.json")
    release = read_json(ROOT / "release.json")
    require(len({c["moduleId"] for c in catalog}) == len(catalog) == release["courseCount"],
            "Course count or duplicate module mismatch")
    seen_assets, expected_paths, locales = set(), set(), Counter()
    note_assets = unresolved_assets = 0
    pending_metadata = []
    for course in catalog:
        seen_locales = set()
        for variant in course["variants"]:
            locale, asset = variant["locale"], variant["assetId"]
            require(locale not in seen_locales and asset not in seen_assets, "Duplicate variant/asset")
            seen_locales.add(locale)
            seen_assets.add(asset)
            locales[locale] += 1
            directory = ROOT / "courses" / course["moduleId"] / locale
            for name in COURSE_FILES:
                path = directory / name
                require(path.is_file(), f"Missing course file: {path.relative_to(ROOT)}")
                expected_paths.add(path)
            for key, name in [("transcript", "transcript.md"), ("subtitles", "captions.vtt")]:
                require(variant[key] == (directory / name).relative_to(ROOT).as_posix(), "Catalog path mismatch")
            metadata_path = directory / "course.json"
            metadata = read_json(metadata_path)
            for key, value in [("moduleId", course["moduleId"]), ("title", course["title"]), ("locale", locale), ("assetId", asset)]:
                require(metadata[key] == value, f"Metadata {key} mismatch: {asset}")
            if metadata["editorialNoteCount"]:
                note_path = directory / "校注.md"
                require(note_path.is_file(), f"Missing reading notes: {asset}")
                require(variant.get("notes") == note_path.relative_to(ROOT).as_posix(), f"Notes path mismatch: {asset}")
                expected_paths.add(note_path)
            else:
                require(not variant.get("notes"), f"Unexpected notes link: {asset}")
            require(not metadata["unresolvedCount"] or metadata["editorialNoteCount"], f"Uncertain wording needs a reading note: {asset}")
            require(metadata["unresolvedCount"] == variant["unresolvedCount"], f"Unresolved catalog mismatch: {asset}")
            require(metadata["releaseVersion"] == release["version"], f"Version mismatch: {asset}")
            text = (directory / "transcript.txt").read_text(encoding="utf-8").strip()
            markdown = (directory / "transcript.md").read_text(encoding="utf-8")
            require(text and text in markdown, f"Markdown/TXT mismatch: {asset}")
            validate_captions(directory / "captions.vtt", text, metadata["sourceVideoDurationSeconds"])
            for field, name in [("transcriptSha256", "transcript.txt"), ("captionSha256", "captions.vtt")]:
                actual_hash = sha(directory / name)
                if refresh:
                    metadata[field] = actual_hash
                require(metadata[field] == actual_hash, f"Hash mismatch: {asset}/{name}")
            pending_metadata.append((metadata_path, metadata))
            note_assets += metadata["editorialNoteCount"] > 0
            unresolved_assets += metadata["unresolvedCount"] > 0
    actual_paths = {p for p in (ROOT / "courses").rglob("*") if p.is_file()}
    require(actual_paths == expected_paths, "Unregistered course files")
    require(len(seen_assets) == release["transcriptCount"], "Transcript count mismatch")
    require(dict(locales) == release["locales"], "Language counts mismatch")
    require(note_assets == release["editorialNotesAssets"], "Editorial note count mismatch")
    require(unresolved_assets == release["unresolvedAssets"], "Unresolved asset count mismatch")
    paths = public_files()
    validate_links_and_privacy(paths)
    if refresh:
        for path, metadata in pending_metadata:
            write_json(path, metadata)
    manifest = {
        "version": release["version"],
        "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in paths],
    }
    if refresh:
        write_json(ROOT / "manifest.json", manifest)
    require(read_json(ROOT / "manifest.json") == manifest, "Manifest mismatch; inspect edits, then run --refresh")
    return {"result": "PASS", "courses": len(catalog), "transcripts": len(seen_assets), "locales": dict(locales), "unresolvedAssets": unresolved_assets, "files": len(paths) + 1, "scope": "local structure, text consistency and file integrity"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Update metadata hashes and manifest after reviewed edits")
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.refresh), ensure_ascii=False))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")
