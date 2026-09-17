import os
import sys
import json
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import PROCESSED_DIR, SEED_PHRASES
from pipeline.utils import setup_logger, append_jsonl

logger = setup_logger("Prefilter")

def run_prefilter():
    in_file = PROCESSED_DIR / "deduped.jsonl"
    out_file = PROCESSED_DIR / "prefiltered.jsonl"
    
    if out_file.exists():
        out_file.unlink()
        
    if not in_file.exists():
        logger.error(f"{in_file} does not exist.")
        return
        
    total = 0
    kept = 0
    
    keywords = [k.lower() for k in SEED_PHRASES]
    
    with open(in_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            total += 1
            text = item.get("text", "").lower()
            
            if any(kw in text for kw in keywords):
                append_jsonl(out_file, item)
                kept += 1
                
    logger.info(f"Prefilter complete. Kept {kept}/{total} items ({(kept/total)*100 if total > 0 else 0:.1f}%)")

if __name__ == "__main__":
    run_prefilter()
