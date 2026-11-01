# Kerala entries in NCERT national catalogues

Checked on **1 November 2026**. The [discovery index](ncert-kerala-exhibit-discovery.json) identifies **105 published exhibit rows from Kerala-located schools across 14 reviewed publications**. It records titles, exhibit codes, school/address wording, PDF pages and the evidence for school location. It does not reproduce synopses or personal contact information.

This is a catalogue audit, not a count of attendees, unique schools, Kerala DGE nominations or prizewinners. The same school or title can occur in several editions. Use [PROJECTS.md](PROJECTS.md) for selected method explanations and [MODEL_REPORTS.md](MODEL_REPORTS.md) for the eleven extended write-ups. Those cases overlap the discovery material; their counts must not be added as if they were disjoint exhibits.

## Edition coverage

| Catalogue | Identified Kerala rows | Source |
| --- | ---: | --- |
| 2010 | 8 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2010_Jaipur.pdf) |
| 2011 | 7 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2011_Patna.pdf) |
| 2012 | 10 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2012_Silvassa.pdf) |
| 2013 | 8 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2013_Gangtok.pdf) |
| 2014 | 8 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2014_Chandigarh.pdf) |
| 2015 | 31 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2015_Muvattupuzha.pdf) |
| 2016 | 3 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2016_Bengaluru.pdf) |
| 2017 | 4 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2017_Bhopal.pdf) |
| 2018 | 8 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2018_Ahmedabad.pdf) |
| 2019 | 9 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2019_Raipur.pdf) |
| Combined 2020/2021 synopsis booklet | 0 | [Archived NCERT booklet](https://web.archive.org/web/20220205221256id_/http://jnnsmee.ncert.org.in/assets/files/Exhibits_Book_for_JNNSMEE_2020_2021.pdf) |
| 2022 | 0 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2022.pdf) |
| 2023 | 3 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2023_Inquisitive_Minds_Pune.pdf) |
| 2024 | 6 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/Exhibits_of_2024_Inquisitive.pdf) |

The zero for 2022 means no confident Kerala school entry was identified in that catalogue. The separate zero for the combined 2020/2021 booklet refers to its own 145 audited address blocks. It does **not** establish that Kerala did not participate, had no nominated exhibit, or had no work represented elsewhere.

## How the rows were checked

For 2010–2017, the audit reviewed all **361 English synopsis-table pages**, checking school-address columns and resolving split rows. For 2018, 2019 and 2022–2024, it reviewed **815 English credit/address blocks**, with checks for unmatched exhibit-code and school/teacher layouts. These are different review units and must not be summed as an entry count. Representative and boundary pages were rendered and visually checked. Per-edition methods, page lists, source hashes and exceptions remain in the JSON.

The newly recovered **188-page combined 2020/2021 booklet** has **145 English school/address blocks**, split into **81 labelled 2020** and **64 labelled 2021**, all read in native text and as rendered address crops. Its seven 2020 and five 2021 subtheme sections were covered. Parallel Hindi/English synopses share each exhibit: they are not 290 distinct entries, and 145 blocks are not a unique-school or attendee count. Ten full frontmatter/boundary/sample/end pages were also read; no full technical or bilingual translation audit of every synopsis is claimed.

Titles, codes and school spellings are preserved with layout whitespace joined. The two-part key is edition plus the literal exhibit code; a code alone is not a permanent project identity. Record IDs use a safe identifier form while keeping the source code in its own field. A report chapter number is a different identifier and is not substituted for an exhibit code.

## Boundaries that affect interpretation

- The 2010 *Safety Boat* row spans PDF pages 50 and 52. The Kerala address continuation belongs to that row, not the adjacent Maharashtra robot entry.
- Mahe/Puducherry and Lakshadweep schools remain outside this Kerala-state-location index. A Kerala-like PIN prefix alone is insufficient.
- The 2018 source's `Kerela` spelling and other published title/address anomalies are retained. Source mistakes are not silently corrected.
- A 2023 school field supplies a Naval Base/Kochi address without an institutional name. The index preserves the address rather than inventing a school name. A separately linked participant form supplies the institution name; see [SELECTIONS.md](SELECTIONS.md#a-separate-source-identifies-the-kochi-institution).
- Kerala-located KV and JNV entries are included by school location. Their selection through Kerala's Sasthrolsavam is not inferred; qualifying routes and prize fields remain null.
- Muvattupuzha hosting the 2015 national event does not make every entry a Kerala-school exhibit.

The inspected English archive lacked year-labelled synopsis links for 2020, 2021, 2025 and 2026. A separate archived NCERT portal now supplies the combined **2020/2021** booklet. Its December 2021 preface schedules the 47th/48th national exhibitions online for **8–11 February 2022**; its February PDF metadata and archive capture remain separate. The later annual report records the combined event in [PATHWAYS.md](PATHWAYS.md). The book is a selected-exhibit overview, rather than an original construction report or a new Kerala method chapter. Missing links in one archive did not establish nonpublication or cancellation.

## Remaining work

Acquire original school reports, construction records, code and test data, then attach them to the correct edition and exhibit. Match reports and catalogue rows through explicit author or organiser evidence where possible; title/school similarities are recorded as candidate correspondence rather than silently filling unknown identifiers. Current school identities, merged schools and changed names need their own dated evidence if used for present-day contact or attribution.

## Three candidate correspondences to the 2015 regional results

Existing 2015 discovery rows 16.2.8, 16.4.2 and 16.6.2 have [qualified SISF correspondences](SISF_HISTORY.md#three-qualified-links-to-the-ncert-2015-catalogue) in school/title/topic wording. Complete original catalogue pages 38, 80 and 120 were read for this comparison. Preserve the school-only national credits and literal variants; no pupil/guide names, prize, qualifying route, unique identity or unchanged version is transferred. The discovery dataset’s 105 records remain unchanged. The plastic-burning environmental claim and short concrete-recovery description do not supply emissions, material-performance or independent safety evidence.
