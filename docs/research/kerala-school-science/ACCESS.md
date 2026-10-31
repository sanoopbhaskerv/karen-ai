# Official portals and adjacent exhibitions

Checked on 31 October 2026. Portal contents are edition-specific snapshots and may change as registrations, appeals and results are processed.

## Registration and school records

The [2026 school portal](https://mela.kite.kerala.gov.in/2026/) says school registration has started and directs schools to use their Sampoorna login. The [2026 download zone](https://mela.kite.kerala.gov.in/2026/index.php/publics/instructions) links to the revised 2025 competition manual and a five-page school software guide whose filename and screenshots identify it as a 2022–23 guide.

That [software guide](https://mela.kite.kerala.gov.in/2026/entry_forms/School%20Sasthrolsavam_2022_23_school%20login_user%20manual_30_09.pdf), PDF pages 1–5, describes school/escorting-teacher details, participant entry using admission numbers, fair-by-fair confirmation, printing the list, and an AEO-office reset after confirmation. Its LP teacher-item screen is a teacher-registration provision. The old interface screenshots should not be treated as a guarantee of today's screen layout or deadline.

For Karen, the school's registration printout is the most useful next record: it should identify the fair, exact item, code if supplied, section, registered participant and organiser. A local phrase such as IT Working Model cannot be assigned a state item code without that evidence. No account login was required to inspect the public material collected here.

## Results and levels

The [2026 state results page](https://mela.kite.kerala.gov.in/2026/state/index.php/result/Public_result) links to declared results, school/subdistrict/district points by fair, overall tables, a map, special-school provision and Vocational Expo. On the access date its overall champion panels said no results had been published. A Results heading or an empty destination does not establish a completed contest.

The [district index](https://mela.kite.kerala.gov.in/2026/district/index.php/result/Public_result) exposes all 14 district result destinations. Their names, identifiers and exact observed URLs are in [districts.json](districts.json). These identifiers are portal keys, not ranks. Follow the edition's own navigation rather than assuming every old endpoint has the same argument structure.

An individual result row and a fair-wide points table answer different questions. A school's overall position is not the result for a particular model; a contestant's grade is not necessarily a rank. Preserve appeals or revisions where shown. The general master item list has rows for sections and teacher items that do not all compete at every level; level-specific eligibility comes from the manual and circulars.

## Item catalogue snapshots

The official [2025 master list](https://mela.kite.kerala.gov.in/2025/state/index.php/publics/item_list) and [2026 master list](https://mela.kite.kerala.gov.in/2026/state/index.php/publics/item_list) each supplied 221 catalogue rows when directly fetched. Counts computed from the rows are:

| Fair label in source | Catalogue rows in each snapshot |
| --- | ---: |
| Science Fair | 39 |
| Mathematics Fair | 42 |
| Socialscience Fair | 25 |
| Workexperience Fair | 95 |
| IT Fair | 20 |

These are counts of catalogue records, including teacher entries, rather than counts of eligible student state contests. Ditto marks in section/fair cells have been expanded in the JSON. Source spellings, item codes and participant codes are preserved. The 2026 master list can be fetched directly even when a browser search tool returns an error. Small wording differences between snapshots are retained rather than rewritten into a single version.

The subdistrict views include LP items omitted from the current state-page view. The following additional snapshots were directly retrieved; their provenance is retained with each JSON file:

| Edition and view | All rows | LP rows | Snapshot |
| --- | ---: | ---: | --- |
| 2019 state-page historical catalogue | 154 | 0 | [2019 catalogue](item-catalogue-2019.json) |
| 2022 subdistrict catalogue | 239 | 39 | [2022 catalogue](subdistrict-catalogue-2022.json) |
| 2023 subdistrict catalogue | 239 | 39 | [2023 catalogue](subdistrict-catalogue-2023.json) |
| 2024 subdistrict catalogue | 239 | 39 | [2024 catalogue](subdistrict-catalogue-2024.json) |
| 2025 subdistrict catalogue | 261 | 40 | [2025 catalogue](subdistrict-catalogue-2025.json) |
| 2026 subdistrict catalogue | 261 | 40 | [2026 catalogue](subdistrict-catalogue-2026.json) |

Together with the two 221-row state-page snapshots above, these eight catalogues contain 1,835 observations across editions. Repeated item codes across years are separate versioned observations. The 2019 state-page view has four UP rows, rather than the newer generic UP list; do not infer a change in pupil eligibility from that interface difference. [Rule changes](RULE_CHANGES.md) documents the actual manual/order evidence. A 2019 subdistrict URL probe redirected in a loop, so it was not labelled a successfully captured catalogue.

## Special-school work experience fair

The [2025–26 special-school portal](https://mela.kite.kerala.gov.in/2025/spss2025/index.php/login) explicitly names a separate State Special School Work Experience Fair. The [2026–27 results interface](https://mela.kite.kerala.gov.in/2026/spss2026/index.php/publishresult/resultindex/resultview) separates visually impaired, hearing impaired LP–UP, hearing impaired HS, hearing impaired HSS, and two exhibition sections. It displayed zero declared items on the access date. These are the source's own category names.

Its [download zone](https://mela.kite.kerala.gov.in/2026/spss2026/index.php/publics/instructions) links a manual, identity certificate and [three-page item-code PDF](https://mela.kite.kerala.gov.in/2026/spss2026/assets/docs/item_codes.pdf). The PDF contains 80 numbered catalogue records. The structured [special-school-items.json](special-school-items.json) preserves all 80, with code, source page and participant limit. Examples include craft work, waste-material products and exhibitions; it does not establish an additional general Science or IT Working Model item.

The linked [manual PDF](https://mela.kite.kerala.gov.in/2026/spss2026/assets/docs/StateSpecialschoolKalolsavamManual.pdf) has 18 scanned pages. Despite Kalolsavam in its filename, its first page discusses special-school work-experience aims and organisation. A version date was not established, and its pages are rotated scans. Its substantive numerical rules have not been adopted into the general competition guide.

## Vocational Expo and Career Fest

KITE's [Sasthrolsavam description](https://mela.kite.kerala.gov.in/2026/state/index.php/result/Public_result/about_us) describes a Vocational Expo showing products made through vocational higher secondary production-training centres and a Career Fest offering guidance. These are adjacent activities; participation is not the same as a Science Working Model result.

The state portal's 2026 Vocational Expo destination, `https://mela.kite.kerala.gov.in/2026/vhseExpo/state26/index.php`, returned HTTP 404 when inspected. Current entry instructions, venues and programme details still need an official notice or a working replacement link.

## Downloads needing replacement or confirmation

| Officially linked destination | Observation on access date | What would resolve it |
| --- | --- | --- |
| `2026/state/entry_forms/Program_Notice_2026.pdf` | HTTP 404 | Published programme PDF or organiser's final schedule |
| `2026/vhseExpo/state26/index.php` | HTTP 404 | Current VHSE Expo page or circular |
| Special-school manual named `StateSpecialschoolKalolsavamManual.pdf` | Retrieved 18-page scanned work-experience document; no version established | Signed applicable manual/order and amendments |
| General school software guide linked in 2026 | Filename/screens identify 2022–23 | Current operator instructions and local deadline |

Temporary browser failures are not the same as confirmed missing documents. Several official PDFs were retrieved directly and visually inspected after the browser tool timed out. Source retrieval notes record that distinction.
