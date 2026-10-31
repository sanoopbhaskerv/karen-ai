# Kerala entries in NCERT national catalogues

Checked on **1 November 2026**. The [discovery index](ncert-kerala-exhibit-discovery.json) identifies **105 published exhibit rows from Kerala-located schools across 13 catalogues**. It records titles, exhibit codes, school/address wording, PDF pages and the evidence for school location. It does not reproduce synopses or personal contact information.

This is a catalogue audit, not a count of attendees, unique schools, Kerala DGE nominations or prizewinners. The same school or title can occur in several editions. Use [PROJECTS.md](PROJECTS.md) for selected method explanations and [MODEL_REPORTS.md](MODEL_REPORTS.md) for the eight extended write-ups. Those cases overlap the discovery material; their counts must not be added as if they were disjoint exhibits.

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
| 2022 | 0 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2022.pdf) |
| 2023 | 3 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/List_of_Exhibits_2023_Inquisitive_Minds_Pune.pdf) |
| 2024 | 6 | [NCERT catalogue](https://ncert.nic.in/desm/pdf/List_of_Exhibits/Exhibits_of_2024_Inquisitive.pdf) |

The zero for 2022 means no confident Kerala school entry was identified in the inspected catalogue. It does **not** establish that Kerala did not participate, had no nominated exhibit, or had no work represented elsewhere.

## How the rows were checked

For 2010–2017, the audit reviewed all **361 English synopsis-table pages**, checking school-address columns and resolving split rows. For 2018, 2019 and 2022–2024, it reviewed **815 English credit/address blocks**, with checks for unmatched exhibit-code and school/teacher layouts. These are different review units and must not be summed as an entry count. Representative and boundary pages were rendered and visually checked. Per-edition methods, page lists, source hashes and exceptions remain in the JSON.

Titles, codes and school spellings are preserved with layout whitespace joined. The two-part key is edition plus the literal exhibit code; a code alone is not a permanent project identity. Record IDs use a safe identifier form while keeping the source code in its own field. A report chapter number is a different identifier and is not substituted for an exhibit code.

## Boundaries that affect interpretation

- The 2010 *Safety Boat* row spans PDF pages 50 and 52. The Kerala address continuation belongs to that row, not the adjacent Maharashtra robot entry.
- Mahe/Puducherry and Lakshadweep schools remain outside this Kerala-state-location index. A Kerala-like PIN prefix alone is insufficient.
- The 2018 source's `Kerela` spelling and other published title/address anomalies are retained. Source mistakes are not silently corrected.
- A 2023 school field supplies a Naval Base/Kochi address without an institutional name. The index preserves the address rather than inventing a school name.
- Kerala-located KV and JNV entries are included by school location. Their selection through Kerala's Sasthrolsavam is not inferred; qualifying routes and prize fields remain null.
- Muvattupuzha hosting the 2015 national event does not make every entry a Kerala-school exhibit.

The inspected English archive has no year-labelled synopsis-catalogue links for 2020, 2021, 2025 or 2026. NCERT separately confirms that the 2020 and 2021 national editions were held together online in February 2022; [PATHWAYS.md](PATHWAYS.md) preserves that evidence. Missing archive links do not prove nonpublication or cancellation.

## Remaining work

Acquire original school reports, construction records, code and test data, then attach them to the correct edition and exhibit. Match reports and catalogue rows through explicit author or organiser evidence where possible; title/school similarities are recorded as candidate correspondence rather than silently filling unknown identifiers. Current school identities, merged schools and changed names need their own dated evidence if used for present-day contact or attribution.
