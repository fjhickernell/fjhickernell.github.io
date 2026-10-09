#!/usr/bin/env python3
"""Build a public catalog from Fred's BibTeX without changing the master file."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urlsplit

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FIELDS = {'author', 'editor', 'title', 'journal', 'booktitle', 'year',
                 'month', 'volume', 'number', 'pages', 'publisher', 'address',
                 'series', 'edition', 'doi', 'url', 'isbn', 'issn'}
CSL_FIELDS = {'id', 'type', 'title', 'author', 'editor', 'issued', 'container-title',
              'volume', 'issue', 'page', 'publisher', 'publisher-place',
              'collection-title', 'collection-number', 'edition', 'DOI', 'URL'}


def clean_tex(value):
    return value.replace(r'\HickernellFJ', 'Hickernell').replace(r'\xspace', '').replace(r'\relax', '')


def safe_url(value):
    value = value.strip().replace(r'\_', '_').replace(r'\&', '&')
    match = re.fullmatch(r'\\url\{(.*)\}', value)
    if match:
        value = match.group(1)
    parts = urlsplit(value)
    return value if parts.scheme in ('https', 'http') and parts.netloc and not parts.username else ''


def import_catalog(source):
    raw = source.read_bytes()
    parser = BibTexParser(ignore_nonstandard_types=False, interpolate_strings=True,
                         add_missing_from_crossref=True)
    database = bibtexparser.loads(clean_tex(raw.decode('utf-8')), parser=parser)
    ids = [entry['ID'] for entry in database.entries]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate BibTeX IDs; correct the source before importing.')
    entries_by_id = {entry['ID']: entry for entry in database.entries}
    topics_path = ROOT / 'data/publication-topics.json'
    topics = json.loads(topics_path.read_text()) if topics_path.exists() else {}
    exclusions_path = ROOT / 'data/publication-exclusions.json'
    excluded_ids = json.loads(exclusions_path.read_text()) if exclusions_path.exists() else {}
    exported, extra = [], {}
    exclusions = Counter()
    warnings = Counter()
    labels = {'soft': 'Software', 'art': 'Journal articles',
              'chap': 'Chapters & conference papers', 'ed': 'Edited volumes',
              'oth': 'Other publications'}
    # Expanded pubtype strings are more descriptive than the original macros.
    categories = {'Refereed Journal Articles': 'art', 'Computer Software': 'soft',
                  'Refereed and/or Invited Book Chapters and Conference Papers': 'chap',
                  'Edited Volumes': 'ed', 'Other Publications': 'oth'}
    for entry in database.entries:
        category_text = re.sub(r'\\Ignore\{[^}]*\}', '', entry.get('pubtype', '')).strip()
        note = entry.get('note', '')
        if 'Preparation' in category_text or re.search(r'in preparation', note, re.I):
            exclusions['private_preparation'] += 1
            continue
        people = entry.get('author') or entry.get('editor', '')
        if not re.search(r'\bHickernell\b', people, re.I):
            exclusions['reference_only_or_not_authored_edited'] += 1
            continue
        if not entry.get('title'):
            exclusions['missing_title'] += 1
            continue
        # Keep website editorial decisions separate from the citation source.
        # Bibliographies also cite talks, notebooks, and project resources.
        if entry['ID'] in excluded_ids or entry['ENTRYTYPE'] in ('talk', 'presentation'):
            exclusions['nonpublication_resource'] += 1
            continue
        public_text = ' '.join(entry.get(k, '') for k in ('doi', 'url', 'howpublished', 'note', 'journal'))
        arxiv = re.search(r'arxiv(?:\.org/(?:abs|pdf)/|(?:\s+preprint)?[\s:./]*)(\d{4}\.\d{4,5}(?:v\d+)?|[a-z.-]+/\d{7})', public_text, re.I)
        under_review = 'Under Review' in category_text or bool(re.search(r'submitted for publication', note, re.I))
        if under_review and not arxiv and not entry.get('doi') and not safe_url(entry.get('url', '')):
            exclusions['review_without_public_identifier'] += 1
            continue
        year_text = entry.get('year', '').strip().strip('{}')
        match = re.fullmatch(r'(\d{4})(\+)?', year_text)
        if not match or (match.group(2) and not arxiv):
            exclusions['missing_or_uncertain_year'] += 1
            continue
        year = int(match.group(1))
        if year > datetime.now().year:
            exclusions['future_year_requires_review'] += 1
            continue
        status = 'Published'
        arxiv_journal = bool(re.match(r'^arxiv\b', entry.get('journal', ''), re.I))
        if under_review or (arxiv and (entry['ENTRYTYPE'] == 'misc' or match.group(2) or arxiv_journal)):
            status = 'Public preprint'
        elif re.search(r'to appear|in press|accepted for publication', note + ' ' + entry.get('howpublished', ''), re.I):
            status = 'Forthcoming'
        if match.group(2):
            warnings['source_year_has_plus'] += 1
        category_key = categories.get(category_text)
        if not category_key:
            category_key = {'article': 'art', 'incollection': 'chap',
                            'inproceedings': 'chap', 'proceedings': 'ed',
                            'book': 'ed', 'electronic': 'soft'}.get(entry['ENTRYTYPE'], 'oth')
        fields = {key: clean_tex(value) for key, value in entry.items() if key in PUBLIC_FIELDS}
        fields['year'] = str(year)
        if entry.get('crossref') and not fields.get('booktitle') and entry['ENTRYTYPE'] in ('incollection', 'inproceedings'):
            fields['booktitle'] = entries_by_id[entry['crossref']].get('title', '')
        doi = fields.get('doi', '').replace(r'\_', '_').strip()
        doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi)
        if doi:
            if not re.match(r'^10\.\d{4,9}/\S+$', doi):
                warnings['malformed_doi_omitted'] += 1
                fields.pop('doi', None)
            else:
                fields['doi'] = doi
        url = safe_url(fields.get('url', ''))
        if not url:
            found = re.search(r'https?://[^\s{}]+', entry.get('howpublished', ''))
            url = safe_url(found.group(0)) if found else ''
        if not url and arxiv:
            url = 'https://arxiv.org/abs/' + arxiv.group(1)
        if url:
            fields['url'] = url
        else:
            fields.pop('url', None)
        fields.update(ID=entry['ID'], ENTRYTYPE=entry['ENTRYTYPE'])
        exported.append(fields)
        extra[entry['ID']] = {'year': year, 'year_label': year_text,
                              'category': labels[category_key], 'status': status,
                              'topics': topics.get(entry['ID'], [])}

    public_database = BibDatabase()
    public_database.entries = exported
    bib = bibtexparser.dumps(public_database)
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / 'public.bib'
        path.write_text(bib)
        result = subprocess.run(['quarto', 'pandoc', '--from=bibtex', '--to=csljson', str(path)],
                                check=True, text=True, capture_output=True)
        csl_records = json.loads(result.stdout)
    if len(csl_records) != len(exported):
        raise ValueError('Pandoc conversion lost records; stop before writing exports.')
    records = []
    for record in csl_records:
        item = {key: value for key, value in record.items() if key in CSL_FIELDS}
        item.update(extra[record['id']])
        if not any(re.search(r'\bHickernell\b', person.get('family', ''), re.I)
                   for person in item.get('author') or item.get('editor', [])):
            raise ValueError(f"Author/editor conversion lost Hickernell for {record['id']}")
        records.append(item)
    records.sort(key=lambda item: (-item['year'], item['title'].casefold(), item['id']))
    doi_counts = Counter(record['DOI'].lower() for record in records if record.get('DOI'))
    summary = {'source_filename': source.name, 'source_sha256': hashlib.sha256(raw).hexdigest(),
               'source_records': len(database.entries), 'imported_records': len(records),
               'exclusions': dict(sorted(exclusions.items())), 'warnings': dict(sorted(warnings.items())),
               'status_counts': dict(Counter(record['status'] for record in records)),
               'category_counts': dict(Counter(record['category'] for record in records)),
               'duplicate_doi_groups': sum(count > 1 for count in doi_counts.values()),
               'records_without_public_link': sum(not record.get('DOI') and not record.get('URL') for record in records),
               'topic_keys_not_in_public_catalog': sum(key not in extra for key in topics),
               'exclusion_keys_not_in_source': sum(key not in entries_by_id for key in excluded_ids),
               'coverage_note': 'A sanitized snapshot of the supplied bibliography, not an exhaustive or current publication claim.'}
    data = ROOT / 'data'
    data.mkdir(exist_ok=True)
    (data / 'publications.bib').write_text(bib)
    (data / 'publications.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    (data / 'import-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    args = parser.parse_args()
    import_catalog(args.source.expanduser().resolve())
