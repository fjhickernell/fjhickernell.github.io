# NEXT

## Current state

Production publishes the Quarto site from `master` through GitHub Actions at
the established root URL. Fred approved the launch on October 9, 2026. The
initial migration was developed on `codex/quarto-personal-site`; future changes
can be reviewed on topic branches. Confirm the deployment workflow and live
output after publication. AcademicLib is pinned as `classlib` and unchanged
upstream.

The Personal Website Codex project is established on M5, with this repository
as its primary folder and this chat attached. Its portable folder assignments
are recorded in the shared project inventory.

The draft has Home, Education & Experience, Research, Publications, Teaching,
Talks, and Software pages. The separate Education & Experience page lists two
degrees and ten academic and administrative appointments, transcribed from Fred's July 2025
full CV. The page also includes three awards and seven society distinctions.
Six distinctions are from that CV, cross-checked against the March 2026 brief CV;
Fred supplied the SIAM fellowship (since 2026) on October 12, 2026.
Society distinctions are displayed without dates, following Fred's edits.
The homepage includes his supplied research wording and family/church bio.
It also links to his Microsoft Bookings page, with an email fallback when no
suitable meeting time is available.
Fred confirmed the Vice Provost for Research appointment as 2018–2024;
he no longer held that role from January 2025. The March 2026 brief CV's
2018–present entry is outdated. The source CV folder remains in OneDrive;
its contents are not copied into the site.
The homepage and navbar link to the page; the legacy `/cv/` URL redirects there.
The centered content column is widened to 1400px on large screens, and main
page titles are slightly smaller. Local typography overrides preserve 18px
reading text; long names can wrap at narrow widths.
The publication catalog is imported from Fred’s confirmed FJHown26.bib, with
public-field sanitization, status labels, year grouping, search, and topic support.
Keep citation details in Fred's designated current own bibliography; adopt a
new annual source explicitly and refresh the versioned public snapshots.
Topic tags and resource exclusions are maintained separately in data/ and
survive refreshes. Six talk/notebook/blog/documentation resources are excluded.
Author initials are preserved as literal HTML so Y. Li and A. Jain cannot become
ordered-list markers. Publication type/status and public links share a wrapping row.

Use `quarto-site-live` from this repository for automatic rendering and browser
refresh. The SharedConfigs helper now watches nested page folders and ignores
directory-only events and temporary HTML/library output that previously caused
a render loop. The master
bibliography still requires an explicit import after it changes; see README.md.
The Publications page loads its generated catalog through a Lua filter after
the pre-render hook, so fresh checkouts can render and start live preview
without first generating the ignored include manually.

## Immediate next work

Fred submitted the Marketing and Communications directory-link request on
October 12, 2026. Await their update linking his Illinois Tech faculty profile
to https://fjhickernell.github.io/ and updating any existing Applied Mathematics
personal-website links. Submission is complete; the institutional link changes
remain unconfirmed. Use the [project request page](https://www.iit.edu/marketing-communications/submit-project-request)
for the official form and process.

Refine home/bio wording, featured publications, topic tags, and source freshness
with Fred. See the
import summary for exclusions and metadata gaps; do not infer missing years or
promote private manuscripts based on the current date.

For updates, review changes and repeat local validation before merging into
`master`. The workflow builds pull requests and deploys pushes to `master`;
topic-branch validation alone does not publish the site.

## Questions to resolve

- Which publications should be featured, and what topic vocabulary should be used?
- Which public preprints or newer records are absent from the master bibliography?
- What additional family and Hong Kong bio details should be public?
- Which additional degrees or roles, including editorial or visiting appointments,
  should be listed beyond the CV's education and employment history?
- Should AcademicLib’s website later become a dedicated resource/documentation hub?

## Validation and coverage

Full Quarto render, public catalog checks, local-link checks, and seven focused
catalog regression tests, including a fresh-checkout render, pass. The shared live-preview helper's isolated
integration test checks nested page saves and prevention of render loops.
All pages were inspected at desktop and 390px phone width. Navigation collapses below
1200px to keep the longer education/experience label readable. Publication
filtering, empty results, and mathematical titles work.
Main course/talk/church/software links return HTTP 200. Speaker Deck rejects
command-line verification with HTTP 403; its established link is retained.

The import contains 144 public records (1977–2026): 139 published, two
forthcoming, and three public preprints. Of 196 source records, 13 preparation
records, 23 reference-only entries, five review records without public
identifiers, five missing/uncertain-year entries, and six nonpublication
resources are excluded. Seventy-nine records have no DOI or public URL.
The arXiv-only GAIL technical report is labeled as a public preprint.
Two GAIL version records share a DOI and
are retained as distinct releases. One public preprint retains a source year
marked with a plus. Review metadata before claiming exhaustive coverage.
The source bibliography’s content hash is unchanged.
