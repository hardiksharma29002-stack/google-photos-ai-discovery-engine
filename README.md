# Google Photos AI Discovery Engine

> A natural-language analytics platform and discovery engine built for the Google Photos Core Experience PM case study. Mines 174,000+ public reviews to understand **how users remember old photos**, **why retrieval fails when memory is incomplete**, and **which problem areas present the highest-ROI product opportunities**.

---

## 🌟 Key Capabilities

1. **4 Core Questions Answered with Empirical Evidence:**
   - **What kinds of old photos do users struggle to retrieve?** (Everyday Moments 38%, Documents/OCR 21%, Pets 20%, Screenshots 10%, Family 10%).
   - **What do people actually remember?** (Visual Appearance 44%, Vague Scene Impression 42%, Face/Person 17%, Setting 11%).
   - **What have they forgotten?** (Exact Calendar Date & Geolocation 88.6%, Album/Folder Name 10.3%).
   - **How do users formulate searches?** (Conversational descriptive sentences 52.5%, Ask Photos AI 30%, Album browsing 8%).
2. **Side-by-Side Problem & Opportunity Comparison:** Compare any two retrieval problem clusters side-by-side on volume, severity, unresolved rate, real user evidence quotes, and PM strategic trade-offs.
3. **Conversational Assistant with Real-Time SSE Streaming:** Ask *any* question about the data, trends, or segments with sub-second token streaming backed by verified metrics.
4. **Transparent Opportunity Scoring:** Prioritizes 14 clusters using:
   $$\text{Opportunity Score} = \text{Frequency Share} \times \frac{\text{Severity}}{3} \times \text{Unresolved Factor} \times \text{Recency Weight} \times 400$$
5. **Quality Audit & Dual-Model Verification:** Includes a 100-item stratified human audit (92% precision, 89.4% recall) and a 300-item cross-model agreement report ($\kappa = 0.84$).

---

## 🚀 Running the Web Application Locally

### Prerequisites
- Node.js (v18 or higher)
- Python 3.10+ (for data pipeline scripts)

### Start Development Server
```bash
cd ui
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Application Navigation
- **Ask Assistant (`/`)**: Interactive chat with SSE token streaming and suggested discovery questions.
- **Dashboard (`/dashboard`)**: KPI overview, all 14 failure clusters with evidence drilldown, and source distribution.
- **Opportunities (`/opportunities`)**: Ranked opportunity table, Photo Types breakdown, Memory & Formulation analysis, and Side-by-Side Problem Comparison.
- **Evidence Browser (`/raw-data`)**: Searchable, filterable directory of 4,615 reviews with intent and source attribution.
- **How It Works (`/how-it-works`)**: System architecture diagram, 5-stage pipeline walkthrough, and security safeguards.
- **Trust & Limits (`/trust`)**: Full funnel visualization, 100-item audit results, dual-model agreement check, and known limitations.
- **Live Test (`/playground`)**: Sandbox to paste any user review and classify it on the fly.

---

## 🔄 How to Rerun and Refresh Data

To refresh the pipeline from raw sources:

1. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and configure:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GROQ_API_KEY=your_groq_api_key
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

2. **Step 1: Ingest Raw Data**
   ```bash
   python pipeline/collectors/google_play.py
   python pipeline/collectors/app_store.py
   ```

3. **Step 2: Clean & Prefilter**
   ```bash
   python pipeline/processing/normalise.py
   python pipeline/processing/prefilter.py
   ```

4. **Step 3: Extract Schema & Verify**
   ```bash
   python pipeline/analysis/process_all_clean_reviews.py
   python pipeline/analysis/enrich_discovery_dimensions.py
   ```

5. **Step 4: Generate Audit & Agreement Metrics**
   ```bash
   python pipeline/analysis/generate_audit_data.py
   ```

All static aggregate bundles are automatically written to `ui/public/data/aggregates/` and `ui/public/data/audit/`.

---

## 📋 Checklist of Manual Steps for Deployment

- [ ] Ensure `.env.local` in `ui/` contains valid `GEMINI_API_KEY` and `GROQ_API_KEY`.
- [ ] Verify static JSON files exist in `ui/public/data/aggregates/` and `ui/public/data/audit/`.
- [ ] Connect the GitHub repository to Vercel.
- [ ] In Vercel Project Settings, add the environment variables (`GEMINI_API_KEY`, `GROQ_API_KEY`).
- [ ] Deploy and verify the live public URL without login.

---

## 📂 Documentation

- [How It Works & Pipeline Flow](file:///c:/Users/hardi/OneDrive/Desktop/NL_Ai_Engine/docs/how_it_works.md)
- [Corpus Funnel & Quality Audit Report](file:///c:/Users/hardi/OneDrive/Desktop/NL_Ai_Engine/docs/corpus_report.md)
- [System Architecture](file:///c:/Users/hardi/OneDrive/Desktop/NL_Ai_Engine/architecture.md)
- [Edge Cases & Design Decisions](file:///c:/Users/hardi/OneDrive/Desktop/NL_Ai_Engine/edgecases.md)
