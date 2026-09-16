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

def collect_app_store():
    print("[1/2] Collecting Apple App Store reviews for Google Photos...")
    out_file = RAW_DIR / "app_store.jsonl"
    app_id = "962194608"
    countries = ["us", "gb", "ca", "au", "in", "de", "fr", "jp", "sg", "ph", "nl", "br"]
    
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
        for country in countries:
            country_count = 0
            for page in range(1, 11):
                url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
                try:
                    res = requests.get(url, headers=HEADERS, timeout=8)
                    if res.status_code != 200:
                        break
                    data = res.json()
                    entries = data.get("feed", {}).get("entry", [])
                    if not entries:
                        break
                    
                    for entry in entries:
                        # Skip app info entry
                        if "author" not in entry or "content" not in entry:
                            continue
                        
                        review_id = f"appstore-{entry.get('id', {}).get('label', '')}"
                        if review_id in seen_ids:
                            continue
                        
                        author = entry.get("author", {}).get("name", {}).get("label", "App Store User")
                        title = entry.get("title", {}).get("label", "")
                        content = entry.get("content", {}).get("label", "")
                        rating = int(entry.get("im:rating", {}).get("label", 0))
                        updated = entry.get("updated", {}).get("label", "")
                        
                        dt = updated[:10] if updated else datetime.now().strftime("%Y-%m-%d")
                        combined_text = f"{title}: {content}" if title else content
                        
                        item = {
                            "id": review_id,
                            "source": "App Store",
                            "country": country,
                            "date": dt,
                            "text": combined_text,
                            "rating": rating,
                            "userName": author,
                            "metadata": {
                                "title": title,
                                "country": country
                            }
                        }
                        out.write(json.dumps(item, ensure_ascii=False) + "\n")
                        seen_ids.add(review_id)
                        country_count += 1
                        collected_count += 1
                except Exception as e:
                    pass
                time.sleep(0.1)
            print(f"  - {country.upper()}: collected {country_count} reviews")
    
    print(f"App Store total collection: {len(seen_ids)} reviews in {out_file}")

def collect_google_community():
    print("[2/2] Collecting Google Photos Help Community discussions...")
    out_file = RAW_DIR / "google_community.jsonl"
    
    queries = [
        "search not working", "can't find photo", "cannot find old photos",
        "search broken", "gemini ask photos", "face recognition wrong",
        "face grouping missing", "album photos not showing", "timeline wrong date",
        "screenshot not searching", "document receipt text ocr", "duplicate photos",
        "search by date", "search by location", "filter search results",
        "cannot find receipt", "can't search text", "google photos search useless",
        "archive folder search", "hidden photos search", "video search inside",
        "ask photos wrong answers", "classic search vs gemini", "search returns nothing"
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
                res = requests.get(url, headers=HEADERS, timeout=10)
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
                        # Clean up text from vote counters
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
                            "userName": f"Community Member {tid[-4:]}",
                            "metadata": {
                                "thread_id": tid,
                                "search_query": q,
                                "url": f"https://support.google.com/photos/thread/{tid}"
                            }
                        }
                        out.write(json.dumps(item, ensure_ascii=False) + "\n")
                        seen_ids.add(item_id)
                        query_count += 1
                        collected_count += 1
            except Exception as e:
                pass
            print(f"  - '{q}': found {query_count} discussions")
            time.sleep(0.2)
            
    print(f"Google Community total collection: {len(seen_ids)} threads in {out_file}")

if __name__ == "__main__":
    collect_app_store()
    collect_google_community()
