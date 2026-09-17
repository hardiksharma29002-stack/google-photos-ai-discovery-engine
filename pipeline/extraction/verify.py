import re

def normalize_ws(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower()).strip()

def verify_extraction(raw_item: dict, extracted_item: dict) -> bool:
    # 1. Quote verification
    quote = extracted_item.get("evidence_quote", "")
    raw_text = raw_item.get("text", "")
    
    if quote and quote.lower() != "none" and len(quote) > 3:
        norm_quote = normalize_ws(quote)
        norm_raw = normalize_ws(raw_text)
        if norm_quote not in norm_raw:
            return False
            
    # 2. Example queries verification
    queries = extracted_item.get("example_queries", [])
    for q in queries:
        if normalize_ws(q) not in normalize_ws(raw_text):
            return False
            
    return True
