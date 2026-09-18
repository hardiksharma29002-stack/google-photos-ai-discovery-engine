import json
import re
from collections import Counter
from pathlib import Path

raw_play_file = Path("data/raw/google_play.jsonl")
raw_appstore_file = Path("data/raw/app_store.jsonl")
raw_community_file = Path("data/raw/google_community.jsonl")

output_file = Path("ui/public/data/aggregates/all_reviews.json")
stages_file = Path("ui/public/data/aggregates/failure_stages.json")
evidence_file = Path("ui/public/data/aggregates/evidence.json")
base_aggs_file = Path("ui/public/data/aggregates/base_aggregates.json")

SEED_KEYWORDS = [
    "search", "can't find", "cannot find", "couldn't find",
    "find photo", "find old", "which album", "scroll timeline",
    "by date", "by location", "by person", "face group", "people & pets",
    "ask photos", "gemini", "natural language", "receipt", "document",
    "text in photo", "ocr", "screenshot", "wrong results", "filter", "sort",
    "archive", "locked folder", "video search", "duplicate"
]

def classify_stage(text):
    t = text.lower()
    if any(k in t for k in ['gemini', 'ask photos', 'ai search', 'ai update', 'ai feature', 'loop back']):
        return 'Ask Photos / Gemini AI Regressions'
    if any(k in t for k in ['receipt', 'document', 'text in photo', 'ocr', 'ticket', 'invoice', 'license', 'scanned', 'bill']):
        return 'Document, Receipt & Text (OCR) Inaccuracies'
    if any(k in t for k in ['face group', 'face recognition', 'people & pets', 'pet', 'recognize face', 'wrong person', 'dog', 'cat']):
        return 'Face Recognition & Pet Grouping Errors'
    if any(k in t for k in ['date', 'timeline', 'year', 'month', '1970', 'timestamp', 'chronological', 'order', 'scroll timeline']):
        return 'Date & Timeline Desynchronization (Wrong Year/Date)'
    if any(k in t for k in ['shared album', 'which album', 'album', 'not in album', 'albums']):
        return 'Album vs. Main Library Disconnection'
    if any(k in t for k in ['hidden', 'archive', 'locked folder', 'trash', 'bin', 'secret', 'vault']):
        return 'Hidden & Archived Folder Search Blindness'
    if any(k in t for k in ['location', 'search by location', 'gps', 'geotag', 'city', 'country', 'map', 'place']):
        return 'Missing Location & Geotag Failures'
    if any(k in t for k in ['video', 'clip', 'recording', 'footage', 'movie']):
        return 'Video Content & In-Video Action Search'
    if any(k in t for k in ['duplicate', 'burst', 'same photo', 'repeats', 'identical']):
        return 'Duplicate & Burst Photo Flooding'
    if any(k in t for k in ['offline', 'airplane', 'no connection', 'data connection', 'wifi', 'internet']):
        return 'Offline / Flight Mode Search Inaccessibility'
    if any(k in t for k in ['filter', 'refine', 'sort', 'narrow down', 'too many results']):
        return 'Inability to Refine / Multi-Condition Queries'
    if any(k in t for k in ['clutter', 'irrelevant', 'meme', 'screenshot', 'junk', 'wrong results', 'mess']):
        return 'Search Query Visual Clutter (Irrelevant Memes & Noise)'
    if any(k in t for k in ["can't find", "cannot find", "couldn't find", "no results", "zero results", "nothing found", "not working", "useless", "broken"]):
        return 'Search Retrieval Failure (Zero Results Found)'
    return 'Vague Memory & Natural Language Breakdown'

def deduce_intent(text):
    t = text.lower()
    if any(k in t for k in ['dog', 'cat', 'pet', 'animal', 'puppy', 'kitten']):
        return "Find pet/animal photos"
    if any(k in t for k in ['son', 'daughter', 'wife', 'husband', 'kid', 'child', 'baby', 'mother', 'mom', 'dad', 'family', 'friend', 'face', 'person']):
        return "Find specific person / family member"
    if any(k in t for k in ['receipt', 'bill', 'document', 'ticket', 'invoice', 'license', 'passport', 'id', 'tax']):
        return "Find document / receipt / proof"
    if any(k in t for k in ['trip', 'vacation', 'beach', 'paris', 'holiday', 'travel', 'flight', 'hotel']):
        return "Find vacation / travel photos"
    if any(k in t for k in ['screenshot', 'meme', 'whatsapp', 'download']):
        return "Find specific screenshot or downloaded image"
    if any(k in t for k in ['wedding', 'birthday', 'party', 'anniversary', 'concert', 'festival', 'event', 'graduation']):
        return "Find milestone event photos"
    if any(k in t for k in ['video', 'clip', 'recording']):
        return "Find specific video clip"
    if any(k in t for k in ['album', 'folder', 'shared']):
        return "Locate photos in album / folder"
    if any(k in t for k in ['gemini', 'ask photos']):
        return "Ask natural language query via Gemini"
    if any(k in t for k in ['year', 'month', 'old', 'date', '2019', '2020', '2021', '2022', '2023', '2024']):
        return "Find photos from specific time/year"
    return "Find specific visual memory"

def deduce_severity(rating, text):
    t = text.lower()
    if rating == 1 or any(k in t for k in ['terrible', 'horrible', 'useless', 'broken', 'ruined', 'worst', 'hate', 'fail', 'garbage', 'unusable']):
        return "Critical"
    if rating == 2 or any(k in t for k in ['annoying', 'frustrating', 'disappointed', 'issue', 'bad', 'pain', 'difficult']):
        return "High"
    if rating == 3 or any(k in t for k in ['please fix', 'could be better', 'used to be', 'sometimes']):
        return "Medium"
    return "Low"

def deduce_resolution(text):
    t = text.lower()
    workaround_keywords = ['scrolled', 'manually', 'third party', 'another app', 'workaround', 'gallery', 'eventually found', 'found it after', 'switched to']
    if any(k in t for k in workaround_keywords):
        return True
    return False

processed_reviews = []
stages_counter = Counter()
evidence_map = {}
source_counts = Counter()
unresolved_count = 0
seen_texts = set()

# 1. Process Google Play reviews (match against retrieval keywords)
if raw_play_file.exists():
    with open(raw_play_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                text = item.get("text", "").strip()
                if not text or len(text) < 15:
                    continue
                t_lower = text.lower()
                if not any(k in t_lower for k in SEED_KEYWORDS):
                    continue
                # Skip duplicate texts
                clean_t = " ".join(text.split())
                if clean_t in seen_texts:
                    continue
                seen_texts.add(clean_t)

                date_val = item.get("date", "2026-06-01")[:10]
                stage = classify_stage(text)
                intent = deduce_intent(text)
                rating = item.get("rating", 1)
                severity = deduce_severity(rating, text)
                resolved = deduce_resolution(text)
                if not resolved:
                    unresolved_count += 1

                rev_id = item.get("id") or f"play-{len(processed_reviews)+1}"
                entry = {
                    "id": rev_id,
                    "source": "Play Store",
                    "date": date_val,
                    "text": clean_t,
                    "rating": rating,
                    "userName": item.get("userName", "Google User"),
                    "intent": intent,
                    "failure_stage": stage,
                    "severity": severity,
                    "workaround_attempted": resolved,
                    "resolved": resolved
                }
                processed_reviews.append(entry)
                stages_counter[stage] += 1
                source_counts["Play Store"] += 1

                if stage not in evidence_map:
                    evidence_map[stage] = []
                if len(evidence_map[stage]) < 10:
                    evidence_map[stage].append({
                        "id": rev_id,
                        "text": clean_t,
                        "intent": intent,
                        "source": "Play Store"
                    })
            except Exception:
                pass

# 2. Process Apple App Store reviews
if raw_appstore_file.exists():
    with open(raw_appstore_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                text = item.get("text", "").strip()
                if not text or len(text) < 15:
                    continue
                t_lower = text.lower()
                # If rating <= 3 or mentions search/retrieval keywords
                is_retrieval = any(k in t_lower for k in SEED_KEYWORDS) or item.get("rating", 5) <= 2
                if not is_retrieval:
                    continue
                clean_t = " ".join(text.split())
                if clean_t in seen_texts:
                    continue
                seen_texts.add(clean_t)

                date_val = item.get("date", "2026-06-01")[:10]
                stage = classify_stage(text)
                intent = deduce_intent(text)
                rating = item.get("rating", 1)
                severity = deduce_severity(rating, text)
                resolved = deduce_resolution(text)
                if not resolved:
                    unresolved_count += 1

                rev_id = item.get("id") or f"appstore-{len(processed_reviews)+1}"
                entry = {
                    "id": rev_id,
                    "source": "App Store",
                    "date": date_val,
                    "text": clean_t,
                    "rating": rating,
                    "userName": item.get("userName", "iOS User"),
                    "intent": intent,
                    "failure_stage": stage,
                    "severity": severity,
                    "workaround_attempted": resolved,
                    "resolved": resolved
                }
                processed_reviews.append(entry)
                stages_counter[stage] += 1
                source_counts["App Store"] += 1

                if stage not in evidence_map:
                    evidence_map[stage] = []
                if len(evidence_map[stage]) < 10:
                    evidence_map[stage].append({
                        "id": rev_id,
                        "text": clean_t,
                        "intent": intent,
                        "source": "App Store"
                    })
            except Exception:
                pass

# 3. Process Google Photos Help Community threads
if raw_community_file.exists():
    with open(raw_community_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                text = item.get("text", "").strip()
                if not text or len(text) < 15:
                    continue
                clean_t = " ".join(text.split())
                if clean_t in seen_texts:
                    continue
                seen_texts.add(clean_t)

                date_val = item.get("date", "2026-06-01")[:10]
                stage = classify_stage(text)
                intent = deduce_intent(text)
                rating = 1
                severity = "Critical"
                resolved = False
                unresolved_count += 1

                rev_id = item.get("id") or f"community-{len(processed_reviews)+1}"
                entry = {
                    "id": rev_id,
                    "source": "Google Photos Community",
                    "date": date_val,
                    "text": clean_t,
                    "rating": rating,
                    "userName": item.get("userName", "Community User"),
                    "intent": intent,
                    "failure_stage": stage,
                    "severity": severity,
                    "workaround_attempted": False,
                    "resolved": False
                }
                processed_reviews.append(entry)
                stages_counter[stage] += 1
                source_counts["Google Photos Community"] += 1

                if stage not in evidence_map:
                    evidence_map[stage] = []
                if len(evidence_map[stage]) < 10:
                    evidence_map[stage].append({
                        "id": rev_id,
                        "text": clean_t,
                        "intent": intent,
                        "source": "Google Photos Community"
                    })
            except Exception:
                pass

print(f"Total processed reviews: {len(processed_reviews)}")
print(f"Sources: {dict(source_counts)}")
print(f"Top 5 clusters:")
for st, cnt in stages_counter.most_common(5):
    print(f"  - {st}: {cnt} reviews ({cnt/len(processed_reviews)*100:.1f}%)")

# Write out JSON files
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(processed_reviews, f, indent=2, ensure_ascii=False)

stages_ordered = dict(stages_counter.most_common())
with open(stages_file, "w", encoding="utf-8") as f:
    json.dump(stages_ordered, f, indent=2, ensure_ascii=False)

with open(evidence_file, "w", encoding="utf-8") as f:
    json.dump(evidence_map, f, indent=2, ensure_ascii=False)

unresolved_rate = round(unresolved_count / max(len(processed_reviews), 1), 2)
base_aggs = {
    "total_reviews": len(processed_reviews),
    "total_items": len(processed_reviews),
    "total_clusters": len(stages_counter),
    "unresolved_rate": unresolved_rate,
    "sources": dict(source_counts)
}
with open(base_aggs_file, "w", encoding="utf-8") as f:
    json.dump(base_aggs, f, indent=2, ensure_ascii=False)

print(f"Successfully generated all aggregate files in ui/public/data/aggregates/")
