import os
import sys
import json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import DATA_DIR
from pipeline.utils import setup_logger

logger = setup_logger("Aggregates")

def compute_aggregates():
    in_file = DATA_DIR / "extracted" / "core.jsonl"
    out_dir = DATA_DIR / "aggregates"
    os.makedirs(out_dir, exist_ok=True)
    
    if not in_file.exists():
        logger.error(f"{in_file} does not exist.")
        return
        
    counts_per_source = defaultdict(int)
    failure_stage_dist = defaultdict(int)
    outcomes = defaultdict(int)
    
    total = 0
    with open(in_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            total += 1
            counts_per_source[item.get("source", "unknown")] += 1
            
            fs = item.get("failure_stage", [])
            primary_fs = fs[0] if fs else "unknown"
            failure_stage_dist[primary_fs] += 1
            
            outcome = item.get("outcome", "unknown")
            outcomes[outcome] += 1
            
    aggs = {
        "total_core_items": total,
        "counts_per_source": dict(counts_per_source),
        "failure_stage_dist": dict(failure_stage_dist),
        "outcomes": dict(outcomes)
    }
    
    with open(out_dir / "base_aggregates.json", "w") as f:
        json.dump(aggs, f, indent=2)
        
    logger.info(f"Aggregates computed for {total} items.")

if __name__ == "__main__":
    compute_aggregates()
