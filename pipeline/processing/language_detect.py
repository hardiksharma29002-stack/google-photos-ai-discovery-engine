import os
import sys
import json
from langdetect import detect, LangDetectException
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import PROCESSED_DIR
from pipeline.utils import setup_logger, append_jsonl

logger = setup_logger("LanguageDetect")

def detect_language(text):
    if not text or len(text.strip()) < 3:
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

def run_language_detection():
    in_file = PROCESSED_DIR / "normalised.jsonl"
    out_file = PROCESSED_DIR / "lang_filtered.jsonl"
    
    if out_file.exists():
        out_file.unlink()
        
    if not in_file.exists():
        logger.error(f"{in_file} does not exist. Run normalise.py first.")
        return
        
    total = 0
    kept = 0
    
    ALLOWED_LANGS = {'en', 'hi', 'unknown'}
    
    with open(in_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            total += 1
            
            lang = detect_language(item["text"])
            item["language"] = lang
            
            if lang in ALLOWED_LANGS:
                append_jsonl(out_file, item)
                kept += 1
                
    logger.info(f"Language detection complete. Kept {kept}/{total} items ({(kept/total)*100 if total > 0 else 0:.1f}%)")

if __name__ == "__main__":
    run_language_detection()
