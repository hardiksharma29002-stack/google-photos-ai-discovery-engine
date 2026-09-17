import os
import sys
import json
import glob
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import RAW_DIR, PROCESSED_DIR
from pipeline.utils import setup_logger, append_jsonl

logger = setup_logger("Normalizer")

def process_file(filepath, out_file):
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            raw_item = json.loads(line)
            
            source = raw_item.get("source", "unknown")
            platform = "android" if source == "google_play" else "ios" if source == "app_store" else "web"
            
            metadata = raw_item.get("metadata", {})
            app_version = metadata.get("reviewCreatedVersion") if source == "google_play" else None
            
            url = ""
            if source == "youtube":
                url = f"https://youtube.com/watch?v={metadata.get('videoId')}"
            
            thread_context = metadata.get("query", "")
            
            normalised_item = {
                "id": raw_item["id"],
                "source": source,
                "url": url,
                "date": raw_item["date"],
                "rating": raw_item.get("rating"),
                "platform": platform,
                "app_version": app_version,
                "language": "unknown", # To be filled in language_detect.py
                "text": raw_item["text"],
                "thread_context": thread_context
            }
            
            append_jsonl(out_file, normalised_item)
            count += 1
            
    return count

def normalise_all():
    out_file = PROCESSED_DIR / "normalised.jsonl"
    
    # clear out_file if it exists so we don't append indefinitely on reruns
    if out_file.exists():
        out_file.unlink()
        
    raw_files = glob.glob(str(RAW_DIR / "*.jsonl"))
    
    total = 0
    for file in raw_files:
        logger.info(f"Normalising {os.path.basename(file)}...")
        count = process_file(file, out_file)
        logger.info(f"Normalised {count} items from {os.path.basename(file)}")
        total += count
        
    logger.info(f"Normalisation complete! Total items: {total}")

if __name__ == "__main__":
    normalise_all()
