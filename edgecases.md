# Comprehensive Edge Cases Document (NL AI Engine)

This document outlines potential edge cases across the entire pipeline—from data collection to LLM extraction and verification—and details exactly how the system is designed to handle them.

---

## 1. Data Collection Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **API Rate Limits / Quota Exhaustion** | YouTube blocks access for the day, crashing the script. | We implemented a strict counter (`YOUTUBE_DAILY_BUDGET=9000`). Once the limit is hit, the script stops gracefully and saves the exact `query` it was on in the checkpoint file to resume tomorrow. |
| **IP Blocking by Play/App Store** | Heavy scraping without an API key causes Google/Apple to return `403 Forbidden` or CAPTCHAs. | We added a `time.sleep()` delay between page fetches. If a `403` occurs, the scraper logs the error, saves the checkpoint, and halts so the user can change IPs (e.g., via VPN) and resume. |
| **Missing Timestamps in App Store JSON** | `app_store.jsonl` entries might lack an `updated` timestamp. | The code includes a fallback: `dt = datetime.now()`. It will treat un-timestamped legacy reviews as current to ensure they aren't dropped by the cutoff filter. |
| **Missing Author/Username** | User deleted their account, leaving a null author string. | The generator uses a fallback ID string (`"unknown"`) to prevent hashing errors in `generate_id()`. |

## 2. Data Cleaning & Processing Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Emojis & Special Characters** | MinHash or JSON parsers throw Unicode errors. | We strictly enforce `encoding="utf-8"` in all file I/O operations. During deduplication, texts are whitespace-normalised and lowercased to standardise them before hashing. |
| **Extremely Short Reviews** | Reviews like "bad search" (2 words) break the MinHash deduplication algorithm (requires ≥3 words). | The `dedup.py` script checks token length. If `len(tokens) < 3`, it skips MinHashing (keeps the item) but still passes it through exact deduplication. |
| **Hinglish & Roman Hindi** | `langdetect` classifies Roman Hindi (e.g., "Mera photo nahi mil raha") as Indonesian, Somali, or Unknown, dropping valid Indian reviews. | We permit `"unknown"` as a fallback language. Because we have an aggressive Keyword Prefilter (`prefilter.py`), keeping `"unknown"` is safe—if it contains "search" or "find", it will be caught by the prefilter. |
| **Infinite Appending on Reruns** | Running `run_phase2.py` twice doubles the file size. | The scripts explicitly check for `out_file.exists()` and `unlink()` (delete) the file at the start of every run. |

## 3. LLM Extraction Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **LLM Returns Markdown instead of JSON** | Gemini outputs ` ```json { ... } ``` ` which crashes Python's `json.loads()`. | The LLM client will include a regex cleaner `re.sub(r'```json\n|\n```', '', text)` before parsing. Alternatively, we use `response_mime_type="application/json"` in the Gemini API config. |
| **Quote Hallucination** | The LLM hallucinates an `evidence_quote` that does not actually exist in the raw user text. | **Phase 3 Verifier:** A strict code-based check (`if quote not in raw_text`) validates every extraction. If it fails, the item is dropped or passed to the Groq agreement model for a retry. |
| **Context Window Overflow** | Batching 20 massive 1,000-word reviews causes Gemini to exceed its token limit or forget instructions. | The batching logic will dynamically measure string length. If a batch exceeds ~15,000 characters, it splits it into a smaller batch automatically. |
| **Rate Limit (`429 Too Many Requests`)** | Sending batches too quickly causes the free tier to block us for a minute. | We will implement a `@backoff` decorator in `llm_client.py` using Exponential Backoff (wait 2s, 4s, 8s, 16s) to handle temporary `429` blocks automatically without crashing. |

## 4. Analytical & Edge-Case Sentiments

| Edge Case | Impact | Mitigation Strategy (Handled by LLM Taxonomy) |
| :--- | :--- | :--- |
| **Sarcasm / Hyperbole** | "Wow, Google Photos search is SO great now that I can't find anything." | We instruct the LLM to look for intent rather than raw sentiment scores. The `sub_intent` will correctly map to "Inability to find specific items" rather than "Praise". |
| **Irrelevant Rambling** | "I can't find my old dog photo. Also my pixel 7 battery sucks and youtube music is bad." | The LLM is instructed to classify `relevance: core`, extract the search-related quote for `evidence_quote`, and ignore the battery/music complaints. |
| **Feature Requests vs. Bug Reports** | "I wish I could search by dog breed" vs "Search by dog breed is broken". | Handled by our enums: `user_intent: "feature_request"` vs `user_intent: "complaint"`. Both are kept in the core corpus but tagged differently. |
| **App Store vs Google Play Lexicon** | Apple users mention "iOS 17" or "iCloud", confusing Android-centric models. | `platform` is passed as context to the LLM, ensuring it understands OS-specific jargon without rejecting the review. |
| **Ambiguous Entities** | "Can't find pictures of my baby" | LLM is trained to classify "baby" as `entity: "Person"` vs "Can't find pictures of my car" -> `entity: "Object"`. |
| **Multiple Complaints in One Review** | "Search is broken, can't find by date, face grouping is gone" | The Prompt explicitly asks the LLM to output an array of `issues` or select the primary `sub_intent` based on what the user emphasizes most. |
| **Non-English Keywords in English Review** | "I want to search for 'Diwali diyas'" | The keyword pre-filter retains English context; the Gemini model inherently understands global/regional entities without translation. |

## 5. Pipeline Integrity & Systems Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Power Outage / Crash mid-run** | Losing hours of LLM extraction progress. | Extraction will write to `extracted.jsonl` in append-mode `("a")` line-by-line. A crash only loses the currently processing batch. Checkpoints resume instantly. |
| **Schema Drift** | The unified schema changes in Phase 2, breaking Phase 3. | Phase 3 relies on a strict Pydantic model (`schema.py`). If a key is missing, Pydantic raises a validation error, skipping the item rather than crashing the pipeline. |
| **Disk Space Exhaustion** | 30,000 JSON items take up too much memory/disk. | Processing is done as an Iterator (`for line in f:`). We never load the full 30,000 items into RAM. Disk footprint for JSONL is minimal (<100MB). |
| **Corrupted JSON Line** | A random bit flip or partial write corrupts a JSON line in `raw.jsonl`. | `json.loads()` will throw `json.decoder.JSONDecodeError`. We catch this, log a warning, and skip the line instead of halting the entire script. |
| **API Provider Outage (Gemini Down)** | Extraction halts completely. | The LLM wrapper (`llm_client.py`) will automatically fallback to Groq (`groq/compound-mini`) if Gemini returns consecutive 500/503 errors. |

## 6. Storage & Security Edge Cases

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Accidental API Key Leak** | Keys pushed to GitHub. | `.env` is rigorously added to `.gitignore`. No hardcoded strings in code. Fallback checking throws an immediate error if `GEMINI_API_KEY` is missing in env. |
| **PII (Personally Identifiable Information)** | Reviews contain emails or phone numbers. | Google Play/App Store auto-redact these usually, but the LLM prompt explicitly instructs the AI: `DO NOT extract names, phone numbers, or emails into evidence_quote`. |

## 7. Scaling Edge Cases (Future-Proofing)

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Dataset grows from 30K to 1 Million** | Deduplication via `datasketch` consumes too much RAM. | `MinHashLSH` is currently in-memory. For 1M+, we will swap the storage backend to Redis (supported natively by `datasketch`). |
| **Extraction takes 50+ hours** | Sequential LLM calls are too slow. | Batching (10-20 per call) cuts time by 90%. If faster speeds are needed, we can implement `asyncio` for parallel API requests, staying just under the RPS limit. |
