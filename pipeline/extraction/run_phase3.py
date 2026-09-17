import os
import sys
import json
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import PROCESSED_DIR, DATA_DIR
from pipeline.utils import setup_logger, append_jsonl
from pipeline.extraction.batch_extract import BatchExtractor
from pipeline.extraction.verify import verify_extraction

load_dotenv()
logger = setup_logger("Phase3")

def main():
    in_file = PROCESSED_DIR / "prefiltered.jsonl"
    out_core = DATA_DIR / "extracted" / "core.jsonl"
    out_adjacent = DATA_DIR / "extracted" / "adjacent.jsonl"
    out_rejected = DATA_DIR / "extracted" / "rejected.jsonl"
    
    os.makedirs(DATA_DIR / "extracted", exist_ok=True)
    
    if not in_file.exists():
        logger.error("No prefiltered data found. Run phase 2.")
        return
        
    extractor = BatchExtractor(provider="gemini")
    
    batch = []
    batch_size = 10
    total_processed = 0
    total_dropped = 0
    
    def process_batch(b):
        nonlocal total_dropped
        if not b: return
        results = extractor.extract(b)
        
        for i, raw_item in enumerate(b):
            if i < len(results):
                ext = results[i]
                is_valid = verify_extraction(raw_item, ext)
                
                if not is_valid:
                    total_dropped += 1
                    continue
                    
                ext["original_text"] = raw_item["text"]
                ext["source"] = raw_item["source"]
                ext["date"] = raw_item["date"]
                ext["url"] = raw_item["url"]
                
                rel = ext.get("relevance", "not_relevant")
                if rel == "core":
                    append_jsonl(out_core, ext)
                elif rel == "adjacent":
                    append_jsonl(out_adjacent, ext)
                else:
                    append_jsonl(out_rejected, ext)
    
    with open(in_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            batch.append(item)
            
            if len(batch) >= batch_size:
                logger.info(f"Processing batch of {len(batch)}... Total processed: {total_processed}")
                process_batch(batch)
                total_processed += len(batch)
                batch = []
                
    if batch:
        process_batch(batch)
        total_processed += len(batch)
        
    logger.info(f"Phase 3 Complete! Processed {total_processed} items. Dropped by Verifier: {total_dropped}")

if __name__ == "__main__":
    main()
