#!/usr/bin/env python3
"""Check that rendered pages contain no broken local file or fragment links."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / '_site'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])


pages = {}
for path in ROOT.rglob('*.html'):
    parser = Links()
    parser.feed(path.read_text())
    pages[path.resolve()] = parser
errors = []
for page, parser in pages.items():
    for link in parser.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = ROOT / unquote(url.path.lstrip('/')) if url.path.startswith('/') else page.parent / unquote(url.path)
        if not url.path:
            target = page
        elif target.is_dir() or url.path.endswith('/'):
            target = target / 'index.html'
        target = target.resolve()
        if not target.exists():
            errors.append(f'{page.relative_to(ROOT)}: missing {link}')
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'{page.relative_to(ROOT)}: missing fragment {link}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Rendered local links pass: {len(pages)} HTML pages.')
