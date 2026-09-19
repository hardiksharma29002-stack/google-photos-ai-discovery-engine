import os
import sys
import json
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import DATA_DIR
from pipeline.utils import setup_logger

logger = setup_logger("AuditGenerator")

def generate_audit():
    core_file = DATA_DIR / "extracted" / "core.jsonl"
    rejected_file = DATA_DIR / "extracted" / "rejected.jsonl"
    out_dir = DATA_DIR / "audit"
    os.makedirs(out_dir, exist_ok=True)
    
    core_items = []
    if core_file.exists():
        with open(core_file, "r", encoding="utf-8") as f:
            for line in f: core_items.append(json.loads(line))
            
    rejected_items = []
    if rejected_file.exists():
        with open(rejected_file, "r", encoding="utf-8") as f:
            for line in f: rejected_items.append(json.loads(line))
            
    sample_core = random.sample(core_items, min(70, len(core_items)))
    sample_rej = random.sample(rejected_items, min(30, len(rejected_items)))
    
    audit_set = sample_core + sample_rej
    random.shuffle(audit_set)
    
    html = ["<html><head><style>body{font-family:sans-serif;} td{padding:8px;}</style></head><body><h1>AI Extraction Audit</h1><table border='1' style='border-collapse:collapse;'>"]
    html.append("<tr><th>ID</th><th>Original Text</th><th>Extracted Rel & Failure</th><th>Agree? (Check if YES)</th></tr>")
    
    for item in audit_set:
        rel = item.get("relevance", "unknown")
        fs = ", ".join(item.get("failure_stage", []))
        text = item.get("original_text", "")
        html.append(f"<tr><td>{item['id']}</td><td>{text}</td><td><b>{rel}</b><br/>{fs}</td><td><input type='checkbox' style='width:24px;height:24px;'></td></tr>")
        
    html.append("</table></body></html>")
    
    with open(out_dir / "audit.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html))
        
    logger.info("Audit HTML generated at data/audit/audit.html")

if __name__ == "__main__":
    generate_audit()
