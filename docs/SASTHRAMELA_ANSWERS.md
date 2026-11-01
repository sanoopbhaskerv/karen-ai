# Sasthramela research answers

Karen connects the checked bilingual facts, original source register and ten collected KITE overall tables to text and voice answers. A bilingual concept layer handles history, prize scope, projects, preparation and 2026 registration. It matches concept groups and common language variants, rather than exact question strings. Bounded lexical retrieval remains available for other exhibition questions. General science conversation continues through the configured provider.

The runtime reads `sasthramela_topics.json`, `knowledge.jsonl`, `sources.json` and the structured result/catalogue/selection registers. It never reads the acceptance questions or held-out Malayalam evaluation file. No new API credentials, embeddings or fine-tuning are required. Dates, event/section boundaries, source-specific credits, archive conflicts and unknowns remain explicit.

## Covered acceptance set

`tests/sasthramela_acceptance.json` contains the user's 40 questions, an independently phrased English version and a Malayalam version for each. Automated checks verify the selected topic, substantive answer details and resolved sources for all 120 phrasings. Forty further interface checks exercise each original through both text and voice without model generation. Registration tests cover categories/classes, codes, school login, progression, contributions, appeals, documents, themes, dates/venues, planning deadlines, current manual and grace-mark cycle boundaries.

Coverage includes early Chittur/Alwaye evidence and unknown statewide inauguration; 2009 integration and early IT; 2012 editions and 2015 venues; pandemic and catalogue changes; school/district standings, archive conflicts, 2017/18 streams and 2025 Robotics; named project mechanisms and award scopes; Working Model team, video, scoring, dimensions, charts, onsite-event distinctions, Arduino classification, internet and local confirmation.

## Sources and voice

Text answers return original source links, preserved on refresh. Source metadata is captured with the answer once per request, avoiding a second lookup against changed shared history. Voice can use a shorter source-bound summary for long lists or overviews while retaining the same values and caveats. `X-Karen-Research-Topic` identifies the route for an individual voice request, allowing live verification without relying on mutable shared conversation. The dashboard preserves citations for full and spoken forms. Privacy filtering still runs before speech and history storage. The WAV-in/MP3-out board protocol is unchanged.

## Evidence boundaries

The cutoff is 1 November 2026. The collection is not a live rules feed or complete year-by-year individual winner roster. Earlier overall tables have documented conflicts; displayed order does not establish a certified final rank. Selection is not a prize, state-category awards are not overall awards, and written project descriptions do not establish independent performance or safety. Teacher review of draft Malayalam translations remains pending.

The 2026 portal links the revised 2025 manual. Action-plan dates remain historical planned milestones, not current local registration deadlines. School entries, final local reporting arrangements, internet/cloud permission, power and additional documents still need applicable organiser instructions. Unsupported years, categories and named-school rank queries are not silently filled from another table.

The request cache retains ten-minute replay for up to 256 results, with one running worker and no unbounded queue. At the existing 512,000-byte voice-result cap, cached MP3 payloads are bounded to roughly 128 MB. A regression sends 80 quick research questions and retrieves the first result without another provider call.
