# Video samples and machine audio drafts

Checked **1 November 2026**. All **21 publicly linked MP4s** were downloaded and matched the earlier artifact byte counts. Their hashes are retained in the [audio-processing index](media-audio-review.json) and [media sources](media-sources.json). One interrupted download was completed with a normal HTTP 206 Range resume; its initial partial acquisition and resumed request remain explicit. No raw clips, audio, frames, full transcripts or model weights are committed.

The native audio extraction covers **2,829.260375 seconds**, about **47 minutes 9 seconds**, across all 21 clips. Local ASR produced 21 outputs. Text screening rejected **two highly repetitive outputs**; the other **19 remain unverified drafts**. Automatic language labels are model output, not verified spoken-language identifications. **Zero audio listening reviews and zero full continuous video reviews** have been completed.

## Exact review scope

The [media index](project-media-index.json) now contains **146 sampled frames across all 21 accessible videos**: the earlier 41 frames from five clips, 96 from the remaining 16, and nine later chart-focused samples from three existing clips. These show displays, component handling and selected interfaces; they are not continuous operation or independently replicated tests. The four award-linked projects retain their earlier specific review limits.

Machine text was screened for topics and obvious failures. It contains uncertain personal names, school spellings, technical terms, numerical statements and occasional timing artefacts. No credit was changed from ASR. Fluent output does not verify a quotation, scientific explanation, health claim, measurement, pupil contribution or award. No new bilingual knowledge fact is based solely on these outputs.

| QR/source link | Compendium title | Native audio duration | Machine output after text screening |
| --- | --- | ---: | --- |
| [P3Y7R6](https://diksha.gov.in/dial/P3Y7R6) | INVESTIGATORY PROJECT ON PALM FIBER | 133.67 s | Unverified draft; listening needed |
| [I3I4B8](https://diksha.gov.in/dial/I3I4B8) | PRISMATIC PILLAR | 107.32 s | Unverified draft; listening needed |
| [C3W9Q2](https://diksha.gov.in/dial/C3W9Q2) | AGRICULTURE VEHICLE | 93.60 s | Unverified draft; listening needed |
| [Q7P4E9](https://diksha.gov.in/dial/Q7P4E9) | MATHS SCRAP BOOK | 240.87 s | Unverified draft; listening needed |
| [S1J4M9](https://diksha.gov.in/dial/S1J4M9) | RIVER CLEANING SYSTEM | 103.16 s | Rejected: repetitive/degenerate text |
| [X2X1V7](https://diksha.gov.in/dial/X2X1V7) | HOPE (Hardware Optimized for People in Emergency) | 134.27 s | Unverified draft; listening needed |
| [U1M5L8](https://diksha.gov.in/dial/U1M5L8) | AGROLINK – AUTOMATIC SMART AGRI SYSTEM | 213.67 s | Unverified draft; listening needed |
| [B4U3I2](https://diksha.gov.in/dial/B4U3I2) | AREA OF TANGENTIAL POLYGON | 166.56 s | Unverified draft; listening needed |
| [M8P5L1](https://diksha.gov.in/dial/M8P5L1) | LOW-COST DRIVING SIMULATOR FOR SAFE DRIVING TRAINING | 111.84 s | Unverified draft; listening needed |
| [J7E9C2](https://diksha.gov.in/dial/J7E9C2) | Li-Fi Based Wireless Data Communication System Using Visible Light | 283.68 s | Unverified draft; listening needed |
| [H7B8D3](https://diksha.gov.in/dial/H7B8D3) | SAMARTH KERALA | 124.96 s | Unverified draft; listening needed |
| [B6V4X5](https://diksha.gov.in/dial/B6V4X5) | VALUE ADDED PRODUCTS FROM BANANA PSEUDO STEM(BPS) | 152.92 s | Rejected: repetitive/degenerate text |
| [W8T8B8](https://diksha.gov.in/dial/W8T8B8) | AN INTELLIGENT AUTOMATED IOT-BASED MEDICATION MANAGEMENT AND DISPENSING SYSTEM | 87.68 s | Unverified draft; listening needed |
| [Z3P3B7](https://diksha.gov.in/dial/Z3P3B7) | SMART WHEELCHAIR FOR HANDICAPPED PEOPLE | 110.84 s | Unverified draft; listening needed |
| [X3L2C8](https://diksha.gov.in/dial/X3L2C8) | Exploring the Agricultural Potential of Invasive Plant Species | 54.12 s | Unverified draft; listening needed |
| [D8B6U6](https://diksha.gov.in/dial/D8B6U6) | SUSTAINABLE AND ECO FRIENDLY DIAPER PRODUCTION FROM NATURAL FIBRES OF BANANA AND BAMBOO | 70.31 s | Unverified draft; listening needed |
| [Q4X1J2](https://diksha.gov.in/dial/Q4X1J2) | WATER ON EARTH | 89.79 s | Unverified draft; listening needed |
| [R3Z7R2](https://diksha.gov.in/dial/R3Z7R2) | NEWTON’S LAW OF MOTION | 104.68 s | Unverified draft; listening needed |
| [K3J4B4](https://diksha.gov.in/dial/K3J4B4) | IONISATION BASED FOG HARVESTING SYSTEM | 150.56 s | Unverified draft; listening needed |
| [D9N7S8](https://diksha.gov.in/dial/D9N7S8) | FROM POLLUTIONS TO INNOVATIONS | 67.56 s | Unverified draft; listening needed |
| [W6Q5X2](https://diksha.gov.in/dial/W6Q5X2) | MAGNETISM | 227.20 s | Unverified draft; listening needed |

The two rejected outputs correspond to River Cleaning System and Value Added Products from Banana Pseudo Stem. Their returned Hindi/Marathi labels are not evidence of those clips’ actual spoken languages. No factual summary is taken from these failed outputs. The written compendium and separately qualified publications remain available for their methods.

## Method and reproducibility

Audio was decoded with native AVFoundation into mono 16 kHz little-endian float32 PCM. Each stored input has a SHA256 digest, byte/sample count and duration. A separate native probe/decode confirmed all 21 audio tracks and their output format/counts; PCM and video durations differ by less than 0.01 seconds. Fresh decodes were not byte-identical, including some sparse larger sample differences, so only the cached derivatives are identified by their exact hashes. No byte-reproducible derivative or transcript is claimed.

Processing used local `mlx-whisper 0.4.3`, `mlx 0.32.4` and [Whisper small in MLX format](https://huggingface.co/mlx-community/whisper-small-mlx), revision `45f3915923c7a79a5a5b5a7d909d39aeb0e5630e`, temperature 0 and previous-text conditioning disabled. Model-file hashes are retained in the index. The public model was downloaded without account credentials; the audio inference ran locally. This was research processing, without changes to Karen’s runtime or a training job.

Some raw ASR segment times have zero duration or extend beyond native audio; their cause was not independently established. The index counts these cases rather than silently treating every timestamp as a verified source locator. The saved output hashes identify the actual drafts used in screening.

## Next review

Listen to the recordings with a competent language reviewer, compare each proposed quotation and scientific term against the audio, and verify numerical/mathematical/health claims against the written report and relevant evidence. Recover original logs/code and measured results separately. The current machine outputs should not be imported as approved answers or model-training examples.

The later [written-method and chart follow-up](SISF_2026_MODELS.md#a-finite-written-method-and-chart-follow-up) uses published pages and precise stills rather than speech drafts. A local audio-input capability probe exposed no audio to the reviewer; it does not count as listening. The 21 machine outputs, two rejected drafts and all zero-listening/continuous-playback/ASR-fact counters remain unchanged. No further audio conversion, transcription or provider request was made for the written subreviews.
