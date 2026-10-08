"""Published platform registry. Paths are confined to this repository."""
import json
import re
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]

def platforms(repo=REPO):
    repo = Path(repo).resolve()
    registry = json.loads((repo / 'platforms.json').read_text())
    result = {}
    directories = set()
    for entry in registry['platforms']:
        key, directory = entry['id'], entry['directory']
        assert re.fullmatch(r'[a-z][a-z0-9-]*', key) and key not in result, 'Invalid/duplicate platform'
        assert re.fullmatch(r'[a-z][a-z0-9-]*', directory), 'Platform must have its own top-level directory'
        root = (repo / directory).resolve()
        assert root.is_relative_to(repo) and root != repo and root not in directories
        config = json.loads((root / 'platform.json').read_text())
        assert config['id'] == key and config['topics'] and config['sourceName']
        assert config['officialHome'].startswith('https://')
        catalog = json.loads((root / 'catalog.json').read_text())
        ids = {c['moduleId'] for c in catalog}
        assert len(ids) == len(catalog) > 0 and set(config['starters']) <= ids
        assert {c['navigationTopic'] for c in catalog} == set(config['topics'])
        result[key] = dict(config, directory=directory, root=root)
        directories.add(root)
    assert registry['defaultPlatform'] in result, 'Unknown default platform'
    return registry, result
