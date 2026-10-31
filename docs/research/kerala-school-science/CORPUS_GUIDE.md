# Using the exhibition research with Karen

This collection supplies evidence for answers, rather than a model trained to remember every result. A future integration should preserve source, event year, competition level, fair and item. The current research does not modify Karen's saved memory or provider request.

## Files and provenance

The topic guides are readable research summaries. The JSON catalogues contain source-backed factual rows, the project index records selected exhibit provenance, and the result snapshots preserve observed overall score tables. `knowledge.jsonl` contains concise claims with stable source identifiers and validity notes; `sources.json` resolves those identifiers to the official or historical source. The topic-specific source registers retain notes about acquisition and reliability. The national discovery index supplies 105 title/code/school/page records; the case index supplies selected method explanations, including eleven extended edited write-ups. A separate 31-entry SISF 2026 method collection preserves pupil/teacher categories and source-specific credit versions. These collections overlap and serve different evidence purposes.

Each source has an access date. Where known, a separate document date is retained. A URL containing 2026 is not sufficient evidence that the linked document was written in 2026: the portal currently serves a 2025 competition manual and a software guide bearing a 2022–23 filename. Likewise, a press page's upload date can differ from the event and the release's internal date.

The catalogue snapshots record literal item names, section labels and codes. They expand ditto marks but do not infer eligibility, change official spellings, or turn teacher categories into student categories. Separate special-school catalogue records are not merged with general fair items.

Karen's exhibition identity is anonymous at the user's request. Exclude its pupils' personal biography, school identity, class section, home details and registration documents from future assistant context or training examples. The preparation guide and class-group evaluation question use generic descriptions for that reason. Organiser-facing registration and genuine participation evidence remain separate from the assistant's public answers.

Historical source credits identify the authors of those exhibits; they must not be presented as Karen's creators. Keep their attribution and source context when discussing the published historical work, without importing unrelated personal or contact information.

## Suggested answer process

1. Identify the requested edition, level, fair and item. Ask for a missing distinction when it changes the answer: Science Working Model and IT contests have different formats.
2. Retrieve a small number of directly relevant claims and their source passages. Current signed circulars and the applicable manual take priority for current rules.
3. State the answer in natural Malayalam at a level a pupil can explain. Preserve a source link in a text interface even if a spoken answer only names the authority and year.
4. If sources disagree, identify the disagreement or give a source-specific answer. Do not manufacture a reconciliation or present an old rule as current.
5. If evidence is absent, say what is unknown and which document could establish it. A model's own plausible historical recollection should not fill an empty archive entry.

These are proposed integration behaviours. No retrieval service, embedding index or provider API has been built or invoked for this research.

## Rules for edition and programme boundaries

| Potential error | Correct handling |
| --- | --- |
| UP item appears at a state-portal URL | Check manual eligibility and whether the row is a teacher item. The master catalogue is generic. |
| A source says one school entry | Distinguish exhibits/teams from pupils in each exhibit. Science HS Working Model specifies two pupils, also recorded in the older 2019 manual. |
| Electronics/IoT/Robotics must be assembled in three hours | Apply that circular to those items. Do not transfer it to prepared Working Model without a rule extending it. |
| NCERT selected an exhibit | Say selected for that edition, not national prizewinner or scientifically validated technology. |
| An old total is much higher than a recent total | Preserve scoring units and scope; do not compare totals across undocumented scoring systems. |
| A school-table sum differs from the district-table sum | Preserve each fetched view and its scope. An internally correct row total does not resolve cross-table differences. |
| An older INSPIRE FAQ gives a different quota | Use the dated 2026–27 notification for that cycle, retaining any live-page condition that needs separate authority. |
| An organiser list and a participant form give different credits | Retrieve all linked credit versions, name the source when answering, and keep attendance/work division unresolved. Do not union names into a claimed team. |
| A state committee must arrange venue internet/power | Keep the stated state-organising scope; do not promise subdistrict credentials, five sockets per exhibit, or cloud-API permission. |
| A state winner can reach SISF/NCERT | Explain selection and invitation conditions. Do not promise automatic entry for every state item. |
| A 2025–26 grace-mark circular is available | Label that exam cycle. It does not prove a 2026–27 entitlement. |
| A school used a cloud AI service | Explain the documented dependency. It does not mean the student trained the foundation model or that the full system runs on the microcontroller. |
| A report documents a regional fair before 1965 | Describe its place, date and regional scope. It does not establish the statewide series' inaugural year or continuity. |
| Kochi appears in NCERT's 1991 host table | Identify the national exhibition series; do not relabel it as Kerala's first state fair. |
| A model report proposes automatic control or a full-scale plant | Separate described construction from proposed applications and measured results. Publication does not validate every scientific claim. |
| A source prints unexplained output units | Retain the source wording and uncertainty; do not invent a correction or relabel it as a validated performance result. |
| The national editions are labelled 2020 and 2021 | Retain their actual combined virtual-event dates in February 2022; do not infer Kerala state-festival activity from them. |

## Review before any fine-tuning

`evaluation-ml.jsonl` is a small human-review set for factual and evidence-handling behaviour. It includes ambiguous questions, unavailable history, category confusion, historical result conflicts and time-dependent rules. It is deliberately not formatted as a provider-specific training file.

Before using any future training set, independently review the Malayalam, source match, applicability and expected answer. Keep evaluation questions out of training examples. Store a source-aware answer rather than an unsupported date, winner or project claim. Use event-specific reports and organisers' written responses as new evidence only after establishing their provenance.

## Adding records

Add a source entry with a stable ID, title, exact URL, publisher/authority, access date, document date when established and a scope note. For a manual, include the printed page and PDF page because they differ. Then add a concise factual claim with source references and an event or rules-version boundary.

For a result, retain academic year, calendar dates, fair, item, section, level, place, grade, score type and status where supplied. Keep a correction as another dated record with an explicit relationship to the earlier one; do not silently overwrite history. For a project, distinguish its title, proposed mechanism, measured results, selection and prize status.

The most valuable next additions are original project reports/logbooks, certified historical result books, annual souvenirs and a redacted entry confirmation containing only the competition fields needed to resolve eligibility. These provide evidence that a list of search links cannot supply.

## Media, live status and planning dates

The media index links each SISF write-up to a public DIKSHA unit and records resource/header access separately from sampled frames. Twenty-one MP4s are linked and sampled through 137 frames. No full continuous playback or audio listening review has been completed; machine processing is a separate evidence layer. Ten teacher units currently have no playable child. Neither access nor empty linkage establishes performance, authorship or absence of recordings elsewhere. A misleading artifact filename must be checked against returned titles and actual media.

The 2026 district dataset is a timed snapshot, with source dashes and arithmetic discrepancies retained. Generic status totals are not eligibility counts; partial champion panels are not final results, and a grade-only row is not a prize rank. The calendar index records planned Science milestones from a mirrored attachment, including literal before-date relations. It must not supply a local check-in time or certify that an event occurred. See [MEDIA.md](MEDIA.md), [DISTRICT_STATUS.md](DISTRICT_STATUS.md) and [CALENDAR_2026.md](CALENDAR_2026.md).


## New source versions, papers and audio drafts

The expanded national index covers 2023–2025: 14 selected rows, 20 separate forms and six versioned findings. The 2025 school/name disagreements remain attached to their documents. The [historical stream snapshots](historical-stream-results.json) are separate from whole-festival tables; blank section cells, stale page titles and different capture times remain explicit.

Four [publication candidates](SCHOOL_PROJECT_REPORTS.md) add component methods, rather than verified exhibit identities or replication. Preserve each paper’s credit/affiliation/date and its reported data problems. Neither publication nor a matching numerical range certifies the complete exhibit or its January version. Use the [additional 2026 circular](ADDITIONAL_2026_CIRCULARS.md) to qualify the original Mathematics dates without changing Science instructions.

The [audio-processing index](media-audio-review.json) records 21 machine outputs from complete extracted audio. Two repetitive outputs are rejected; the other 19 are unverified drafts. There have been zero listening reviews and zero continuous video reviews, despite 137 inspected frames. Do not use ASR names to change credits or import draft speech as scientific fact, quotations, approved answers or training examples. No knowledge fact is based solely on these outputs.


## Capture-specific result evidence and dated item directions

The result-version register groups captures of the same original endpoint. Its top URL can represent only one observation. For a dated claim, use the matching acquisition’s actual effective URL/Memento-Datetime; the new historical knowledge records provide `capture_urls` for this purpose. Preserve the difference between a complete table and a landing top-five list. The 17 captured pages contain repeated observations and do not establish exact revision dates, correction authority or signed finality. Do not replace all old statements with the current table.

The [club-governance circulars](CLUB_GOVERNANCE.md) direct elections and reporting. Terms/targets do not prove the elections occurred or name current appointees. June 15 is the 2026 subdistrict election target from a school-office-bearers’ general body, not an asserted school-election deadline. The [IT Quiz schedule](ADDITIONAL_2026_CIRCULARS.md#it-quiz-original-schedule-and-later-subdistrict-amendment) distinguishes its 9-to-10 September amendment from Mathematics’ 19-to-23 September change. Presentation-format questions do not imply portal conduct.

The [2024 Science circular](HISTORICAL_SCIENCE_CIRCULARS.md) attaches its AI-assisted-website restriction to C. V. Raman essay reference directions. It does not decide a 2026 Working Model cloud-AI rule. Preserve its conflicting November dates and keep the Mathematics/Social Science formats on later pages out of Science requirements. Early national counts of unnamed states and combined teacher-training totals do not establish Kerala’s inaugural year or a Kerala-only headcount.
