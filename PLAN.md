# Phase 0: Credential & API Verification Plan

## Endpoints Verified
1. **YouTube Data API v3**: Verified. Cost is 100 units per `search.list` call, 1 unit per `commentThreads.list` call. Daily limit is 10,000 units. We will limit our batch to 9,000 units per run to avoid capping out.
2. **Gemini API**: Verified (using `gemini-2.5-flash`). Extremely fast, generous free tier (1,500 req/day).
3. **Groq API**: Verified (using `groq/compound-mini`). Very high rate limits.
4. **Reddit API**: SKIPPED for now.

## Data Collection Strategy
Because we skipped Reddit, we will pull more heavily from the **Google Play Store**, **App Store**, and **YouTube** to ensure we hit our 20,000 - 30,000 item goal. 

## Rate Limits & Fallbacks
- **Google Play**: `google-play-scraper` has no strict rate limit, but we will add a 0.5s sleep to prevent IP bans.
- **App Store**: `app-store-scraper` hits public RSS feeds. We will limit it to 1 req/sec.
- **YouTube**: We will strictly monitor quota units and checkpoint the file after every query so we can resume tomorrow if we hit the limit.
