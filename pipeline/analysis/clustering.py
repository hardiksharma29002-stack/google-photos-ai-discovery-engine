import os
import sys
import json
import numpy as np
import hdbscan
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import DATA_DIR
from pipeline.utils import setup_logger

logger = setup_logger("Clustering")

def run_clustering():
    emb_file = DATA_DIR / "index" / "embeddings.npy"
    id_file = DATA_DIR / "index" / "embedding_ids.json"
    out_dir = DATA_DIR / "clusters"
    os.makedirs(out_dir, exist_ok=True)
    
    if not emb_file.exists() or not id_file.exists():
        logger.error("Embeddings not found. Run embeddings.py first.")
        return
        
    embeddings = np.load(emb_file)
    with open(id_file, "r") as f:
        ids = json.load(f)
        
    if len(embeddings) < 15:
        logger.warning("Too few items for clustering.")
        return
        
    logger.info("Running HDBSCAN...")
    clusterer = hdbscan.HDBSCAN(min_cluster_size=15, min_samples=5)
    labels = clusterer.fit_predict(embeddings)
    
    clusters = {}
    emerging_themes = []
    
    for item_id, label in zip(ids, labels):
        label_int = int(label)
        if label_int == -1:
            emerging_themes.append(item_id)
        else:
            if label_int not in clusters:
                clusters[label_int] = []
            clusters[label_int].append(item_id)
            
    with open(out_dir / "clusters.json", "w") as f:
        json.dump({
            "clusters": clusters,
            "emerging_themes": emerging_themes
        }, f, indent=2)
        
    logger.info(f"Found {len(clusters)} valid clusters and {len(emerging_themes)} noise/emerging items.")

if __name__ == "__main__":
    run_clustering()
