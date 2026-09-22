import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from pipeline.config import RAW_DIR
from pipeline.utils import setup_logger, append_jsonl, generate_id, save_checkpoint, load_checkpoint

logger = setup_logger("RedditApifyCollector")

# Target subreddits and search queries related to Google Photos search & retrieval breakdowns
REDDIT_SUBREDDITS = ["googlephotos", "GooglePixel", "Android"]
REDDIT_SEARCH_QUERIES = [
    "search not working",
    "can't find photo",
    "cannot find photo",
    "face grouping broken",
    "missing photos in search",
    "Ask Photos Gemini",
    "wrong date timeline search",
    "search receipts documents ocr",
    "search hidden locked folder",
    "find old photos"
]

def collect_reddit_apify(max_items_per_query: int = 50):
    """
    Collects real user feedback from Reddit using Apify's REST API.
    Bypasses official Reddit OAuth constraints while ensuring structured JSON output.
    
    Requires:
        APIFY_API_TOKEN in environment (.env)
    Outputs:
        data/raw/reddit.jsonl
    """
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token or api_token.strip() == "your_apify_api_token_here":
        logger.warning("APIFY_API_TOKEN not configured in .env.")
        logger.warning("To enable Reddit ingestion, add your Apify token to .env: APIFY_API_TOKEN=apify_api_...")
        logger.warning("Free Apify tokens are available at: https://console.apify.com/account/integrations")
        return 0

    out_file = RAW_DIR / "reddit.jsonl"
    checkpoint = load_checkpoint("reddit_apify")
    completed_queries = set(checkpoint.get("completed_queries", []))

    total_collected = 0
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    logger.info("Initializing Apify Reddit Collector...")
    logger.info(f"Targeting subreddits: {', '.join(REDDIT_SUBREDDITS)}")

    # Apify actor: trudax/reddit-scraper-lite
    # https://apify.com/trudax/reddit-scraper-lite
    actor_id = "trudax~reddit-scraper-lite"

    for query in REDDIT_SEARCH_QUERIES:
        if query in completed_queries:
            logger.info(f"Skipping already completed query: '{query}'")
            continue

        logger.info(f"Scraping Reddit discussions via Apify for: '{query}'")
        
        # Build search URLs across target subreddits
        search_urls = [
            f"https://www.reddit.com/r/{sub}/search/?q={requests.utils.quote(query)}&restrict_sr=1&sort=relevance"
            for sub in REDDIT_SUBREDDITS
        ]

        actor_input = {
            "searches": search_urls,
            "maxItems": max_items_per_query,
            "maxComments": 10,
            "scrollTimeout": 20
        }

        try:
            # Trigger synchronous run with dataset retrieval (waits up to 120s)
            run_url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?timeout=120"
            response = requests.post(run_url, headers=headers, json=actor_input, timeout=130)

            if response.status_code not in (200, 201):
                logger.error(f"Apify API returned status {response.status_code}: {response.text[:200]}")
                continue

            items = response.json()
            if not isinstance(items, list):
                logger.warning(f"Unexpected response format from Apify: {type(items)}")
                continue

            query_collected = 0
            for post in items:
                title = post.get("title", "").strip()
                body = post.get("selftext", "") or post.get("body", "") or ""
                url = post.get("url", "") or post.get("permalink", "")
                subreddit = post.get("subreddit", "googlephotos")
                score = post.get("score", 0)
                post_id = post.get("id", "") or str(hash(title))

                # Collect top comments if available
                comments = post.get("comments", [])
                comment_texts = []
                if isinstance(comments, list):
                    for c in comments[:5]:
                        if isinstance(c, dict) and c.get("body"):
                            comment_texts.append(c["body"].strip())

                comments_block = "\n---\nComment: ".join(comment_texts)
                full_text = f"Title: {title}\nPost: {body}"
                if comments_block:
                    full_text += f"\nUser Comments:\n{comments_block}"

                # Skip completely empty or ultra-short posts
                if len(full_text.strip()) < 30:
                    continue

                created_utc = post.get("createdUtc") or post.get("createdAt")
                if created_utc:
                    try:
                        if isinstance(created_utc, (int, float)):
                            dt_str = datetime.utcfromtimestamp(created_utc).isoformat()
                        else:
                            dt_str = str(created_utc)
                    except Exception:
                        dt_str = datetime.utcnow().isoformat()
                else:
                    dt_str = datetime.utcnow().isoformat()

                normalized_item = {
                    "id": generate_id("reddit", f"{post_id}-{title}"),
                    "source": "reddit",
                    "country": "global",
                    "date": dt_str,
                    "title": title,
                    "text": full_text,
                    "url": url if url.startswith("http") else f"https://reddit.com{url}",
                    "subreddit": f"r/{subreddit}",
                    "score": score
                }

                append_jsonl(out_file, normalized_item)
                query_collected += 1

            total_collected += query_collected
            logger.info(f"Successfully collected {query_collected} Reddit posts for '{query}'.")

            # Update checkpoint
            completed_queries.add(query)
            save_checkpoint("reddit_apify", {"completed_queries": list(completed_queries)})

            # Rate-limiting pause between Apify runs
            time.sleep(2)

        except requests.exceptions.Timeout:
            logger.error(f"Apify request timed out for query '{query}'. Moving to next query.")
        except Exception as e:
            logger.error(f"Error scraping Reddit via Apify for query '{query}': {e}")

    logger.info(f"Reddit collection finished. Total posts stored: {total_collected} in {out_file}")
    return total_collected

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Starting Apify Reddit Collector test...")
    collected = collect_reddit_apify(max_items_per_query=20)
    print(f"Done. Collected: {collected} items.")
