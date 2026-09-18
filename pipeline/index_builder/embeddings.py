import os
import sys
import json
import numpy as np
from sentence_transformers import SentenceTransformer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import DATA_DIR
from pipeline.utils import setup_logger

logger = setup_logger("Embeddings")

def generate_embeddings():
    in_file = DATA_DIR / "extracted" / "core.jsonl"
    out_dir = DATA_DIR / "index"
    os.makedirs(out_dir, exist_ok=True)
    
    if not in_file.exists():
        logger.error("Core JSONL missing.")
        return
        
    # Lightweight, fast model for 384-dimensional embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    ids = []
    texts = []
    
    with open(in_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            ids.append(item["id"])
            texts.append(item.get("core_problem", item.get("failure_detail", "")))
            
    if not texts:
        return
        
    logger.info(f"Generating embeddings for {len(texts)} items...")
    embeddings = model.encode(texts)
    
    np.save(out_dir / "embeddings.npy", embeddings)
    with open(out_dir / "embedding_ids.json", "w") as f:
        json.dump(ids, f)
        
    logger.info("Embeddings saved successfully.")

if __name__ == "__main__":
    generate_embeddings()
