"""Protect author initials and catalog structure through Markdown conversion."""
import contextlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import render_publications as renderer


class CatalogStructure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.author_paragraphs = []
        self.author_text = None
        self.list_count = 0
        self.metadata_links = []
        self.text_content = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.stack.append((tag, attrs.get('class', '')))
        if tag in ('ol', 'ul'):
            self.list_count += 1
        if tag == 'p' and 'class' not in attrs:
            self.author_text = ''
        if tag == 'a' and ('div', 'publication-meta') in self.stack:
            self.metadata_links.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag == 'p' and self.author_text is not None:
            self.author_paragraphs.append(self.author_text)
            self.author_text = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        self.text_content.append(text)
        if self.author_text is not None:
            self.author_text += text


class RenderTests(unittest.TestCase):
    def test_initials_remain_paragraphs_and_links_share_metadata_row(self):
        records = [
            {'id': 'li', 'title': 'A transformed $L_2$ design', 'year': 2020,
             'year_label': '2020', 'category': 'Chapters & conference papers',
             'status': 'Published', 'topics': [], 'container-title': r'Conference $50^{\mathrm{th}}$ session',
             'author': [{'given': 'Y.', 'family': 'Li'}, {'given': 'F. J.', 'family': 'Hickernell'}],
             'DOI': '10.1234/design', 'URL': 'https://example.org/design'},
            {'id': 'jain', 'title': 'A numerical method', 'year': 2020,
             'year_label': '2020', 'category': 'Journal articles',
             'status': 'Published', 'topics': [],
             'author': [{'given': 'A.', 'family': 'Jain'}, {'given': 'F. J.', 'family': 'Hickernell'}]}
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'data').mkdir()
            (root / 'data/publications.json').write_text(json.dumps(records))
            (root / 'data/publication-topics.json').write_text('{}')
            with patch.object(renderer, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                renderer.render()
            # Exercise the real parser that previously turned initials into lists.
            result = subprocess.run(['quarto', 'pandoc', '--from=markdown', '--to=html'],
                                    input=(root / '_includes/publications.html').read_text(),
                                    text=True, capture_output=True, check=True)
        parsed = CatalogStructure()
        parsed.feed(result.stdout)
        self.assertEqual(result.stdout.count('<math '), 2)
        self.assertNotIn('$', ''.join(parsed.text_content))
        self.assertEqual(parsed.list_count, 0)
        self.assertEqual(parsed.author_paragraphs,
                         ['Y. Li; F. J. Hickernell', 'A. Jain; F. J. Hickernell'])
        self.assertEqual(parsed.metadata_links,
                         ['https://doi.org/10.1234/design', 'https://example.org/design'])


if __name__ == '__main__':
    unittest.main()
