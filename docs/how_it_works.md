# How the AI Discovery Engine Works

## 5-Line Executive Summary
1. **Unsupervised Public Ingestion:** Ingests 174,000+ public reviews and support discussions from Google Play Store, Apple App Store, and Google Photos Help Community across key English-speaking markets.
2. **High-Recall Prefiltering:** Applies a 35+ retrieval seed keyword filter to discard generic cloud storage, billing, and backup complaints, isolating 35,210 retrieval candidates.
3. **Structured Schema Extraction:** Employs LLM batch extraction with strict JSON-schema enforcement to extract photo types, remembered cues, forgotten clues, query formulation patterns, and verbatim evidence quotes.
4. **Opportunity Score Ranking:** Groups problems into 14 distinct taxonomy clusters, ranking each by a mathematical Opportunity Score ($\text{Frequency Share} \times \frac{\text{Severity}}{3} \times \text{Unresolved Factor} \times \text{Recency Weight} \times 400$).
5. **Instant Precomputed Serving:** Serves all insights and an AI conversational assistant via Next.js and in-memory static aggregations with sub-2-second latency and zero live scraping dependencies.

---

## Architecture Flowchart

```mermaid
graph TD
    A[Public Data Sources<br/>Google Play 168k | App Store 5k | Community 51 | Reddit via Apify] --> B[Phase 1 & 2: Cleaning & Regex Prefilter<br/>35+ Retrieval Seed Keywords]
    B --> C[35,210 Candidate Pool]
    C --> D[Phase 3: Schema Extraction & Code Verification<br/>Gemini 2.5 Flash + Exact Substring Match]
    D --> E[4,615 High-Signal Core Cases<br/>Photo Types | Clues Remembered vs Forgotten | Failure Stages]
    E --> F[Phase 4: Clustering & Opportunity Scoring<br/>14 Opportunity Areas Ranked by Score]
    F --> G[Precomputed Static JSON Indices<br/>In-Memory UI Data Store]
    G --> H[Web Application<br/>Next.js 16 App Router]
    H --> I[Ask Assistant with SSE Streaming]
    H --> J[Opportunity Map & Side-by-Side Comparison]
    H --> K[Interactive Evidence Browser]
    H --> L[Trust & Quality Audit Gate]
```

---

## Key Safety & Performance Safeguards

- **Prompt-Injection Defense:** Untrusted user review text is strictly demarcated within XML blocks. The extraction model is instruction-isolated, and quotes are programmatically verified against the original text using exact substring matching in Python.
- **PII Anonymization:** Author names, usernames, and identifiers are stripped or hashed before indexing.
- **Latency Guarantee:** Request paths perform zero batch LLM calls or web scraping; all data is pre-materialized in JSON bundles for sub-1.5s client response times.
