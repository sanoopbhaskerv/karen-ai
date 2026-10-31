# District portal status and Working Model reports, 2026

Captured on **1 November 2026** in India, between **20:39:16 and 20:39:23 UTC on 31 October**. The [structured snapshot](district-status-2026.json) preserves all **14 district status pages, 210 fair/section rows and 28 Science Working Model item-row observations**. These are public portal snapshots, not certified final results or attendance counts. The [source register](district-status-sources.json) records URLs, acquisition times, hashes and byte sizes for all 42 HTML pages.

## Observed status

The first two numeric columns below reproduce each status page's displayed totals. Each page uses a **221-row generic catalogue**. Its UP rows do not independently establish district-level pupil eligibility. A completed counter is the portal's published status, not proof that every item in an eligible competition programme has finished.

| District | Displayed completed | Displayed total | HS Working Model report link | HSS/VHSS Working Model report link |
| --- | ---: | ---: | --- | --- |
| Thiruvananthapuram | 170 | 221 | Present | Present |
| Kollam | 19 | 221 | Absent | Absent |
| Pathanamthitta | 16 | 221 | Absent | Absent |
| Alappuzha | 17 | 221 | Absent | Absent |
| Kottayam | 16 | 221 | Absent | Absent |
| Idukki | 15 | 221 | Absent | Absent |
| Ernakulam | 20 | 221 | Absent | Absent |
| Thrissur | 13 | 221 | Absent | Absent |
| Palakkad | 15 | 221 | Absent | Absent |
| Malappuram | 18 | 221 | Absent | Absent |
| Kozhikode | 13 | 221 | Absent | Absent |
| Wayanad | 19 | 221 | Absent | Absent |
| Kannur | 13 | 221 | Absent | Absent |
| Kasaragod | 19 | 221 | Absent | Absent |

“Absent” means no public report link occurred in the retrieved **HS 115** or **HSS/VHSS 126** item row. It does not establish that a contest was cancelled, had no entrants, or had not been held. The index retains each actual item-list URL and capture time; the [district index](districts.json) supplies the official navigation destinations.

The [Palakkad landing page](https://mela.kite.kerala.gov.in/2026/district/index.php/result/Public_result/dist_index/9/Palakkad) already displays *Overall School Champion* and *Overall Sub District Champion* panels, while its [status page](https://mela.kite.kerala.gov.in/2026/district/index.php/result/Public_result/status/9) shows 15 completed catalogue rows. A heading or current leader must not be promoted to a final championship without a final result statement.

## Preserve the arithmetic discrepancy

The [Alappuzha status page](https://mela.kite.kerala.gov.in/2026/district/index.php/result/Public_result/status/4) reports **8 total, 1 completed and 8 incomplete** for both HS and HSS/VHSS IT. Its grand total is **221 total, 17 completed and 206 incomplete**. These figures do not satisfy total = completed + incomplete. The sums of their displayed columns do agree with their corresponding row sums; that does not resolve the internal discrepancy.

The dataset retains the source values and calculated reconciliation flags. The cause is unknown. Dashes in either completion column are retained as published and interpreted as zero only for arithmetic checks; they are not claims about attendance or eligibility. No values were silently corrected.

## Two available Working Model grade reports

The two Thiruvananthapuram PDFs identify **St. Mary's HSS Pattom**, **23–25 October 2026**, and report generation **1 November 2026, 02:12 am**. The timestamp has no explicitly printed timezone. Each is three pages with **46 published pupil rows: 30 A and 16 B grades**. The derived index retains only these aggregates.

- [HS Working Model 115, all-grade report](https://mela.kite.kerala.gov.in/2026/district/index.php/result/Public_result/reportforCertificate/115/1/3/0/2/1).
- [HSS/VHSS Working Model 126, all-grade report](https://mela.kite.kerala.gov.in/2026/district/index.php/result/Public_result/reportforCertificate/126/1/4/0/2/1).

These are pupil rows, not a verified count of distinct exhibits or attendees. The reports have no rank/mark column and no project titles or mechanisms. The first A-grade row cannot be called the winner from this report alone. Individual names, registration numbers, raw PDFs and page images are not copied into this collection.

For entry rules use [RULES.md](RULES.md), and for historically captured overall scores use [RESULTS.md](RESULTS.md). This district snapshot is a different evidence layer and does not reconcile earlier championship conflicts.
