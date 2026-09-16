import os
import sys
# Add pipeline root to path so we can import from config and utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_play_scraper import Sort, reviews
from datetime import datetime, timedelta
import time
from pipeline.config import COUNTRIES, DATE_WINDOW_MONTHS, RAW_DIR
from pipeline.utils import setup_logger, save_checkpoint, load_checkpoint, append_jsonl, generate_id

logger = setup_logger("GooglePlayCollector")

def collect_play_store_reviews():
    app_id = "com.google.android.apps.photos"
    out_file = RAW_DIR / "google_play.jsonl"
    cutoff_date = datetime.now() - timedelta(days=DATE_WINDOW_MONTHS * 30)
    
    checkpoint = load_checkpoint("google_play")
    
    for country in COUNTRIES:
        if checkpoint.get(country, False):
            logger.info(f"Skipping {country}, already completed.")
            continue
            
        logger.info(f"Starting collection for country: {country}")
        continuation_token = None
        count = 0
        
        while True:
            try:
                result, continuation_token = reviews(
                    app_id,
                    lang='en',
                    country=country,
                    sort=Sort.NEWEST,
                    count=200,
                    continuation_token=continuation_token
                )
                
                if not result:
                    break
                    
                earliest_date = datetime.now()
                
                for r in result:
                    dt = r['at']
                    if dt < earliest_date:
                        earliest_date = dt
                    
                    if dt < cutoff_date:
                        continue
                        
                    item = {
                        "id": generate_id("gplay", r['reviewId']),
                        "source": "google_play",
                        "country": country,
                        "date": dt.isoformat(),
                        "text": r['content'],
                        "rating": r['score'],
                        "metadata": {
                            "thumbsUpCount": r['thumbsUpCount'],
                            "reviewCreatedVersion": r.get('reviewCreatedVersion')
                        }
                    }
                    append_jsonl(out_file, item)
                    count += 1
                
                logger.info(f"[{country}] Collected {count} reviews... Earliest seen: {earliest_date.date()}")
                
                if earliest_date < cutoff_date or not continuation_token:
                    logger.info(f"[{country}] Reached cutoff date or end of feed.")
                    break
                    
                # 0.5s sleep to prevent rate limiting
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error fetching reviews for {country}: {e}")
                break
                
        checkpoint[country] = True
        save_checkpoint("google_play", checkpoint)
        
    logger.info("Google Play Store collection complete.")

if __name__ == "__main__":
    collect_play_store_reviews()
