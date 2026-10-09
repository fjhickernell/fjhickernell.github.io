<!-- classlib-consumer-contract:start -->
## Shared classlib guidance

This repository consumes `classlib` as a pinned submodule. Initialize the
recorded submodule commit before substantive work; do not replace it with a
moving branch tip during routine setup or validation.

Before substantive work involving shared teaching, presentation, webpage,
content, component, or infrastructure conventions, read
`classlib/AGENTS.md`. Guidance applies in this order:

1. applicable global instructions;
2. shared guidance in the pinned `classlib/AGENTS.md`;
3. explicit consumer-local instructions and exceptions.

Keep universal guidance in `classlib` rather than copying it locally. Record a
genuine local exception explicitly, including its scope and reason. Flag an
apparent accidental conflict for review instead of silently resolving it.
<!-- classlib-consumer-contract:end -->

# Personal Website

This is the professional/personal Quarto site served at fjhickernell.github.io.
Read PLAN.md and notes/NEXT.md before substantive work. Follow the shared
webpage guide in classlib/docs/webpage-style.md. Keep detailed course and talk
content in its owning repository; link to it here.

## Explicit local exceptions

The shared classroom theme favors 21px text and wide projector layouts.
This personal site uses 18px text, serif headings with modest page titles,
a portrait introduction, and full-width pages constrained to a centered content
column up to 1400px wide without a side table of contents. Scope these overrides to site.scss; do not change
the shared teaching theme to implement them.

## Public catalog

Fred's designated current own bibliography, presently FJHown26.bib, is the
authoritative import source. Use a newer annual file when Fred adopts it;
record the filename and hash in the import summary. Keep preparation records,
local attachment paths, BibDesk metadata, and private notes out of all public
exports. Label preprints and forthcoming work separately. Topic tags belong
in data/publication-topics.json; website inclusion decisions belong in
data/publication-exclusions.json. Both must survive source refreshes. Talks,
notebooks, recordings, blogs, and documentation websites are not publications.
Retain scholarly conference papers and citable software releases. Do not
infer missing bibliographic metadata. Run the catalog and rendered-link checks,
render the site, and inspect desktop and narrow layouts before publication.

## Publication

The production branch is master. Publishing requires the complete migration
and the repository’s Pages source set to GitHub Actions. Do not assume a
successful local render establishes a successful remote deployment. Preserve
the existing root URL and established links where practical.
