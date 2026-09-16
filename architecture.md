# AI Discovery Engine — System Architecture

> A natural-language analytics platform that mines public user feedback to uncover **how and why** photo retrieval fails in Google Photos, and surfaces the highest-impact opportunities for improvement.

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Discovery Engine                              │
│                                                                         │
│  ┌──────────┐   ┌───────────┐   ┌────────────┐   ┌──────────────────┐  │
│  │  Collect  │──▶│  Process  │──▶│  Analyse   │──▶│  Serve (Web UI)  │  │
│  │  (Phase 1)│   │ (Phase 2) │   │(Phase 3-4) │   │   (Phase 5-7)    │  │
│  └──────────┘   └───────────┘   └────────────┘   └──────────────────┘  │
│                                                                         │
│  Offline, resumable pipeline ──────────────────▶  Precomputed serving   │
└─────────────────────────────────────────────────────────────────────────┘
```

The system follows a strict **offline-pipeline → precomputed-serving** split. No scraping, LLM calls, or heavy compute happens at request time. Everything the web app needs is materialised ahead of time, ensuring sub-2-second dashboard loads and sub-3-second chat first-token latency.

---

## Phase 0 — Planning & Credential Verification

**Objective:** Validate every external dependency with a single minimal call before committing to the full pipeline.

| Activity | Detail |
|---|---|
| **Credential smoke tests** | Reddit (PRAW read-only), YouTube Data API v3, LLM providers (Gemini / Groq free tier) |
| **Source reachability** | Google Play scraper, App Store RSS/JSON feed, Help Community (Playwright + robots.txt check) |
| **Plan document** | `PLAN.md` — captures confirmed endpoints, rate limits, quotas, fallback strategies |
| **Decision gate** | No further work proceeds until all credentials are live and the plan is reviewed |

### Key Design Decisions

- **Environment variables only** — keys never touch version control (`.env` + server-side env vars).
- **Quota logging** — every API call is counted and checkpointed so runs can safely resume across days (critical for the YouTube 10,000-unit/day budget).

---

## Phase 1 — Data Collection

**Objective:** Assemble a broad raw pool (~20,000–30,000 items) from five authorised public sources.

### 1.1 Source Architecture

```
                     ┌──────────────────────────┐
                     │     Collection Layer      │
                     └──────────────────────────┘
                              │
         ┌────────────┬───────┴────────┬──────────────┐
         ▼            ▼                ▼              ▼
  ┌────────────┐ ┌──────────┐  ┌────────────┐ ┌──────────────┐
  │ Google Play│ │App Store │  │   Reddit   │ │   YouTube    │
  │  Scraper   │ │ RSS/JSON │  │   (PRAW)   │ │ Data API v3  │
  │            │ │  Feed    │  │            │ │              │
  │ python     │ │ iTunes   │  │ r/google-  │ │ search.list  │
  │ google-    │ │ customer │  │ photos +   │ │ + comment-   │
  │ play-      │ │ reviews  │  │ site-wide  │ │ Threads.list │
  │ scraper    │ │          │  │ queries    │ │              │
  └────────────┘ └──────────┘  └────────────┘ └──────────────┘
                                                      │
                                              ┌───────┴───────┐
                                              ▼               ▼
                                       ┌────────────┐ ┌──────────────┐
                                       │ Help       │ │  Checkpoint  │
                                       │ Community  │ │  & Quota     │
                                       │(Playwright)│ │  Tracker     │
                                       └────────────┘ └──────────────┘
```

### 1.2 Collection Strategy Per Source

| Source | Library / Method | Pagination | Rate Limiting | Target |
|---|---|---|---|---|
| **Google Play** | `google-play-scraper` | Continuation tokens, `Sort.NEWEST` | Built-in backoff | ~1,200 core |
| **App Store** | iTunes RSS/JSON feed (`/rss/customerreviews/`) | 10 pages × many country codes | 1 req/s | ~700 core |
| **Reddit** | PRAW (read-only, `.env` credentials) | Multiple queries × sort × time filter | 100 queries/min | ~800 core |
| **YouTube** | Data API v3 (key from `.env`) | ~25 search queries, `commentThreads.list` | ≤ 9,000 units/day, checkpoint | ~300–500 core |
| **Help Community** | Playwright headless | robots.txt-first, 1 req / 2 s | Polite crawl | ~300+ core |

### 1.3 Collection Principles

- **Newest-first** — default 24-month window; extend only if under target.
- **Multi-country** — Play/App Store hit `us, in, gb, ca, au, ie, nz, sg, za` for broader coverage.
- **Rating oversample** — 1–3 ★ reviews carry most failure detail, but 4–5 ★ are kept for "what works" signal.
- **Comment depth** — Reddit comments up to depth 2 (rich workaround data).
- **Resumability** — every collector checkpoints progress to disk so interrupted runs pick up where they left off.
- **Balance constraint** — no single source may exceed 50 % of the final corpus.

### 1.4 Scope & Ethics

- **English-only** by default; Hindi/Hinglish added only if English cannot reach the 3,200-item target.
- **Public data only** — usernames and PII are dropped or hashed at collection time.
- **No fabrication** — if a source fails, the pipeline halts and reports rather than substituting data.
- **Prompt-injection defence** — all scraped text is treated as untrusted; never executed or followed.

---

## Phase 2 — Cleaning & Pre-filtering

**Objective:** Normalise, deduplicate, and cheaply reduce the raw pool before expensive LLM passes.

### 2.1 Normalisation Schema

Every item is mapped to a single unified record:

```json
{
  "id":              "play-us-abc123",
  "source":          "google_play",
  "url":             "https://...",
  "date":            "2025-11-14",
  "rating":          2,
  "platform":        "android",
  "app_version":     "6.74.0",
  "language":        "en",
  "text":            "...",
  "thread_context":  null
}
```

### 2.2 Deduplication

```
Raw items
   │
   ├─ Exact hash dedup (SHA-256 on normalised text)
   │
   └─ Near-duplicate detection (MinHash / Jaccard ≥ 0.85)
          │
          ▼
   Unique items
```

### 2.3 Pre-filter (Keyword / Regex)

A high-recall keyword and regex pass eliminates obviously irrelevant items **before** any LLM call, cutting cost and latency.

**Seed retrieval phrases** (auto-expanded):

> `can't find`, `cannot find`, `search not working`, `search useless`, `find old photo`, `scroll timeline`, `search by date/location/person`, `ask photos`, `gemini`, `natural language search`, `wrong results`, `too many results`, `face group`, `text in photo`, …

### 2.4 Data Funnel

```
Raw (~20-30k)
   │
   ├─ Language filter ─────▶ English-only
   ├─ Exact dedup ─────────▶ Remove duplicates
   ├─ Near-duplicate ──────▶ Remove fuzzy matches
   └─ Keyword pre-filter ──▶ High-recall retrieval subset
                                │
                                ▼
                     Pre-filtered pool (~5-8k estimated)
```

---

## Phase 3 — LLM Extraction & Verification

**Objective:** Classify each pre-filtered item for retrieval relevance and extract a rich structured taxonomy.

### 3.1 Extraction Pipeline

```
Pre-filtered items
       │
       ▼
 ┌─────────────────────────────────────────┐
 │  LLM Batch Extraction (10-20 per call)  │
 │  JSON-schema-constrained output         │
 │                                         │
 │  Model: env-configured (e.g. Gemini)    │
 │  Fallback: secondary provider (Groq)    │
 │  Cache: hash(text + prompt_version)     │
 └─────────────────────────────────────────┘
       │
       ▼
 ┌─────────────────────────────────────────┐
 │  Code-based Verification (no LLM)      │
 │                                         │
 │  • evidence_quote ⊂ original text?     │
 │  • All enums valid?                     │
 │  • Retry once on failure, then drop     │
 └─────────────────────────────────────────┘
       │
       ▼
   Verified core corpus (target ≥ 3,200)
```

### 3.2 Extracted Taxonomy

Each verified item carries:

| Field | Values / Type |
|---|---|
| `relevance` | `core` · `adjacent` · `not_relevant` (+ confidence 0–1) |
| `vague_memory` | `yes` · `no` · `unclear` |
| `photo_type` | screenshot · document/receipt · medical · travel · family/people · pet · food · event · video · old/scanned · other · unknown |
| `clues_remembered` | person · place · event · approx_time · season · object · text_in_image · activity · source/context · visual_appearance · other |
| `clues_forgotten` | exact_date · album · location_name · keywords/filename · device/account · who_is_in_it · other |
| `search_behavior` | typed_keyword · natural_language_query · people_filter · place_filter · date_filter · scroll_timeline · browse_albums · ask_photos_ai · external_workaround · gave_up · other |
| `example_queries` | Exact search strings from the user's own words |
| `failure_stage` | `cannot_express` · `system_misunderstands` · `results_hard_to_evaluate` · `cannot_refine` · `photo_not_indexed_or_missing` · `other` · `none` |
| `failure_detail` | Free text, ≤ 25 words |
| `core_problem` | One-sentence summary (used for clustering) |
| `workaround` | List of workarounds mentioned |
| `outcome` | `found` · `found_after_workaround` · `not_found` · `gave_up` · `unknown` |
| `severity` | 1 (annoyance) · 2 (major friction) · 3 (blocker / abandoned) |
| `regression_claim` | Boolean |
| `ai_feature_mentioned` | ask_photos · gemini · natural_language_search · face_grouping · text_search · location_search · memories · other |
| `evidence_quote` | Exact substring, ≤ 25 words |
| `labeler_confidence` | 0–1 |

### 3.3 Gate: Corpus Size Check

| Condition | Action |
|---|---|
| Core ≥ 3,200 | Proceed to Phase 4 |
| 1,000 ≤ Core < 3,200 | **STOP** — present funnel + options (extend date window, add Hindi/Hinglish, include adjacent items with labelling) |
| Core < 1,000 | **Hard stop** — investigate source failures |

---

## Phase 4 — Aggregation, Clustering & Opportunity Scoring

**Objective:** Derive actionable intelligence from the verified corpus.

### 4.1 Precomputed Aggregates

All analytics are materialised once and served as static JSON:

- Data funnel (raw → pre-filter → LLM-relevant → final)
- Counts per source and per month
- `failure_stage` distribution
- `failure_stage` × `photo_type` cross-tabulation
- Clues remembered vs. forgotten
- Remembered-clue × failure-stage heatmap
- Outcomes and workarounds
- Example user queries
- Regression and AI-feature mention trends
- Cluster summary table

### 4.2 Bottom-Up Theme Discovery

```
core_problem sentences
        │
        ▼
 Sentence embeddings (384–768 dims)
        │
        ▼
 Clustering (HDBSCAN or KMeans, k via silhouette)
        │
        ▼
 LLM names each cluster:
   • Title
   • One-line definition
   • 3 example item IDs
        │
        ▼
 Sanity check: sample members vs. label fit
        │
        ▼
 Keep clusters with ≥ 15 items
 Remaining → "Emerging Themes"
```

### 4.3 Opportunity Score

A transparent, component-based scoring formula:

```
Opportunity Score =
    frequency_share
  × severity_avg
  × recency_weight
  × unresolved_factor
```

| Component | Calculation |
|---|---|
| **Frequency share** | Cluster size ÷ total core items |
| **Severity** | Mean severity within the cluster (1–3 scale) |
| **Recency weight** | 0–6 months → 1.0 · 6–12 months → 0.75 · 12–24 months → 0.5 |
| **Unresolved factor** | `not_found` / `gave_up` → 1.0 · `found_after_workaround` → 0.6 |

> Clusters with **n < 30** are flagged as low-confidence.

### 4.4 Trust & Validation

| Check | Method |
|---|---|
| **Human audit** | `audit.html` / CSV with 100 stratified-random items (30 rejected); Yes/No toggle; script computes precision & estimated recall |
| **Model agreement** | 300 random items re-labelled by a **different** LLM provider; inter-model agreement on `relevance` and `failure_stage` reported |

### 4.5 Narrative Insight Synthesis

Raw numbers and clusters are not enough. The pipeline generates a set of **human-readable observations** — narrative patterns that emerge when the feedback is read together. Each observation follows a consistent structure:

```
Pattern (what the data shows)
  → Implication (what it means for the product)
```

**How observations are generated:**

1. The pipeline identifies the top 8–12 cross-cutting patterns by analysing cluster overlaps, clue × failure-stage intersections, and outcome distributions.
2. An LLM synthesises each pattern into a short narrative paragraph grounded in specific counts and evidence.
3. Each observation is tagged with an **implication arrow** (`→`) — a one-line inference about what this means for photo retrieval design.
4. Every number in an observation traces back to a precomputed aggregate; nothing is hallucinated.

**Example observations the system might produce:**

> Most retrieval failures happen not because the user forgot everything, but because they remember the *wrong kind of clue* — a visual detail ("the blue sky photo") that the search system cannot interpret, while ignoring clues (date, location) that it can.
>
> → The gap is not memory loss; it is a **translation gap** between how people remember and how the system indexes.

> Users who mention "Ask Photos" or Gemini-based search report *higher* frustration scores than those using traditional keyword search — even though the AI feature is designed to help with vague queries.
>
> → Early AI search adoption is creating new expectations that the current implementation cannot meet.

> Workarounds cluster around two strategies: scrolling the timeline manually (slow but reliable) and searching by person then scanning (only works if the person was recognised). No one reports a successful workaround for screenshots or documents.
>
> → Screenshots and documents are a **dead end** — users who cannot find them have no fallback.

These observations are precomputed as `data/aggregates/observations.json` and displayed prominently on the Explore page.

---

## Phase 5 — Web Application

**Objective:** Deliver a public, fast, self-explanatory analytics experience. The app does not just display data — it **tells a story**. Every page should communicate clearly at first glance, then reward exploration with depth.

### 5.1 Design Principles

| Principle | What It Means |
|---|---|
| **Insight-first, not data-first** | Lead with what the data means, not with raw charts. Headlines and observations before tables. |
| **Progressive disclosure** | Show the summary; let users expand into evidence. Never overwhelm on first render. |
| **Every claim is grounded** | Every number, every observation, every ranking traces to real user quotes. Evidence is always one click away. |
| **Accessible and legible** | Okabe-Ito colour-blind-safe palette. Never encode meaning by colour alone — use icons, labels, patterns. Readable font sizes (≥ 14px body). |
| **Mobile-first** | Evaluators will open this on phones. Every layout must work at 375px. |

### 5.2 Tech Stack

```
┌───────────────────────────────────────────────┐
│                  Frontend                      │
│  Next.js (TypeScript) — Vercel deployment     │
│  Precomputed data loaded in memory at boot    │
│  Colour-blind-safe palette (Okabe-Ito)        │
│  Mobile-first responsive design               │
└───────────────────────────────────────────────┘
         │ Server-side API routes
         ▼
┌───────────────────────────────────────────────┐
│              Data & Search Layer              │
│                                               │
│  • Static JSON aggregates (precomputed)       │
│  • BM25 keyword index (in-memory)             │
│  • Precomputed embeddings (quantised, ≤15 MB) │
│  • LLM call (env-configured model)            │
│    — cached by question hash                  │
│    — provider failover on 429                 │
└───────────────────────────────────────────────┘
```

### 5.3 Application Pages — Detailed Breakdown

---

#### Page 1: Ask (Landing Page)

**What the user sees first:**

A clean hero section with the engine's purpose stated in plain English:

> *Why do users fail to find photos they know they have?*
>
> An AI engine that reads real public feedback and reveals where Google Photos retrieval breaks — what people remember, how they search, and why it fails.

Below: a chat input with **suggested-question chips**:

- "What kinds of old photos do users struggle to retrieve?"
- "What do people remember vs. forget?"
- "How do users phrase searches when memory is incomplete?"
- "Compare screenshots vs travel photos"
- "Which problem is the biggest opportunity?"

**Chat answer format:**

```
┌─────────────────────────────────────────────────────┐
│  Direct answer (≤ 120 words)                        │
│  ─────────────────────────────────────────────       │
│  Confidence: High · Based on 247 items              │
│                                                     │
│  Evidence:                                          │
│  ┌──────────────────────────────────────────┐       │
│  │ ▎ "I remember the photo had a blue sky   │       │
│  │ ▎  but searching 'blue sky' gives me     │       │
│  │ ▎  thousands of results"                 │       │
│  │   — Play Store · ★★ · Nov 2025          │       │
│  └──────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────┐       │
│  │ ▎ "I know it was from last summer but    │       │
│  │ ▎  there's no way to search by season"   │       │
│  │   — Reddit · r/googlephotos · Sep 2025  │       │
│  └──────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────┐       │
│  │ ▎ "Asked Gemini to find my cat photo     │       │
│  │ ▎  and it showed me random animals"      │       │
│  │   — YouTube comment · Aug 2025          │       │
│  └──────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

Every evidence card has a **coloured left border**, the **exact user quote**, **source**, **date**, and a **link to the original post**.

---

#### Page 2: Explore (Dashboard)

**Headline stat cards** (large, prominent — the first thing the eye lands on):

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│      3,400       │  │       14         │  │        5         │  │       67%        │
│  core feedback   │  │ failure clusters │  │     sources      │  │   unresolved     │
│  items analysed  │  │    discovered    │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Section: Where the feedback came from**

Horizontal bar chart showing source distribution with counts — readers instantly see the corpus composition.

**Section: Observations**

Narrative insight paragraphs (from the Narrative Insight Synthesis layer). Each one reads like a finding, not a chart description. Each ends with an **implication arrow** (`→`).

> Most of what users write on the Play Store and App Store is about search returning wrong results or nothing at all. Reddit and Help Community posts are different — they describe *strategies* for working around the system.
>
> → Public reviews capture the frustration. Community discussions capture the coping.

**Section: What users are struggling with**

Ranked list of failure stages, each as an **expandable card** with:

- **Title** + **category tag** (coloured badge, e.g. `EXPRESSION GAP`, `SYSTEM FAILURE`, `EVALUATION BURDEN`)
- **One-line description** of what this failure means
- **Count and percentage bar** (e.g. `412 · 38.2%`)
- **Expandable section** with:
  - A narrative paragraph explaining the pattern
  - 3–5 real user quotes with coloured left-border, source, and date

```
┌─────────────────────────────────────────────────────────────────┐
│ + System misunderstands query   SYSTEM FAILURE     412 · 38.2% │
│   User gave a reasonable clue but Photos returned wrong results│
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                     │
├─────────────────────────────────────────────────────────────────┤
│ + Cannot express what they want  EXPRESSION GAP    287 · 26.6% │
│   Remembers something but can't turn it into a searchable query│
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                             │
├─────────────────────────────────────────────────────────────────┤
│ + Results hard to evaluate       EVALUATION BURDEN 198 · 18.4% │
│   Results appear but user can't tell which is right            │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Additional dashboard sections:**

- Clues remembered vs. forgotten (stacked bar or butterfly chart)
- Photo type × failure stage heatmap
- Search behaviour distribution
- Timeline trend (items per month, overlaid with regression/AI-feature mentions)
- Outcome distribution (found / workaround / not found / gave up)

---

#### Page 3: Opportunity Map

Ranked problem clusters, ordered by **opportunity score** (highest first). Each cluster card shows:

- **Cluster title** + **category tag**
- **One-line definition**
- **Opportunity score** with a breakdown bar showing the 4 components visually
- **Item count** (n) with low-confidence flag if n < 30
- **Click-through** to evidence: expands to show the cluster's representative user quotes

This page answers: **"If the team could fix one thing, what should it be?"**

---

#### Page 4: Evidence Browser

A searchable, filterable interface for exploring individual feedback items:

- **Filter panel**: source, date range, failure_stage, photo_type, severity, outcome, search_behavior
- **Keyword search**: BM25-powered full-text search
- **Results list**: each item shows the quote, source, date, rating, failure_stage tag, and a link to the original post
- **Sort options**: by date, severity, relevance

This is the "show me the raw data" page — every claim on other pages can be verified here.

---

#### Page 5: How It Works

A single-slide-ready explanation:

- Architecture diagram (clean SVG)
- 5-line plain-English summary of the pipeline
- "About the data" block: X pieces of real user feedback from Y sources, each tagged against Z fields spanning the full retrieval journey

---

#### Page 6: Trust & Limits

Transparency page — this is what makes the engine credible:

- **Data funnel** visualisation (raw → filtered → LLM-classified → verified)
- **Audit results** (precision, estimated recall from human review)
- **Model agreement** (% agreement between two LLM providers on relevance and failure_stage)
- **Data freshness date** (when the corpus was last collected)
- **Known limitations** (explicit, honest list — e.g. "selection bias toward vocal users", "English-only", "no private usage data")

### 5.3 Chat Agent Architecture

The chat agent is **tool-bound** — it can only answer questions using structured tool calls against precomputed data:

```
User question
     │
     ▼
 ┌──────────────────────────┐
 │   Chat Agent (LLM)       │
 │   Max 4 tool calls/turn  │
 └──────────────────────────┘
     │
     ├──▶ search_evidence(query, filters, k)
     ├──▶ aggregate(group_by, filters)
     ├──▶ compare(segment_a, segment_b, dimension)
     └──▶ get_review(id)
     │
     ▼
 ┌──────────────────────────┐
 │   Answer Generation      │
 │                          │
 │  • ≤ 120 words           │
 │  • Numbers from tools    │
 │  • 3-6 evidence cards    │
 │  • Confidence + n        │
 │  • "Not enough evidence" │
 │    if < 3 items           │
 └──────────────────────────┘
```

**Safety rails:**
- Refuses off-topic / competitor questions politely.
- Never states a statistic not returned by a tool.
- Falls back from embedding search to BM25 on failure.
- Falls back across LLM providers on 429.

### 5.4 Search Index

| Component | Detail |
|---|---|
| **Semantic** | Precomputed embeddings (768-dim or smaller, quantised) |
| **Keyword** | BM25 index over item text |
| **Filters** | source, date range, failure_stage, photo_type, severity, outcome |
| **Bundle size** | ≤ 15 MB total |

---

## Phase 6 — Testing & Performance Validation

### 6.1 Automated Tests

| Category | Coverage |
|---|---|
| **Unit tests** | Quote-substring verification, valid enum checks, ID existence |
| **Golden set** | 15 questions (including 3 adversarial: off-topic, missing statistic, competitor question) with expected behaviour |
| **Integrity** | Every cited ID exists in the corpus; every rendered number matches precomputed aggregates |

### 6.2 Performance Budget

| Metric | Target |
|---|---|
| Dashboard load | < 2 seconds |
| Chat first token | < 3 seconds (streamed) |
| Chat full answer | < 8 seconds (typical) |
| Measured by | Script of 20 sequential queries → p50 / p95 reported |

### 6.3 Security & Abuse Prevention

| Control | Implementation |
|---|---|
| **No login required** | Public access for all evaluators |
| **Per-IP rate limiting** | Prevents abuse of LLM-backed endpoints |
| **Input cap** | 500 characters max per question |
| **Daily budget guard** | Prevents free-tier quota exhaustion |
| **Server-side keys only** | API keys live in Vercel env vars; never in client bundle |

---

## Phase 7 — Deployment & Handoff

### 7.1 Deployment Target

| Item | Detail |
|---|---|
| **Platform** | Vercel (Next.js / TypeScript) |
| **Data loading** | Static JSON + index files loaded into memory at boot |
| **Environment** | All secrets via Vercel environment variables |
| **Domain** | Public URL, no authentication |

### 7.2 Deliverables

| Deliverable | Description |
|---|---|
| **Live URL** | Public, works on desktop and mobile, all suggested questions return cited answers within speed budget |
| **Repository** | Clean codebase with `README.md` (how to rerun and refresh data) |
| **`docs/how_it_works.md`** | Architecture diagram + 5-line explanation |
| **`docs/corpus_report.md`** | Funnel, per-source counts, date ranges, audit & agreement results, limitations |
| **Audit & trust data** | Precision, recall estimates, model agreement visible in the app |
| **RUNLOG.md** | Counts, quota usage, errors from every pipeline stage |

---

## Cross-Cutting Concerns

### Resilience & Resumability

Every pipeline stage writes checkpoints. A crash at any point resumes from the last completed batch — critical for multi-day YouTube quota windows and free-tier LLM rate limits.

### Caching Strategy

```
LLM results  ──▶  hash(text + prompt_version) ──▶  disk cache
Chat answers  ──▶  hash(question)              ──▶  response cache
API calls     ──▶  per-source checkpoint files  ──▶  skip completed
```

### Cost Management

| Concern | Mitigation |
|---|---|
| LLM free-tier limits | Batch 10–20 items per call; cache every result; exponential backoff on rate limits |
| YouTube quota (10k units/day) | Budget ≤ 9,000 units/day; log usage; checkpoint for next-day resume |
| Vercel free tier | No heavy compute at request time; all data precomputed |

### Data Privacy & Ethics

- Public data only — no private APIs or authenticated user data.
- Usernames and PII dropped or hashed at ingestion.
- `robots.txt` respected; rate limits honoured.
- Scraped text treated as untrusted (prompt-injection defence).
- No person's name appears anywhere in the app, repo, or documentation.

---

## Technology Summary

| Layer | Technology |
|---|---|
| Collection | `google-play-scraper`, iTunes RSS, PRAW, YouTube Data API v3, Playwright |
| Processing | Python (normalisation, dedup, regex pre-filter) |
| Extraction | LLM (env-configured, e.g. Gemini / Groq) with JSON-schema-constrained output |
| Clustering | Sentence embeddings + HDBSCAN / KMeans |
| Search index | BM25 + precomputed vector embeddings (quantised) |
| Web app | Next.js (TypeScript) |
| Hosting | Vercel |
| Secrets | Server-side env vars only |
