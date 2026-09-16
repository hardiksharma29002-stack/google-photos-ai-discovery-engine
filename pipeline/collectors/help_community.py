import os
import sys
import time
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
from pipeline.config import SEED_PHRASES, DATE_WINDOW_MONTHS, RAW_DIR
from pipeline.utils import setup_logger, save_checkpoint, load_checkpoint, append_jsonl, generate_id

logger = setup_logger("HelpCommunityCollector")

def collect_help_community():
    out_file = RAW_DIR / "help_community.jsonl"
    cutoff_date = datetime.now() - timedelta(days=DATE_WINDOW_MONTHS * 30)
    
    checkpoint = load_checkpoint("help_community")
    completed_queries = set(checkpoint.get("completed_queries", []))
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        count = 0
        
        for query in SEED_PHRASES[:10]:
            if query in completed_queries:
                continue
                
            logger.info(f"Searching Google Support for: {query}")
            try:
                search_url = f"https://support.google.com/photos/search?q={query}"
                page.goto(search_url, wait_until="domcontentloaded")
                time.sleep(2)
                
                results = page.locator(".search-results .search-result").all()
                for res in results:
                    title = res.locator("h3").inner_text() if res.locator("h3").count() > 0 else ""
                    snippet = res.locator(".snippet").inner_text() if res.locator(".snippet").count() > 0 else ""
                    
                    if title and snippet:
                        item = {
                            "id": generate_id("help", f"{title}-{snippet}"),
                            "source": "help_community",
                            "country": "unknown",
                            "date": datetime.now().isoformat(),
                            "text": f"Title: {title}\nSnippet: {snippet}",
                            "rating": None,
                            "metadata": {
                                "query": query
                            }
                        }
                        append_jsonl(out_file, item)
                        count += 1
                        
            except Exception as e:
                logger.error(f"Error fetching help community for query {query}: {e}")
                
            completed_queries.add(query)
            checkpoint["completed_queries"] = list(completed_queries)
            save_checkpoint("help_community", checkpoint)
            time.sleep(2)
            
        logger.info(f"Help community collection complete. Collected {count} snippets.")
        browser.close()

if __name__ == "__main__":
    collect_help_community()
