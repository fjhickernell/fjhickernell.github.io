#!/usr/bin/env python3
"""Render a static, progressively enhanced publication index from catalog JSON."""
from collections import defaultdict
import html
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
escape = html.escape


def text_html(value):
    # Use Pandoc's MathML conversion for scientific text while escaping all
    # surrounding prose. Native browser MathML avoids displaying raw TeX.
    chunks = re.split(r'(\$[^$]+\$)', value)
    rendered = []
    for chunk in chunks:
        if chunk.startswith('$') and chunk.endswith('$'):
            converted = subprocess.run(['quarto', 'pandoc', '--from=markdown', '--to=html', '--mathml'],
                                       input=chunk, text=True, capture_output=True, check=True).stdout.strip()
            rendered.append(converted.removeprefix('<p>').removesuffix('</p>'))
        else:
            rendered.append(escape(chunk))
    return ''.join(rendered)


def names(people):
    return '; '.join(' '.join(person[key] for key in
                             ('given', 'dropping-particle', 'non-dropping-particle', 'family', 'suffix')
                             if person.get(key))
                    for person in people)


def render():
    records = json.loads((ROOT / 'data/publications.json').read_text())
    topic_overrides = json.loads((ROOT / 'data/publication-topics.json').read_text())
    for record in records:
        record['topics'] = topic_overrides.get(record['id'], record.get('topics', []))
    categories = sorted({record['category'] for record in records})
    topics = sorted({topic for record in records for topic in record['topics']})
    years = defaultdict(list)
    for record in records:
        years[record['year']].append(record)
    out = ['<div id="publication-catalog">', '<div class="catalog-controls" hidden>',
           '<div><label for="publication-search">Search publications</label><input id="publication-search" type="search" placeholder="Title, author, or journal"></div>',
           '<div><label for="publication-category">Publication type</label><select id="publication-category"><option value="">All types</option>']
    out += [f'<option>{escape(category)}</option>' for category in categories]
    out += ['</select></div>', '<div><label for="publication-year">Year</label><select id="publication-year"><option value="">All years</option>']
    out += [f'<option>{year}</option>' for year in sorted(years, reverse=True)]
    out += ['</select></div>']
    if topics:
        out += ['<div><label for="publication-topic">Topic</label><select id="publication-topic"><option value="">All topics</option>']
        out += [f'<option>{escape(topic)}</option>' for topic in topics]
        out += ['</select></div>']
    out += ['</div>', f'<p class="catalog-summary" id="catalog-summary" role="status">{len(records)} records · {min(years)}–{max(years)}</p>',
            '<p class="catalog-empty" hidden>No publications match these filters.</p>']
    for year in sorted(years, reverse=True):
        out += [f'<section class="publication-year" data-year="{year}"><h2 id="year-{year}">{year}</h2>']
        for record in years[year]:
            author_text = names(record.get('author') or record.get('editor', []))
            if not record.get('author'):
                author_text += ' (editors)'
            venue = record.get('container-title') or record.get('publisher') or ''
            details = ', '.join(str(record[key]) for key in ('volume', 'issue', 'page') if record.get(key))
            search = ' '.join([record['title'], author_text, venue, record['category'], *record['topics']]).casefold()
            out += [f'<article class="publication" id="{escape(record["id"], quote=True)}" data-category="{escape(record["category"], quote=True)}" data-year="{year}" data-topics="{escape(json.dumps(record["topics"]), quote=True)}" data-search="{escape(search, quote=True)}">',
                    f'<h3>{text_html(record["title"])}</h3>', f'<p>{escape(author_text)}</p>']
            if venue or details:
                out += [f'<p class="venue">{text_html(venue)}{", " if venue and details else ""}{text_html(details)}</p>']
            status = record['category']
            if record['status'] != 'Published':
                status += ' · ' + record['status']
            if record['year_label'] != str(year):
                status += ' · Source year: ' + record['year_label']
            if record['topics']:
                status += ' · ' + ', '.join(record['topics'])
            out += ['<div class="publication-meta">', f'<span class="status">{escape(status)}</span>']
            doi_url = 'https://doi.org/' + record['DOI'] if record.get('DOI') else ''
            if doi_url:
                out += [f'<a href="{escape(doi_url, quote=True)}">DOI</a>']
            if record.get('URL') and record['URL'] != doi_url:
                out += [f'<a href="{escape(record["URL"], quote=True)}">Online version</a>']
            out += ['</div>', '</article>']
        out += ['</section>']
    out += ['</div>']
    path = ROOT / '_includes/publications.html'
    path.parent.mkdir(exist_ok=True)
    # Quarto includes are parsed as Markdown. A literal HTML block prevents
    # initials such as "Y. Li" and "A. Jain" from becoming ordered lists.
    path.write_text('```{=html}\n' + '\n'.join(out) + '\n```\n')
    print(f'Rendered {len(records)} publication records.')


if __name__ == '__main__':
    render()
