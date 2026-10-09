# Website direction

## Agreed purpose

Professional first, with a brief personal bio. Use Git, Quarto, and the existing
root GitHub Pages URL. The home page introduces Fred and directs readers to
education and experience, research, publications, teaching, talks, and
software. Education & Experience has its own page, linked from the home page
and navbar. Degrees and roles use editable Markdown lists; include dates only
when confirmed.
Use degree abbreviations without periods, such as PhD and BA.

The personal bio may mention family, following Christ, membership in Wheaton
Chinese Alliance Church, and living in Hong Kong. Fred will supply more detail
later; do not add family names or biographical dates without a source.

## Content ownership

- Personal website: profile, research overview, publication catalog, and curated
  links to courses, talks, and software.
- Course and talk repositories: their detailed materials and archives.
- QMCSoftware: project descriptions, software documentation, and community content.
- HickernellAcademicLib: shared components, academic resources, and library guidance.

AcademicLib’s existing website remains in place during the root migration.
Later, consider orienting it toward reusable resources, documentation, and
examples, with links to the canonical personal site. Preserve existing URLs
or redirect them when changing that site. This draft does not change AcademicLib.

## Publication catalog

Import Fred's designated current own bibliography (presently FJHown26.bib)
into a versioned public catalog. Start
with grouping by year, search, publication categories, and BibTeX download.
Keep topic tags and publication exclusions independent from the import so
curated classifications and inclusion decisions persist. Update citation
details in the master bibliography, then regenerate the public snapshots.
Exclude talks and notebook/blog/documentation resources from publications;
retain scholarly conference papers and citable software releases.
Treat preparation records and internal BibDesk fields as private. Separate
public preprints and forthcoming work from published records.

## Build and launch

1. Review and refine the first Quarto draft and bibliography coverage.
2. Verify desktop and phone layouts, navigation, citation data, and public links.
3. Review the complete diff, including removed template samples and CI.
4. Save reviewed work on the migration branch. At the agreed launch, merge it
   into `master` and switch Pages to GitHub Actions.
5. Expand selected publications, topics, a verified CV, and the talk archive as needed.

Fred approved the first Quarto launch on October 9, 2026. Future development
continues through reviewed changes published from `master`.

The Codex project is Personal Website, with the website repository as its
primary folder. HickernellAcademicLib, SharedConfigs, and the Obsidian vault
are supporting folders, together with the OneDrive Curriculum_Vitae folder
and the master bibliography folder. The project and this chat's membership
were verified on M5 on October 9, 2026; setup on the other Macs remains to be
verified.
