# Fred J. Hickernell — Personal Website

Quarto source for https://fjhickernell.github.io. The root site is the curated
professional home; individual course, talk, software, and library repositories
retain their detailed content and independent publishing workflows.

## Local development

Initialize the recorded shared library, then render or preview:

```bash
git submodule update --init --recursive
python3 classlib/tools/bootstrap_consumer.py check .
python3 tools/render_publications.py
quarto render
quarto preview --no-browser
```

For automatic rendering and browser refresh while editing, run the shared
`quarto-site-live` command from this repository's root in Warp. Keep it running
and use the local URL it prints. Stop it with Ctrl+C. Its logs are ignored.

Generated HTML in `_site/` and the generated publication include are ignored. Normal rendering uses only Quarto and
Python’s standard library; bibliography import dependencies are separate.

## Profile, education, and experience

Edit `index.qmd` to update the homepage and short personal bio. The separate
Education & Experience page is `education-experience/index.qmd`, linked from
the homepage and navbar. It uses ordinary Markdown lists: add each degree with its institution and
graduation year, and each role with its institution or organization and date
range. Roles are grouped by institution. Keep current appointments first,
then most recent first, and omit unconfirmed details. The initial entries
come from Fred's July 2025 full CV; his Vice Provost appointment ended in 2024,
as he confirmed. Use degree abbreviations without periods, such as PhD and BA.

The CV source remains in the project's OneDrive Curriculum_Vitae folder.
Update the website's curated entries when that source changes; the site does
not copy or automatically publish the source folder.

## Publication catalog

`data/publications.json` is the public structured catalog; `data/publications.bib`
is its sanitized citation export. Both are generated snapshots. The authoritative
source remains Fred’s own bibliography in the shared master bibliography
folder, currently `FJHown26.bib`. When Fred adopts a newer annual file, pass
that file to `--source`; do not select a file merely by its modification date.
The import summary records the actual source filename and content hash.
Edit bibliographic details in that source, then refresh these snapshots.
Do not maintain a second copy of the citation details in the website exports.

To refresh from that source:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-import.txt
.venv/bin/python tools/import_publications.py --source ~/Documents/SharedConfigs/texmf/bibtex/bib/MasterBibFiles/FJHown26.bib
python3 tools/render_publications.py
quarto render
```

The importer expands author macros, resolves cross-references, selects records
authored or edited by Hickernell, and excludes private preparation records.
Public preprints and forthcoming publications carry explicit status. It keeps
only public bibliographic fields, excluding BibDesk attachments, local paths,
free-form notes, and private timestamps. Source files are never modified.

Keep website inclusion decisions in `data/publication-exclusions.json`, keyed
by BibTeX ID with a short reason. Talks, tutorial notebooks, recordings, blogs,
and documentation websites are excluded from the publication catalog; scholarly
conference papers and citable software releases remain. Check new records
during each refresh. These decisions survive changes to the master bibliography.
Live preview renders website changes but does not automatically reimport the
master bibliography outside this repository; run the import command above
after updating that source.

Add topic classifications in `data/publication-topics.json`, keyed by BibTeX ID:

```json
{"Hic98a": ["Quasi-Monte Carlo", "Discrepancy"]}
```

Use actual IDs from the catalog. Topics survive refreshes and appear as a filter
when present. Do not infer or bulk-assign topics without reviewing them.

`data/import-summary.json` records coverage and quality checks. A snapshot is
only as current as its source bibliography; Google Scholar and new public
preprints can be checked later for additions. Do not claim this is exhaustive.

## GitHub Pages

The publishing workflow builds pull requests and deploys pushes to `master`.
It renders with pinned Quarto 1.10.19, initializes `classlib`, validates the
consumer contract and public catalog, and uploads only `_site/`.

Repository **Settings → Pages → Source** uses **GitHub Actions**. Fred approved
the first Quarto launch on October 9, 2026. Future updates publish when reviewed
source is pushed to `master`; verify the workflow and deployed output after
publication. The root URL stays the same. Course and talk project-site URLs stay
in their owning repos.

The AcademicPages/Jekyll template and its sample records remain recoverable in
Git history. Its license notice is retained. `/publications/`, `/teaching/`,
and `/talks/` retain their established paths; `/cv/` points to Education & Experience.

See `PLAN.md` for scope and `notes/NEXT.md` for immediate next work.
