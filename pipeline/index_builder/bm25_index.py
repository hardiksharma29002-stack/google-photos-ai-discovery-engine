import os
import sys
import json
import pickle
from rank_bm25 import BM25Okapi
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import DATA_DIR
from pipeline.utils import setup_logger

logger = setup_logger("BM25Index")

def build_index():
    core_file = DATA_DIR / "extracted" / "core.jsonl"
    out_dir = DATA_DIR / "index"
    os.makedirs(out_dir, exist_ok=True)
    
    if not core_file.exists():
        logger.error("Core file missing.")
        return
        
    corpus = []
    ids = []
    
    with open(core_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            ids.append(item["id"])
            
            text = item.get("original_text", "") + " " + item.get("core_problem", "")
            tokens = text.lower().split()
            corpus.append(tokens)
            
    if not corpus:
        return
        
    logger.info(f"Building BM25 Index for {len(corpus)} items...")
    bm25 = BM25Okapi(corpus)
    
    with open(out_dir / "bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)
        
    with open(out_dir / "bm25_ids.json", "w") as f:
        json.dump(ids, f)
        
    logger.info("BM25 Index built and saved successfully.")

if __name__ == "__main__":
    build_index()
