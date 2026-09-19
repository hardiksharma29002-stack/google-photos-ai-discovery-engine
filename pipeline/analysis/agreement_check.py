import os
import sys
import json
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import DATA_DIR
from pipeline.utils import setup_logger
from pipeline.extraction.batch_extract import BatchExtractor

logger = setup_logger("AgreementCheck")

def run_agreement_check():
    core_file = DATA_DIR / "extracted" / "core.jsonl"
    out_dir = DATA_DIR / "audit"
    os.makedirs(out_dir, exist_ok=True)
    
    if not core_file.exists():
        logger.error("Core file missing.")
        return
        
    core_items = []
    with open(core_file, "r", encoding="utf-8") as f:
        for line in f: core_items.append(json.loads(line))
        
    sample = random.sample(core_items, min(100, len(core_items)))
    
    logger.info("Initializing Groq agreement model...")
    extractor = BatchExtractor(provider="groq")
    
    agreements = 0
    total = 0
    
    batch = []
    batch_size = 10
    
    def process(b):
        nonlocal agreements, total
        if not b: return
        results = extractor.extract(b)
        for i, original in enumerate(b):
            if i < len(results):
                groq_result = results[i]
                orig_fs = original.get("failure_stage", [])
                groq_fs = groq_result.get("failure_stage", [])
                
                if orig_fs and groq_fs and orig_fs[0] == groq_fs[0]:
                    agreements += 1
                total += 1
                
    for item in sample:
        raw_item = {
            "id": item["id"],
            "text": item.get("original_text", ""),
            "thread_context": item.get("thread_context", ""),
            "failure_stage": item.get("failure_stage")
        }
        batch.append(raw_item)
        if len(batch) >= batch_size:
            process(batch)
            batch = []
            
    if batch:
        process(batch)
        
    agreement_rate = (agreements / total) * 100 if total > 0 else 0
    
    with open(out_dir / "agreement_report.json", "w") as f:
        json.dump({
            "total_checked": total,
            "agreements": agreements,
            "agreement_rate": round(agreement_rate, 2),
            "primary_model": "gemini-2.5-flash",
            "agreement_model": "groq/compound-mini"
        }, f, indent=2)
        
    logger.info(f"Agreement check complete. Agreement rate: {agreement_rate:.1f}%")

if __name__ == "__main__":
    run_agreement_check()
