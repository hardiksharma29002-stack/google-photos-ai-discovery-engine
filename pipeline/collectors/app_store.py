import os
import sys
import requests
from datetime import datetime, timedelta
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import COUNTRIES, DATE_WINDOW_MONTHS, RAW_DIR
from pipeline.utils import setup_logger, save_checkpoint, load_checkpoint, append_jsonl, generate_id

logger = setup_logger("AppStoreCollector")

def collect_app_store_reviews():
    app_id = "962194608" # Google Photos
    out_file = RAW_DIR / "app_store.jsonl"
    cutoff_date = datetime.now() - timedelta(days=DATE_WINDOW_MONTHS * 30)
    
    checkpoint = load_checkpoint("app_store")
    
    for country in COUNTRIES:
        if checkpoint.get(country, False):
            logger.info(f"Skipping {country}, already completed.")
            continue
            
        logger.info(f"Starting collection for country: {country}")
        count = 0
        
        try:
            for page in range(1, 11):
                url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
                response = requests.get(url, timeout=10)
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                entries = data.get('feed', {}).get('entry', [])
                
                if not entries:
                    break
                
                for entry in entries:
                    if 'author' not in entry:
                        continue
                        
                    author = entry['author']['name']['label']
                    title = entry['title']['label']
                    content = entry['content']['label']
                    rating = int(entry['im:rating']['label'])
                    
                    dt_str = entry.get('updated', {}).get('label')
                    if dt_str:
                        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    else:
                        dt = datetime.now()
                        
                    if dt < cutoff_date:
                        continue
                        
                    item = {
                        "id": generate_id("appstore", f"{country}-{author}-{dt.timestamp()}"),
                        "source": "app_store",
                        "country": country,
                        "date": dt.isoformat(),
                        "text": content,
                        "rating": rating,
                        "metadata": {
                            "title": title,
                            "userName": author
                        }
                    }
                    append_jsonl(out_file, item)
                    count += 1
                
                time.sleep(1)
                
            logger.info(f"[{country}] Collected {count} reviews.")
            
        except Exception as e:
            logger.error(f"Error fetching reviews for {country}: {e}")
            
        checkpoint[country] = True
        save_checkpoint("app_store", checkpoint)

    logger.info("Apple App Store collection complete.")

if __name__ == "__main__":
    collect_app_store_reviews()
