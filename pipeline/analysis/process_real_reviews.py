import json
import re
from collections import Counter
from pathlib import Path

prefiltered_file = Path("data/processed/prefiltered.jsonl")
output_file = Path("ui/public/data/aggregates/all_reviews.json")
stages_file = Path("ui/public/data/aggregates/failure_stages.json")
evidence_file = Path("ui/public/data/aggregates/evidence.json")
base_aggs_file = Path("ui/public/data/aggregates/base_aggregates.json")

def classify_stage(text):
    t = text.lower()
    if any(k in t for k in ['gemini', 'ask photos', 'ai search', 'ai update', 'ai feature']):
        return 'Ask Photos / Gemini AI Regressions'
    if any(k in t for k in ['receipt', 'document', 'text in photo', 'ocr', 'ticket', 'invoice', 'license', 'scanned', 'bill']):
        return 'Document, Receipt & Text (OCR) Inaccuracies'
    if any(k in t for k in ['face group', 'face recognition', 'people & pets', 'pet', 'recognize face', 'wrong person', 'dog', 'cat']):
        return 'Face Recognition & Pet Grouping Errors'
    if any(k in t for k in ['date', 'timeline', 'year', 'month', '1970', 'timestamp', 'chronological', 'order', 'scroll timeline']):
        return 'Date & Timeline Desynchronization (Wrong Year/Date)'
    if any(k in t for k in ['shared album', 'which album', 'album', 'not in album']):
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
    workaround_keywords = ['scrolled', 'manually', 'third party', 'another app', 'workaround', 'gallery', 'eventually found', 'found it after']
    if any(k in t for k in workaround_keywords):
        return True # resolved via workaround
    return False # unresolved / gave up

processed_reviews = []
stages_counter = Counter()
evidence_map = {}
unresolved_count = 0

with open(prefiltered_file, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, start=1):
        item = json.loads(line)
        text = item.get("text", "").strip()
        if not text:
            continue
            
        # Clean text
        text_clean = " ".join(text.split())
        source_raw = item.get("source", "google_play")
        source_display = "Play Store" if source_raw == "google_play" else "YouTube"
        
        date_raw = item.get("date", "2026-06-01")
        date_display = date_raw.split("T")[0] if "T" in str(date_raw) else str(date_raw)[:10]
        
        stage = classify_stage(text_clean)
        intent = deduce_intent(text_clean)
        severity = deduce_severity(item.get("rating"), text_clean)
        is_resolved = deduce_resolution(text_clean)
        
        if not is_resolved:
            unresolved_count += 1
            
        stages_counter[stage] += 1
        
        if stage not in evidence_map:
            evidence_map[stage] = []
        if len(evidence_map[stage]) < 5 and len(text_clean) > 30 and len(text_clean) < 250:
            evidence_map[stage].append(text_clean)
            
        processed_reviews.append({
            "id": item.get("id", f"REV-{str(idx).zfill(5)}"),
            "source": source_display,
            "date": date_display,
            "text": text_clean,
            "intent": intent,
            "stage": stage,
            "severity": severity
        })

print(f"Processed {len(processed_reviews)} real reviews.")
print(f"Unresolved count: {unresolved_count} / {len(processed_reviews)} ({(unresolved_count/len(processed_reviews))*100:.1f}%)")
print("Stages distribution:")
for s, c in stages_counter.most_common():
    print(f"  {s}: {c}")

# Save real reviews
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(processed_reviews, f, indent=2)

# Save failure stages
with open(stages_file, "w", encoding="utf-8") as f:
    json.dump(dict(stages_counter.most_common()), f, indent=2)

# Save evidence quotes
with open(evidence_file, "w", encoding="utf-8") as f:
    json.dump(evidence_map, f, indent=2)

# Save base aggregates
base_aggs = {
    "total_items": len(processed_reviews),
    "total_clusters": len(stages_counter),
    "unresolved_rate": round(unresolved_count / len(processed_reviews), 2)
}
with open(base_aggs_file, "w", encoding="utf-8") as f:
    json.dump(base_aggs, f, indent=2)

print("Saved all real review aggregates successfully.")
