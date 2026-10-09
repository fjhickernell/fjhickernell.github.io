#!/usr/bin/env python3
"""Validate catalog completeness, public fields, authorship, and export hygiene."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'data/publications.json').read_text())
summary = json.loads((ROOT / 'data/import-summary.json').read_text())
excluded_ids = json.loads((ROOT / 'data/publication-exclusions.json').read_text())
assert len(records) == summary['imported_records']
assert len(records) + sum(summary['exclusions'].values()) == summary['source_records']
assert len({record['id'] for record in records}) == len(records)
assert not (set(excluded_ids) & {record['id'] for record in records})
assert records == sorted(records, key=lambda record: (-record['year'], record['title'].casefold(), record['id']))
for record in records:
    assert record['title'] and isinstance(record['year'], int)
    assert any('hickernell' in person.get('family', '').lower()
               for person in record.get('author') or record.get('editor', [])), record['id']
    assert record['status'] in ('Published', 'Public preprint', 'Forthcoming')
    assert isinstance(record['topics'], list) and all(isinstance(topic, str) for topic in record['topics'])
    assert not any(key in record for key in ('note', 'annote', 'abstract', 'file', 'date-added', 'date-modified'))
    for key in ('URL',):
        if record.get(key):
            assert urlsplit(record[key]).scheme in ('http', 'https')
    assert r'\Hickernell' not in json.dumps(record)
bib = (ROOT / 'data/publications.bib').read_text()
assert len(re.findall(r'(?m)^@\w+\{', bib)) == len(records)
assert not re.search(r'bdsk-|date-added|date-modified|/Users/|file://|in preparation|Manuscripts Under Review', bib, re.I)
print(f'Catalog checks pass: {len(records)} records; exclusions accounted for.')
