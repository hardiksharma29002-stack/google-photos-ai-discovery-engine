import os
import sys
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def collect_google_community():
    print("Collecting Google Photos Help Community discussions...", flush=True)
    out_file = RAW_DIR / "google_community.jsonl"
    
    queries = [
        "search", "can't find photo", "cannot find old photos",
        "search broken", "gemini", "ask photos", "face recognition",
        "face grouping", "album", "timeline", "wrong date",
        "screenshot", "receipt", "document", "ocr", "duplicate",
        "search by date", "search by location", "filter search",
        "archive folder", "locked folder", "video search",
        "photos missing", "photos disappeared", "search not working"
    ]
    
    seen_ids = set()
    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    seen_ids.add(data.get("id"))
                except Exception:
                    pass
                    
    collected_count = 0
    with open(out_file, "a", encoding="utf-8") as out:
        for q in queries:
            query_count = 0
            url = f"https://support.google.com/photos/threads?hl=en&max_results=30&q={requests.utils.quote(q)}"
            try:
                res = requests.get(url, headers=HEADERS, timeout=8)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    links = soup.find_all("a", href=re.compile(r'/photos/thread/(\d+)'))
                    for l in links:
                        href = l.get("href", "")
                        match = re.search(r'/photos/thread/(\d+)', href)
                        if not match:
                            continue
                        tid = match.group(1)
                        item_id = f"community-{tid}"
                        if item_id in seen_ids:
                            continue
                        
                        raw_text = l.get_text(separator=" ", strip=True)
                        cleaned_text = re.sub(r'\d+\s+(Recommended Answers?|Relevant Answers?|Replies?|Upvotes?)', '', raw_text).strip()
                        if len(cleaned_text) < 15:
                            continue
                        
                        item = {
                            "id": item_id,
                            "source": "Google Photos Community",
                            "country": "global",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "text": cleaned_text,
                            "rating": 1,
                            "userName": f"Community User {tid[-4:]}",
                            "metadata": {
                                "thread_id": tid,
                                "search_query": q,
                                "url": f"https://support.google.com/photos/thread/{tid}"
                            }
                        }
                        out.write(json.dumps(item, ensure_ascii=False) + "\n")
                        out.flush()
                        seen_ids.add(item_id)
                        query_count += 1
                        collected_count += 1
            except Exception as e:
                pass
            print(f"Query '{q}': {query_count} threads added (Total: {len(seen_ids)})", flush=True)
            time.sleep(0.1)
            
    print(f"Finished. Total Google Photos Community records: {len(seen_ids)}", flush=True)

if __name__ == "__main__":
    collect_google_community()
