# Historical result snapshots

The [structured result snapshots](result-snapshots.json) preserve the current official KITE overall district and school tables for 2019, 2022, 2023, 2024 and 2025, fetched on 31 October 2026. The ten tables contain **6,379 rows: 70 district rows and 6,309 school rows across five editions**. Repeated schools across editions are separate observations, not distinct schools.

These are overall festival point tables. They do not identify the winner of a particular Science Working Model event. They are also not certified reconciliations of disagreements between the live historical archive and contemporary government or press reports. Read the source conflicts in [the history guide](HISTORY.md) before giving an unqualified championship answer.

## Tables captured

| Portal year | District rows | School rows | Observed first district | Observed first school |
| --- | ---: | ---: | --- | --- |
| 2019 | 14 | 1,259 | Palakkad, 1,366 | BSS Gurukulam HSS Alathur, 146 |
| 2022 | 14 | 1,236 | Palakkad, 1,383 | Durga HSS Kanhangad, 112 |
| 2023 | 14 | 1,264 | Malappuram, 1,407 | Durga HSS Kanhangad, 142 |
| 2024 | 14 | 1,262 | Malappuram, 1,429 | Durga HSS Kanhangad, 135 |
| 2025 | 14 | 1,288 | Malappuram, 1,548 | Sacred Heart HSS Dwaraka, 164 |

These headings describe what the fetched tables display. In particular, the 2019, 2022, 2023 and 2024 archive records have conflicts documented in the history guide. A score from this table must be attributed to the observed KITE archive rather than presented as a reconciled final historical result.

Official source destinations:

| Year | Overall district table | Overall school table |
| --- | --- | --- |
| 2019 | [District points](https://mela.kite.kerala.gov.in/2019/state/result/Public_result/districtwisePointdetailed/0/0/0/1) | [School points](https://mela.kite.kerala.gov.in/2019/state/result/Public_result/schoolwisePointdetailed/0/0/0/1) |
| 2022 | [District points](https://mela.kite.kerala.gov.in/2022/state/index.php/result/Public_result/districtwisePointdetailed/0/0/0/1) | [School points](https://mela.kite.kerala.gov.in/2022/state/index.php/result/Public_result/schoolwisePointdetailed/0/0/0/1) |
| 2023 | [District points](https://mela.kite.kerala.gov.in/2023/state/index.php/result/Public_result/districtwisePointdetailed/0/0/0/1) | [School points](https://mela.kite.kerala.gov.in/2023/state/index.php/result/Public_result/schoolwisePointdetailed/0/0/0/1) |
| 2024 | [District points](https://mela.kite.kerala.gov.in/2024/state/index.php/result/Public_result/districtwisePointdetailed/0/0/0/1) | [School points](https://mela.kite.kerala.gov.in/2024/state/index.php/result/Public_result/schoolwisePointdetailed/0/0/0/1) |
| 2025 | [District points](https://mela.kite.kerala.gov.in/2025/state/index.php/result/Public_result/districtwisePointdetailed/0/0/0/1) | [School points](https://mela.kite.kerala.gov.in/2025/state/index.php/result/Public_result/schoolwisePointdetailed/0/0/0/1) |

## Data fields and checks

Each snapshot records its source URL, retrieval timestamp, response hash, table scope and row count. Each row preserves display order, district or school identity, counts of first/second/third places, counts of A/B/C grades and total points. School codes are strings so their identifiers are not treated as arithmetic quantities. Source spellings are preserved.

The displayed counts reproduce every captured total under this arithmetic check:

```text
5 × first places + 3 × second places + third places
+ 5 × A grades + 3 × B grades + C grades
```

This checks internal numerical consistency only. It cannot show that an archive includes every applicable contest, incorporates every appeal, or uses the same scope as a contemporary closing report. Display order is retained without inferring a universal tie-break rule. The 2025 PRD explanation of its equal-point ranking is separately cited in the history guide.

A separate aggregation check also finds that the school and district views do not always reconcile:

| Year | Sum of displayed district points | Sum of displayed school points | Sums agree |
| --- | ---: | ---: | --- |
| 2019 | 17,266 | 17,270 | No |
| 2022 | 17,831 | 16,206 | No |
| 2023 | 17,608 | 17,551 | No |
| 2024 | 17,814 | 17,764 | No |
| 2025 | 19,865 | 19,865 | Yes |

All data rows in each fetched HTML table were accounted for, and each detailed table's first five rows match the separately fetched landing page. These checks do not explain the aggregate differences. Do not invent a missing-school, appeal, exclusion or correction explanation; the applicable organisers' consolidated records are still needed.

For an individual exhibit, begin at the edition's declared-results list, then identify fair, pupil section and item code. Keep an item's place and grade separate from an overall school score. Detailed individual-result pages remain linked from the official archives; they are not all included in this overall-table snapshot.
