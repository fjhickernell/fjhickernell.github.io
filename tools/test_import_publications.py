"""Regression checks for meaningful bibliography import risks."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import import_publications as importer

FIXTURE = r'''
@string{art = {\Ignore{a}Refereed Journal Articles}}
@string{prep = {\Ignore{z}Manuscripts in Preparation}}
@string{sub = {\Ignore{u}Manuscripts Under Review}}
@proceedings{parent, title={Conference volume}, editor={Other, A.}, year={2024}, publisher={Publisher}}
@inproceedings{chapter, author={F. J. \HickernellFJ and {\relax Ll}. A. {Jim\'enez Rugama}}, title={Known chapter}, crossref={parent}, bdsk-file-1={PRIVATE-ATTACHMENT}, note={PRIVATE-NOTE}}
@article{private, author={F. J. \HickernellFJ}, title={PRIVATE-DRAFT}, year={2025}, pubtype=prep}
@misc{publicpreprint, author={F. J. \HickernellFJ}, title={Public preprint}, year={2025+}, howpublished={arXiv preprint 2501.12345}}
@misc{unreleased, author={F. J. \HickernellFJ}, title={PRIVATE-REVIEW}, year={2020}, pubtype=sub}
@article{forthcoming, author={F. J. \HickernellFJ}, title={Accepted paper}, year={2026}, pubtype=art, note={To appear}, doi={10.1234/chapter\_one}}
@article{unknownyear, author={F. J. \HickernellFJ}, title={Needs metadata}, pubtype=art}
'''


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / 'data').mkdir()
        (self.root / 'data/publication-topics.json').write_text('{"chapter": ["Sampling"]}')
        self.source = self.root / 'fixture.bib'
        self.source.write_text(FIXTURE)
        self.original_root = importer.ROOT
        importer.ROOT = self.root

    def tearDown(self):
        importer.ROOT = self.original_root
        self.temporary.cleanup()

    def perform_import(self):
        with contextlib.redirect_stdout(io.StringIO()):
            importer.import_catalog(self.source)
        return {record['id']: record for record in json.loads((self.root / 'data/publications.json').read_text())}

    def test_macros_crossrefs_topics_and_public_fields(self):
        before = self.source.read_bytes()
        records = self.perform_import()
        self.assertEqual(set(records), {'chapter', 'publicpreprint', 'forthcoming'})
        chapter = records['chapter']
        self.assertEqual(chapter['author'][0]['family'], 'Hickernell')
        self.assertIn('Jiménez', chapter['author'][1]['family'])
        self.assertEqual(chapter['year'], 2024)
        self.assertEqual(chapter['container-title'], 'Conference volume')
        self.assertEqual(chapter['topics'], ['Sampling'])
        exported = (self.root / 'data/publications.bib').read_text()
        self.assertNotIn('PRIVATE', exported)
        self.assertNotIn('bdsk-', exported)
        self.assertEqual(self.source.read_bytes(), before)

    def test_preprint_and_forthcoming_are_not_published(self):
        records = self.perform_import()
        self.assertEqual(records['publicpreprint']['status'], 'Public preprint')
        self.assertEqual(records['publicpreprint']['year_label'], '2025+')
        self.assertEqual(records['publicpreprint']['URL'], 'https://arxiv.org/abs/2501.12345')
        self.assertEqual(records['forthcoming']['status'], 'Forthcoming')
        self.assertEqual(records['forthcoming']['DOI'], '10.1234/chapter_one')

    def test_duplicate_bibtex_keys_stop_import(self):
        self.source.write_text(FIXTURE + '\n@article{chapter, author={F. J. Hickernell}, title={Duplicate}, year={2024}}')
        with self.assertRaisesRegex(ValueError, 'Duplicate BibTeX IDs'):
            self.perform_import()
        self.assertFalse((self.root / 'data/publications.json').exists())

    def test_editorial_exclusions_survive_refresh_without_removing_papers_or_software(self):
        exclusion_file = self.root / 'data/publication-exclusions.json'
        exclusion_file.write_text('{"notebook": "Talk notebook"}')
        self.source.write_text(FIXTURE + r'''
@misc{notebook, author={F. J. Hickernell}, title={Talk computations}, year={2024}, url={https://example.org/demo.ipynb}}
@presentation{talk, author={F. J. Hickernell}, title={A conference talk}, year={2024}, url={https://example.org/talk}}
@article{paper, author={F. J. Hickernell}, title={Using notebooks in numerical research}, year={2024}, journal={Research Journal}, doi={10.1234/paper}}
@misc{software, author={F. J. Hickernell}, title={Software release}, year={2024}, pubtype={Computer Software}, doi={10.1234/software}}
''')
        exclusions_before = exclusion_file.read_bytes()
        topics_before = (self.root / 'data/publication-topics.json').read_bytes()
        for _ in range(2):
            records = self.perform_import()
            self.assertNotIn('notebook', records)
            self.assertNotIn('talk', records)
            self.assertIn('paper', records)
            self.assertEqual(records['software']['category'], 'Software')
            self.assertEqual(records['chapter']['topics'], ['Sampling'])
        self.assertEqual(exclusion_file.read_bytes(), exclusions_before)
        self.assertEqual((self.root / 'data/publication-topics.json').read_bytes(), topics_before)

    def test_arxiv_only_article_is_labeled_as_preprint(self):
        self.source.write_text(FIXTURE + r'''
@article{report, author={F. J. Hickernell}, title={Software technical report}, year={2024}, journal={arXiv:2401.12345}}
''')
        records = self.perform_import()
        self.assertEqual(records['report']['status'], 'Public preprint')
        self.assertEqual(records['report']['URL'], 'https://arxiv.org/abs/2401.12345')


if __name__ == '__main__':
    unittest.main()
