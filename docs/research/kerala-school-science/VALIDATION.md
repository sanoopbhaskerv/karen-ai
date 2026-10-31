# Research collection checks

Checked on 31 October 2026. These checks establish the integrity and stated scope of the collected records. They do not resolve missing historical evidence or independently validate the performance of student exhibits.

## Collection inventory

| Material | Checked count |
| --- | ---: |
| Source records | 136 |
| Distinct source URLs | 132 |
| JSON files | 22 |
| Concise English/Malayalam knowledge records | 63 |
| Draft Malayalam evaluation questions | 44 |
| Indexed exhibit records | 16 |
| General catalogue snapshots | 8 |
| Catalogue observations across those snapshots | 1,835 |
| Separate special-school catalogue records | 80 |
| Historical overall district/school table snapshots | 10 |
| Rows in those historical tables | 6,379 |
| District-result destinations | 14 |

Repeated item codes, schools and source URLs across editions are versioned observations. They are not counts of distinct participants, original scientific projects, or independent corroborating publishers.

## Data and reference checks

- Every JSON and JSONL record parses. Source, claim, question, project and within-snapshot catalogue identifiers are unique in their stated scope.
- The unified source register reproduces all topic source registers. Every referenced source and knowledge identifier resolves, including the signed INSPIRE notification and the repository implementation evidence.
- Each catalogue's row count, fair count and section count agrees with its records. Ditto fields have been expanded. Every stored catalogue difference was recomputed from its two matching subdistrict views.
- Every result table's stored row count agrees with the extracted rows. All HTML data rows were accounted for, and the top five entries agree with independently retrieved landing-page summaries.
- The observed grade/place counts reproduce all 6,379 displayed result totals. Cross-table school/district sums were calculated separately; the mismatches are retained in [RESULTS.md](RESULTS.md), rather than described as reconciled final outcomes.
- Every local Markdown target and linked heading resolves. Whitespace checks passed. No downloaded source PDFs, source credentials or scratch environments are included in the research directory.

## Domain review

Relevant official PDF pages were extracted and visually checked, including the two-pupil Working Model wording, required group attendance, dimensions, chart count, construction-video condition and the seven-criterion 100-mark rubric. The 2019 manual, later orders and 2026 circulars are kept distinct.

Independent reviews checked historical edition boundaries, source-specific championship disagreements, different catalogue views, primary-teacher versus pupil progression, the recovered 2009 integration milestone, the dated INSPIRE quota and the distinction between exhibit selection, award scope and measured performance. NCERT case records retain their page references and school-system boundaries.

Malayalam records remain marked for a teacher's language and educational review. They are a research/evaluation collection, not an approved model-training file. Runtime behaviour, live providers and physical hardware were not changed or exercised by this research; application tests are not evidence that the archive is historically complete.

The initial research commit passed the repository's Windows setup CI. Publication of later additions is tracked by the pull request's checks. The unresolved work is listed in [COVERAGE.md](COVERAGE.md).
