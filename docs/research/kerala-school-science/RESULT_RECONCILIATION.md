# Result conflicts: dated publication versions, certification still missing

Checked 1 November 2026. Archived official KITE pages now document changes in the published 2022, 2023 and 2024 overall tables. They also establish that the current 2019 score version was already displayed in September 2022. This improves the chronology of the conflicts in [HISTORY.md](HISTORY.md); **no signed final championship statement or authenticated correction order explaining them was recovered**.

The [version dataset](result-version-snapshots.json) preserves 17 selected capture pages: 12 complete table observations containing 7,675 rows, plus ten landing-page top-five observations containing 50 rows. These are repeated observations of districts and schools, not unique participants. The existing [ten overall snapshots](result-snapshots.json), containing 6,379 rows, are unchanged. The [companion sources](result-reconciliation-sources.json) group versions of the same original KITE endpoint and retain each actual replay URL, requested URL, response hash, byte count and Memento-Datetime.

## 2019: a longstanding portal version

The [29 September 2022 district capture](https://web.archive.org/web/20220929212655id_/https://mela.kite.kerala.gov.in/2019/state/result/Public_result/districtwisePointdetailed/0/0/0/1) gives Palakkad 1,366, Kozhikode 1,364 and Kannur 1,351. All 14 district rows match the October 2026 snapshot. The [school capture that evening](https://web.archive.org/web/20220929214839id_/https://mela.kite.kerala.gov.in/2019/state/result/Public_result/schoolwisePointdetailed/0/0/0/1) contains 1,259 rows and BSS Gurukulam 146. School names and numerical fields match the current table when keyed by school code; display order differs, so no stable ordering for equal scores is inferred.

This does not resolve the [government closing report](https://keralanews.gov.in/115/State-science-fest:-Kozhikode-district-overall-champions.html), which names Kozhikode after a 1,374-point tie and gives BSS Gurukulam 141. The archived portal version is established by September 2022, without identifying when or why it diverged from the closing report. Sources `result-reconciliation-001` and `002`.

## 2022: several score versions and a school-order change

| Actual capture | Leading districts, points | Leading schools, points | Observation scope |
| --- | --- | --- | --- |
| 26 November 2022 | Palakkad 1,383; Malappuram 1,350; Kannur 1,338 | Fathima Matha 125; Durga 117; Mananthavady 113 | Separate full district/school captures; 14 / 1,294 rows |
| 28 January 2023 | Palakkad 1,378; Malappuram 1,350; Kannur 1,338 | Fathima Matha 120; Durga 117; Mananthavady 108 | One landing page; five displayed leaders in each table |
| 2 April 2023 | Palakkad 1,378; Malappuram 1,345; Kannur 1,338 | Durga 117; Fathima Matha 115; Mananthavady 108 | Separate full captures; 14 / 1,244 rows |
| Existing October 2026 snapshot | Palakkad 1,383; Malappuram 1,345; Kannur 1,338 | Durga 112; Fathima Matha 110; Mananthavady 108 | Existing full tables; 14 / 1,236 rows |

The [November school page](https://web.archive.org/web/20221126154432id_/https://mela.kite.kerala.gov.in/2022/state/index.php/result/Public_result/schoolwisePointdetailed/0/0/0/1), [January landing page](https://web.archive.org/web/20230128204830id_/https://mela.kite.kerala.gov.in/2022/state/index.php/result/Public_result) and [April school page](https://web.archive.org/web/20230402083444id_/https://mela.kite.kerala.gov.in/2022/state/index.php/result/Public_result/schoolwisePointdetailed/0/0/0/1) document the sequence. The previously registered closing press report gives Fathima Matha 120 and Mananthavady 113, rather than exactly matching one captured version. Preserve that report too. The order changed between observed publications; the authority, policy, appeal handling and exact revision dates remain unestablished. Sources `003`–`005`, with the two full-table versions retained under their original-endpoint source IDs.

## 2023: primary support for the contemporary closing totals

The genuine [7 December 2023 KITE landing capture](https://web.archive.org/web/20231207131226id_/https://mela.kite.kerala.gov.in/2023/state/index.php/result/Public_result) gives Malappuram 1,442, Palakkad 1,350 and Kannur 1,333; schools Durga 142, Fathima Matha 138 and Panangad 134. These agree with the contemporary closing figures already recorded in the history guide. A checked 9 December repeat has the same displayed leaders; it is not counted as an independent publisher or additional dataset capture.

The [15 June 2024 district capture](https://web.archive.org/web/20240615070504id_/https://mela.kite.kerala.gov.in/2023/state/index.php/result/Public_result/districtwisePointdetailed/0/0/0/1) and [11 November 2024 school capture](https://web.archive.org/web/20241111020135id_/https://mela.kite.kerala.gov.in/2023/state/index.php/result/Public_result/schoolwisePointdetailed/0/0/0/1) match all keyed numerical/name fields in the respective current 14 / 1,264-row tables. They show Malappuram 1,407, Palakkad 1,320 and Kozhikode 1,299; schools Durga 142, Panangad 134 and Fathima Matha 133. This dates two publication states, rather than certifying a final correction or its cause. Sources `006`–`008`.

## 2024: closing figures, an intermediate state, then current leaders

| Actual capture | Leading districts, points | Leading schools, points | Scope |
| --- | --- | --- | --- |
| 2 December 2024 | Malappuram 1,450; Kannur 1,412; Kozhikode 1,353 | Durga 140; Dwaraka 131; Fathima Matha 126 | Landing page, top five per table |
| 17–18 April 2025 | Malappuram 1,450; Kannur 1,412; Kozhikode 1,353 | Durga 140; Dwaraka 131; Fathima Matha 126 | Separate full school capture on 17 April and district capture on 18 April; 1,268 / 14 rows |
| 1 May 2025 | Malappuram 1,440; Kannur 1,399; Kozhikode 1,343 | Durga 135; Dwaraka 131; Fathima Matha 126 | Landing page, top five per table |
| 23 May 2025 | Malappuram 1,429; Kannur 1,389; Kozhikode 1,328 | Durga 135; Dwaraka 126; Fathima Matha 126 | Landing page, top five per table |
| 8–9 September 2025 | Same numerical/name content as the current district table | Same keyed numerical/name content as the current school table | Separate full captures; 14 / 1,262 rows |

The [2 December landing](https://web.archive.org/web/20241202104858id_/https://mela.kite.kerala.gov.in/2024/state/index.php/result/Public_result) reproduces the leaders in the [PRD closing release](https://www.prd.kerala.gov.in/ml/node/274429). The [1 May](https://web.archive.org/web/20250501035117id_/https://mela.kite.kerala.gov.in/2024/state/index.php/result/Public_result) and [23 May](https://web.archive.org/web/20250523120125id_/https://mela.kite.kerala.gov.in/2024/state/index.php/result/Public_result) captures establish an intermediate publication version and the later displayed leaders. None identifies a correction order or explains the differing counts. Sources `009`–`011`.

One important replay limitation: requesting the nominal **10 December 2024 district** capture redirects to an **18 April 2025** memento. It is recorded once under the actual capture date. A CDX listing or requested timestamp alone is insufficient date evidence; the effective URL and Memento-Datetime were checked for every selected body.

## Arithmetic and a dated grading provision

Every stored row reproduces its displayed total under the existing 5/3/1 place-plus-grade check. This confirms arithmetic, not the inclusion rules. Separate full district/school captures still have differing point sums: 2019 September observations differ by 4; November 2022 by 33; April 2023's 2022 views by 1,355; April 2025's 2024 views by 50; and September 2025's 2024 views by 50. Their timestamps differ, so these are explicitly non-atomic cross-capture calculations. No missing-school, teacher-point, appeal or software explanation is inferred.

The official [DGE circular Y1/16807/2023](https://education.kerala.gov.in/wp-content/uploads/2023/10/sastholsavam10102023.pdf), printed **4 October 2023**, supplies a dated 2023–24 grading table at PDF/printed page 2: A at 80% or above gives five points, B at 70–79% gives three, and C at 60–69% gives one. The website post and filename carry 10 October; these dates remain distinct. This grade table provides period-specific scoring context, without explaining the publication changes or certifying a championship. Source `012`; the cited header/grading pages were checked visually.

## Remaining reconciliation work

A bounded search covered DGE publications and public post metadata, KITE result endpoints, PRD/Keralanews material, official-source links advertised by teacher indexes, and selected Internet Archive captures. It did not recover a signed final consolidated statement or a correction order naming these changed overall totals. The 2023 and 2024 guidance bodies are not championship certificates, and later appeal instructions cannot be retroactively assigned as the cause.

Preserve all dated versions. The next decisive record would identify the applicable contests/categories, accepted appeals, championship point rules, exact revision and authorised final district/school statement. Until then, an answer should name its source and publication observation rather than silently replace a closing result with the current portal table.
