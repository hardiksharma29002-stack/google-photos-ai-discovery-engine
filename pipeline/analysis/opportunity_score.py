import os
import sys
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import DATA_DIR
from pipeline.utils import setup_logger

logger = setup_logger("OpportunityScore")

def run_opportunity_scoring():
    core_file = DATA_DIR / "extracted" / "core.jsonl"
    clusters_file = DATA_DIR / "clusters" / "clusters.json"
    out_dir = DATA_DIR / "aggregates"
    os.makedirs(out_dir, exist_ok=True)
    
    if not core_file.exists() or not clusters_file.exists():
        logger.error("Required files missing.")
        return
        
    core_items = {}
    with open(core_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            core_items[item["id"]] = item
            
    with open(clusters_file, "r") as f:
        cluster_data = json.load(f)
        
    total_items = len(core_items)
    scores = {}
    
    for cluster_id, member_ids in cluster_data.get("clusters", {}).items():
        n = len(member_ids)
        freq_share = n / total_items if total_items > 0 else 0
        
        total_severity = 0
        total_recency = 0
        total_unresolved = 0
        
        for mid in member_ids:
            item = core_items.get(mid, {})
            
            total_severity += item.get("severity", 1)
            
            # Recency Weight
            date_str = item.get("date", "")
            recency = 0.5 # default 12-24
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str)
                    months_old = (datetime.now() - dt).days / 30
                    if months_old <= 6:
                        recency = 1.0
                    elif months_old <= 12:
                        recency = 0.75
                except ValueError:
                    pass
            total_recency += recency
            
            # Unresolved Factor
            outcome = item.get("outcome", "unknown")
            if outcome in ["gave_up", "not_found"]:
                total_unresolved += 1.0
            elif outcome == "found_after_workaround":
                total_unresolved += 0.6
                
        avg_sev = total_severity / n
        avg_rec = total_recency / n
        unresolved_factor = total_unresolved / n
        
        score = freq_share * avg_sev * avg_rec * unresolved_factor
        
        scores[cluster_id] = {
            "n": n,
            "frequency_share": round(freq_share, 4),
            "avg_severity": round(avg_sev, 2),
            "recency_weight": round(avg_rec, 2),
            "unresolved_factor": round(unresolved_factor, 2),
            "opportunity_score": round(score, 4),
            "confident": n >= 30
        }
        
    with open(out_dir / "opportunity_scores.json", "w") as f:
        json.dump(scores, f, indent=2)
        
    logger.info(f"Opportunity scores calculated for {len(scores)} clusters.")

if __name__ == "__main__":
    run_opportunity_scoring()
