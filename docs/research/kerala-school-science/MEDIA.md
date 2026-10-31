# Public project media linked from SISF 2026

Checked **1 November 2026**. All **31 Kerala project QR references** in SCERT Telangana's official compendium decode and resolve to matching public DIKSHA units. **21 units expose an MP4 resource**: all 14 individual and seven group write-ups. The ten teacher units currently return no playable child. Every returned MP4 artifact answered HTTP HEAD with **200 and video/mp4**.

These findings concern published media availability. They do not establish a complete delegation, award, qualifying state item/rank, independent performance or a pupil's contribution to building/coding. Existing source-specific school and pupil/guide credits remain in the [model index](sisf-2026-models.json) and [project collection](PROJECTS.md).

The [31-entry media index](project-media-index.json) records exact source pages, decoded URLs, DIKSHA unit/resource IDs, artifact URLs and review scope. The [media source register](media-sources.json) records request provenance and hashes. No source clips, frames, pupil photographs or contact fields are included in this repository.

## What was inspected

1. Decoded one QR URL from each credited Kerala write-up start using native macOS Vision. QR provenance is the [official compendium](https://www.scert.telangana.gov.in/Pdf/publication/SouthernIndiasciencefair2026-ExhibitsCompendium.pdf), source `pathways-37`, PDF pages 195–247; each individual start/page is retained in the index.
2. Followed all 31 public DIKSHA links. They redirect to `/get/dial/{code}?source=scan` and return a common client-side application shell. That HTML alone does not establish the linked project contents.
3. Read the portal's publicly served frontend source, which identifies its guest DIAL lookup and public collection-hierarchy requests. Ordinary unauthenticated requests returned OK for all 31 units. This produced 21 linked `video/mp4` children and ten named units with no playable child in the received hierarchy.
4. Checked the 21 artifact URLs with HTTP HEAD. Sampled video frames from the four award-linked projects, plus SAMARTH to resolve a misleading artifact filename. **Five videos were sampled visually; zero full clips or audio tracks were reviewed.** The other 16 returned videos have metadata/header checks only.

No report or code-repository links were found in the returned unit/resource descriptions, bodies or titles. This is a finding about these QR-linked records, not a search of every possible school or project website. A public unit without a playable child does not prove that no recording exists elsewhere or was ever made.

## Four award-linked videos: precise review limits

| Project / QR link | Native duration | Visual sampling | What the samples support |
| --- | --- | --- | --- |
| [Driving simulator — M8P5L1](https://diksha.gov.in/dial/M8P5L1) | 111.84 s | 12 frames, including a one-second sequence at 55–60 s | Physical steering/pedal/gear controls are handled while the simulator display changes. This is visual demonstration evidence; input/output timing and training effectiveness remain unverified. |
| [Medication management / Medibot — W8T8B8](https://diksha.gov.in/dial/W8T8B8) | 87.68 s | 14 frames, including the interface/output area at 66–86.48 s | Schedule editing, enclosure and output-chute views are visible. Automatic medicine release and correct dose delivery were not resolved in these samples; their absence from the full clip is not established. |
| [Natural-fibre diaper — D8B6U6](https://diksha.gov.in/dial/D8B6U6) | 70.32 s | Six frames at 0, 10, 23.40, 35.12, 46.84 and 67.28 s | Fibre-treatment beakers, raw/processed materials and product/fabric handling are visible. These samples do not establish a measured absorbency comparison or production/test procedure. **KL-G-06 was not confidently readable**; the existing award correspondence remains a candidate. |
| [Fog harvesting — K3J4B4](https://diksha.gov.in/dial/K3J4B4) | 150.56 s | Six frames, including collector close-ups at 50.16, 75.28 and 100.36 s | Mist is visibly present near the mesh/collector. Ionisation, collected yield, water quality and controlled comparisons remain unverified. |

Frame timestamps and observations are recorded in each resource's `review` object. Sampled frames do not provide continuous playback, audio/transcription, a complete demonstration audit or independent certification. Source publication timestamps are kept as metadata and are not treated as verified recording dates.

The four video links do not resolve differing pupil/guide spellings between the compendium and VITM's award list. Preserve the [source-specific correspondence notes](SISF_2026_MODELS.md) and the original credit versions.

## All 31 QR references

“MP4 available” below means the public hierarchy exposes one Live MP4 and its artifact responded 200/video-mp4; it does not mean the clip was watched. “No playable child” means the named unit resolves but the returned hierarchy exposes none on this access date.

| Category | Compendium title | Printed / PDF start | Decoded DIKSHA link | Observed result |
| --- | --- | --- | --- | --- |
| individual | INVESTIGATORY PROJECT ON PALM FIBER | 156 / 195 | [P3Y7R6](https://diksha.gov.in/dial/P3Y7R6) | MP4 available; metadata only |
| individual | PRISMATIC PILLAR | 159 / 198 | [I3I4B8](https://diksha.gov.in/dial/I3I4B8) | MP4 available; metadata only |
| individual | AGRICULTURE VEHICLE | 161 / 200 | [C3W9Q2](https://diksha.gov.in/dial/C3W9Q2) | MP4 available; metadata only |
| individual | MATHS SCRAP BOOK | 162 / 201 | [Q7P4E9](https://diksha.gov.in/dial/Q7P4E9) | MP4 available; metadata only |
| individual | RIVER CLEANING SYSTEM | 163 / 202 | [S1J4M9](https://diksha.gov.in/dial/S1J4M9) | MP4 available; metadata only |
| individual | HOPE (Hardware Optimized for People in Emergency) | 164 / 203 | [X2X1V7](https://diksha.gov.in/dial/X2X1V7) | MP4 available; metadata only |
| individual | AGROLINK – AUTOMATIC SMART AGRI SYSTEM | 165 / 204 | [U1M5L8](https://diksha.gov.in/dial/U1M5L8) | MP4 available; metadata only |
| individual | AREA OF TANGENTIAL POLYGON | 166 / 205 | [B4U3I2](https://diksha.gov.in/dial/B4U3I2) | MP4 available; metadata only |
| individual | LOW-COST DRIVING SIMULATOR FOR SAFE DRIVING TRAINING | 168 / 207 | [M8P5L1](https://diksha.gov.in/dial/M8P5L1) | MP4 available; frames sampled |
| individual | Li-Fi Based Wireless Data Communication System Using Visible Light | 170 / 209 | [J7E9C2](https://diksha.gov.in/dial/J7E9C2) | MP4 available; metadata only |
| individual | SAMARTH KERALA | 172 / 211 | [H7B8D3](https://diksha.gov.in/dial/H7B8D3) | MP4 available; frames sampled |
| individual | VALUE ADDED PRODUCTS FROM BANANA PSEUDO STEM(BPS) | 174 / 213 | [B6V4X5](https://diksha.gov.in/dial/B6V4X5) | MP4 available; metadata only |
| individual | AN INTELLIGENT AUTOMATED IOT-BASED MEDICATION MANAGEMENT AND DISPENSING SYSTEM | 176 / 215 | [W8T8B8](https://diksha.gov.in/dial/W8T8B8) | MP4 available; frames sampled |
| individual | SMART WHEELCHAIR FOR HANDICAPPED PEOPLE | 178 / 217 | [Z3P3B7](https://diksha.gov.in/dial/Z3P3B7) | MP4 available; metadata only |
| group | Exploring the Agricultural Potential of Invasive Plant Species | 180 / 221 | [X3L2C8](https://diksha.gov.in/dial/X3L2C8) | MP4 available; metadata only |
| group | SUSTAINABLE AND ECO FRIENDLY DIAPER PRODUCTION FROM NATURAL FIBRES OF BANANA AND BAMBOO | 182 / 223 | [D8B6U6](https://diksha.gov.in/dial/D8B6U6) | MP4 available; frames sampled |
| group | WATER ON EARTH | 183 / 224 | [Q4X1J2](https://diksha.gov.in/dial/Q4X1J2) | MP4 available; metadata only |
| group | NEWTON’S LAW OF MOTION | 184 / 225 | [R3Z7R2](https://diksha.gov.in/dial/R3Z7R2) | MP4 available; metadata only |
| group | IONISATION BASED FOG HARVESTING SYSTEM | 185 / 226 | [K3J4B4](https://diksha.gov.in/dial/K3J4B4) | MP4 available; frames sampled |
| group | FROM POLLUTIONS TO INNOVATIONS | 187 / 228 | [D9N7S8](https://diksha.gov.in/dial/D9N7S8) | MP4 available; metadata only |
| group | MAGNETISM | 189 / 230 | [W6Q5X2](https://diksha.gov.in/dial/W6Q5X2) | MP4 available; metadata only |
| teacher | EARTH MOVEMENT | 192 / 235 | [Q6A2H4](https://diksha.gov.in/dial/Q6A2H4) | No playable child |
| teacher | The Impact of Three-Dimensional Manipulatives on Spatial Reasoning: Solving the Square Pyramid Challenge. | 193 / 236 | [T5F9N3](https://diksha.gov.in/dial/T5F9N3) | No playable child |
| teacher | SOUND WAVES AND FREQUENCY | 194 / 237 | [E4G1T8](https://diksha.gov.in/dial/E4G1T8) | No playable child |
| teacher | THE RAINBOW UNFOLD | 195 / 238 | [H3L8Z7](https://diksha.gov.in/dial/H3L8Z7) | No playable child |
| teacher | HYDRO-SEASONAL INFLUENCE ON MICROPLASTICS DYNAMICS: A COMPARATIVE EVALUATION OF SURFACE WATERS IN THE ALAPPUZHA - CHANGANACHERRY CANAL (AC CANAL) | 197 / 240 | [Y6T6W1](https://diksha.gov.in/dial/Y6T6W1) | No playable child |
| teacher | WONDERS OF WORLD-EYE AND VISION | 199 / 242 | [H4Y9X9](https://diksha.gov.in/dial/H4Y9X9) | No playable child |
| teacher | LEARNING AID BASED ON THE UNIT ‘ATMOSPHERIC CONDITIONS AND CLIMATE’ | 201 / 244 | [U1K4M5](https://diksha.gov.in/dial/U1K4M5) | No playable child |
| teacher | Tabacco and Neem : A Promising Approach to Manage Giant African land Snail | 202 / 245 | [Q7M3F6](https://diksha.gov.in/dial/Q7M3F6) | No playable child |
| teacher | E. COLI AND PROTOZOA – INDICATOR A BRAIN EATING AMOEBA | 203 / 246 | [Z2Y1V3](https://diksha.gov.in/dial/Z2Y1V3) | No playable child |
| teacher | TRIGONOMETRY IN PRACTICAL SITUATIONS | 204 / 247 | [G5W3Q9](https://diksha.gov.in/dial/G5W3Q9) | No playable child |

## Source anomalies and use in Karen

The SAMARTH unit H7B8D3 returns resource title `KERALA_INDIVIDUAL Exhibit_Project Samarth`, while its artifact filename is `an-intelligent-mwdication-management-.mp4`. Three sampled frames at 0, 20 and 60.12 seconds show SAMARTH signage/interfaces; the 0-second wall placard reads **KL-I-11**. The actual URL is preserved. A filename alone is insufficient to identify a project's subject.

The returned unit titles for Newton's law and Atmospheric Conditions and Climate contain malformed punctuation. Their API versions remain separate from the compendium titles; the index does not silently overwrite either source.

For Karen, retain the link and access/review status as evidence pointers. Use reviewed write-ups for method summaries; use these sampled observations only for the specific visible actions described above. Do not turn a published video into an automatic claim of scientific accuracy, reliability, authorship, attendance or a prize. The [methods guide](MODEL_REPORTS.md) and [SISF 2026 guide](SISF_2026_MODELS.md) keep those evidence types separate.
