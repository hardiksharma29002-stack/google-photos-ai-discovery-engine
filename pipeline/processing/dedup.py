import os
import sys
import json
import re
from datasketch import MinHash, MinHashLSH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import PROCESSED_DIR
from pipeline.utils import setup_logger, append_jsonl

logger = setup_logger("Dedup")

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def run_dedup():
    in_file = PROCESSED_DIR / "lang_filtered.jsonl"
    out_file = PROCESSED_DIR / "deduped.jsonl"
    
    if out_file.exists():
        out_file.unlink()
        
    if not in_file.exists():
        logger.error(f"{in_file} does not exist.")
        return
        
    exact_seen = set()
    lsh = MinHashLSH(threshold=0.85, num_perm=128)
    
    total = 0
    kept = 0
    
    with open(in_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            total += 1
            text = item.get("text", "")
            norm_text = normalize_text(text)
            
            if not norm_text:
                continue
                
            # Exact dedup
            if norm_text in exact_seen:
                continue
            exact_seen.add(norm_text)
            
            # Near-dup dedup
            tokens = set(norm_text.split())
            if len(tokens) < 3: # Too short to minhash reliably, keep it
                append_jsonl(out_file, item)
                kept += 1
                continue
                
            m = MinHash(num_perm=128)
            for d in tokens:
                m.update(d.encode('utf8'))
                
            result = lsh.query(m)
            if result:
                # It's a near duplicate of an existing item
                continue
                
            lsh.insert(item["id"], m)
            append_jsonl(out_file, item)
            kept += 1
            
    logger.info(f"Dedup complete. Kept {kept}/{total} items ({(kept/total)*100 if total > 0 else 0:.1f}%)")

if __name__ == "__main__":
    run_dedup()
