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

The [historical appeal/Work Experience supplement](HISTORICAL_OPERATIONS.md) separates advancing-entry capacity from pupils within a group exhibit. Its Work Experience Innovative Working Model permission for a needed mobile/laptop explanation requires both judge and invigilator permission, alongside that circular's general mobile/smartwatch restriction. It does not authorise Science Working Model cloud access. The [12 October 2023 amendment](HISTORICAL_SCIENCE_CIRCULARS.md#official-amendment-12-october-2023) changes that year's IT Quiz dates and cancels a specified Mathematics question instruction; it is not a current schedule or Science Talent Search cancellation.

Use the [pandemic sources](PANDEMIC_ACTIVITIES.md) to distinguish DGE-reported departmental non-conduct from separate online Shasthrarangam/NCSC plans. Preserve unresolved deadline/year anomalies and planned status. A historical no-grace decision is not a current entitlement rule; an online programme direction is not evidence of a completed virtual state fair.

The [early IT circulars](HISTORY_2000S.md) retain issue dates separately from archive captures and planned events. Their hardware/software demonstration clause is historical, rather than present category permission. The [publisher-library bibliography](MODEL_REPORTS.md#publisher-library-references-for-physical-follow-up) gives seven reference entries without new book bodies or Kerala method cases. Preserve its title/imprint ambiguity. The [March 2026 government order](RULES.md#examination-grace-marks-are-separate-from-fair-points) supplies an attributed Skill Festival naming account; its sports window and the implementation circular’s named removed-item exception must not be transferred to general Science rules.

## Technical-school, observer and earlier result evidence

Tag the [Technical High School fair](TECHNICAL_SCHOOL_FAIR.md) as a separate programme before answering an eligibility, size, duration, rubric or funding question. Its 2017 history does not date General Education Sasthrolsavam; its 2023 cover, 2024 approval and separate 2025 amendment are different source dates. The served base is not a fully consolidated amended text. Preserve the detailed/appendix rubric disagreements, and distinguish a planned programme or conditional funding permission from actual attendance and spending.

The [2019 observer article](OBSERVER_ACCOUNTS.md) supports attributed commentary for that edition. It does not supply an experimental design, measured learning outcomes, a statewide prevalence estimate or a government rule. Retain this source genre when summarising its observations.

The [archived IT event-site records](HISTORY_2000S.md) distinguish announced dates, received HTML captions and January 2008 captures. Their six tables contain 230 numbered publication entries, including a teacher table with absent/NIL wording. Do not convert these into unique pupil attendance, overall champions or a complete annual Science Fair history. The new Malayalam questions test these distinctions and remain held out from any future training data.

The new technical-school orders distinguish a first academic cycle, authorised spending, conditional ratification, retrospective event references and upload/signing dates. A larger parent allocation is not the fair budget, and a required bank-account action is not proof it was fulfilled. The [undated portal map/form](ACCESS.md#map-and-blank-form-served-under-the-2026-portal) likewise does not acquire current-rule authority from a 2026 URL or HTML title.

For the [IRIS/ISEF fish case](PROJECTS.md), retain the explicit NCSC shortlist label, matching 2024 organiser records, different credit formatting and missing NCSC-edition/prize evidence. Its abstract reports a comparison and system design, without raw data or independent validation. The [KFRI annual-report entries](PATHWAYS.md#ncsc-research-and-completed-training-records) are different evidence: an ongoing assessment-project listing and reported training completions do not supply that assessment's findings, pupil counts or causal learning effects.

The [IRIS / ISEF research route](IRIS_ISEF.md) adds public pages with mixed edition labels and internal/cross-page timetable conflicts. Keep the closed-window observation dated. IRIS's 90-second video and material-anonymity rules differ from Kerala Working Model. ISEF's own grade/age/team and generative-AI authorship/disclosure provisions require their programme/year tags; they do not establish a Kerala subdistrict AI or uniform ban. The expressly illustrative sample paper supplies no actual pupil measurements and is not a new exhibit case.

For the two earlier ISEF abstracts, distinguish reported mechanism/measurements from validation. Electrical-protection claims are not a safety certification; the membrane abstract's proposed filler/application is not a measured separation result. Blank award fields do not certify prizes or no-prize outcomes. A current district school-location record is not a recovered 2021 finalist directory; a 2022 directory's Virtual label is not proof of physical attendance.

The [dated common identity form](ACCESS.md#special-school-work-experience-fair) supplies printed 2026–27 details and edition labels, not accepted registration, final venues or a dated special-school governing manual. A library's [NCSC compilation holding](PATHWAYS.md) is a bibliographic lead, not recovered abstract contents, current shelf availability or an event date inferred from publication year.


The [project follow-up](PROJECTS.md) preserves an earlier SPARK selection with different Raksha school/guide credits, limited CUSAT context for the taro pair and a separate official ISEF category-award result. Retrieve the award source when answering prize questions: the taro category award is now established even though its received abstract field remains blank. Do not transfer an earlier guide to 2021, read list position as prize rank, infer work division from laboratory affiliation, or call a category award overall second place/per-pupil payment.

The [SISF annual reports](SISF_HISTORY.md) retain report cycles, website index dates, event dates and narrative labels separately. Their five event records and two non-conduct paragraphs are seven report observations, not seven completed editions. Literal school/student/project/visitor populations and contradictory labels are not reconciled into unique people or Kerala-only counts. Institutional pandemic paragraphs do not replace Kerala state-series orders.

The special-school scan's [full review](ACCESS.md#special-school-work-experience-fair) dates a cited 2006 reference, not the manual. Referenced forms absent from this received body do not prove omission from the complete original. The new [Education report holding](HISTORY.md) similarly supplies registered 1967–68/1970 bibliography, not original pages, a current barcode or state-fair inauguration.

The [IT@School retrospective](HISTORY_2000S.md#government-retrospective-it-fairs-in-200204) attributes first/second IT fairs to its 2002/2003 headings and records Kottayam under 2004 without a third-edition label. Keep these stream-specific claims separate from the Science Fair's origin and the document's unknown issue date.

Use the [INSPIRE compendia](INSPIRE_MODELS.md) with edition and state/organisation tags. An Awardee label, a selected cohort and a described mechanism do not establish a final rank, attendance, Sasthrolsavam route or engineering validation. The later October deadline announcement is separate from its unchanged July PDF; the twelfth event's earlier financial-year cohorts are separate from current nominations. The [older model-book holdings](MODEL_REPORTS.md#five-institutional-catalogue-targets-for-older-volumes) add exact library targets, without recovered books or new Kerala method cases.


The [2015 programme](HISTORICAL_EDITIONS.md#the-recovered-2015-kollam-programme) and [2014 trophy-design invitation](HISTORY.md#a-gold-cup-design-invitation-in-2014) establish historical plans, not completed events or awards. Keep Science/IT ordinals, detailed programme times and cultural performances separate. For the eighth INSPIRE edition, source-specific FY2019–20 and September 2021 reports supply chronology outside the undated compendium frontmatter; serial rows do not replace explicit prize positions. A different pupil’s kitchen-machine prize cannot be transferred by topic similarity.

The [combined NCERT booklet](DISCOVERY.md) contains parallel Hindi/English synopses: its 145 credit blocks are not 290 different exhibits or an attendance count. No confident Kerala address in that bounded review does not establish nonparticipation. Preserve the later first-person lifting-device account as a candidate correspondence outside the original entry. A published personal narrative, natural-origin claim or short mechanism is not independent identity, work-division, effectiveness or safety validation.

The [gold-cup administrative chain](HISTORY.md#contribution-permission-procedures-and-the-2015-naming-decision) adds contribution permission, planned remittance, a blank form and a naming order. Preserve reproduction provenance, printed dates and archive captures; none is a receipt, manufactured-cup certificate or current fee instruction. The [specific 2024 funding rejection](HISTORICAL_OPERATIONS.md#a-specific-district-funding-request-rejected-in-2024) must not become an approved grant, a general funding ban or a reason copied from a neighbouring item.

The [post-fair camp report](PATHWAYS.md#a-separately-reported-post-fair-camp) is institutional participation/activity reporting, without measured or causal learning results. A separate personal proposal in the [observer guide](OBSERVER_ACCOUNTS.md) has no official scoring authority. Retain these source genres when answering questions about implementation and educational effects.

The [ninth INSPIRE descriptions and dated reports](INSPIRE_MODELS.md#ninth-nlepc-eleven-kerala-heading-descriptions-and-a-separate-kv-entry) separate eleven Kerala-heading entries from one KV entry, compendium preface/cover dates from event reporting, and support identification from individual payment. Do not convert a planned awards venue into confirmed conduct, a source's year wording into an explicit financial year, or “Start-Ups” into legally incorporated companies. The [provider EOI](PATHWAYS.md#a-historical-mobile-science-provider-proposal) has its own applicant criteria and scoring, separate from pupils' model rules.
