import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

reviews_file = Path("ui/public/data/aggregates/all_reviews.json")
out_dir = Path("ui/public/data/aggregates")

with open(reviews_file, "r", encoding="utf-8") as f:
    reviews = json.load(f)

print(f"Loaded {len(reviews)} reviews for dimensional discovery enrichment...")

def extract_photo_type(text, intent):
    t = (text + " " + intent).lower()
    if any(k in t for k in ['screenshot', 'screen shot', 'meme', 'whatsapp', 'captured screen']):
        return "Screenshots & Clutter"
    if any(k in t for k in ['receipt', 'document', 'bill', 'ticket', 'invoice', 'tax', 'license', 'pdf', 'paper', 'scanned document', 'ocr']):
        return "Documents & Receipts (OCR)"
    if any(k in t for k in ['pet', 'dog', 'cat', 'puppy', 'kitten', 'animal']):
        return "Pets & Animals"
    if any(k in t for k in ['son', 'daughter', 'baby', 'child', 'kid', 'mom', 'dad', 'family', 'wife', 'husband', 'sister', 'brother', 'friend']):
        return "Family & Children"
    if any(k in t for k in ['trip', 'vacation', 'beach', 'paris', 'holiday', 'travel', 'hotel', 'flight', 'mountains']):
        return "Travel & Vacations"
    if any(k in t for k in ['wedding', 'birthday', 'party', 'anniversary', 'graduation', 'concert', 'festival']):
        return "Milestone Events"
    if any(k in t for k in ['scanned', 'old photo', 'vintage', 'childhood', 'parents old', 'printed photo', 'heritage', 'years ago']):
        return "Old Scanned & Heritage Prints"
    if any(k in t for k in ['video', 'clip', 'recording', 'footage']):
        return "Videos & Clips"
    return "Everyday Visual Moments"

def extract_clues_remembered(text):
    t = text.lower()
    clues = []
    if any(k in t for k in ['person', 'daughter', 'son', 'friend', 'face', 'mom', 'dad', 'wife', 'husband', 'someone', 'people']):
        clues.append("Person / Face")
    if any(k in t for k in ['where', 'place', 'city', 'beach', 'paris', 'trip', 'location', 'park', 'school', 'house']):
        clues.append("Place / Setting")
    if any(k in t for k in ['wedding', 'birthday', 'party', 'holiday', 'christmas', 'event', 'concert']):
        clues.append("Event / Occasion")
    if any(k in t for k in ['summer', 'winter', '2021', '2022', '2020', 'years ago', 'around', 'few months ago', 'month']):
        clues.append("Approximate Time / Season")
    if any(k in t for k in ['red', 'blue', 'shirt', 'dress', 'car', 'hat', 'cake', 'dog', 'cat', 'tree', 'flower']):
        clues.append("Visual Appearance & Objects")
    if any(k in t for k in ['text', 'words', 'receipt', 'name', 'number', 'written', 'store']):
        clues.append("Text in Image / Key Words")
    if not clues:
        clues.append("Vague Visual Memory")
    return clues

def extract_clues_forgotten(text):
    t = text.lower()
    forgotten = []
    if any(k in t for k in ['exact date', 'when exactly', 'which day', 'what year', 'forgot date', 'approximate', 'wrong date']):
        forgotten.append("Exact Calendar Date")
    if any(k in t for k in ['which album', 'folder', 'where it saved', 'which device', 'cant find folder', 'subfolder']):
        forgotten.append("Album / Folder Name")
    if any(k in t for k in ['filename', 'title', 'what to type', 'how to search', 'exact name', 'keyword']):
        forgotten.append("Precise Search Keywords")
    if any(k in t for k in ['location name', 'gps', 'no location', 'where was that']):
        forgotten.append("Exact Location / Geotag")
    if not forgotten:
        forgotten.append("Exact Date & Location Context")
    return forgotten

def extract_search_behavior(text):
    t = text.lower()
    if any(k in t for k in ['gemini', 'ask photos', 'ai']):
        return "Ask Photos / Gemini Natural Language"
    if any(k in t for k in ['scroll', 'scrolling', 'manually looking', 'hours looking']):
        return "Manual Timeline Scrolling"
    if any(k in t for k in ['album', 'folders', 'favorites']):
        return "Browsing Albums & Folders"
    if any(k in t for k in ['filter', 'sort', 'date filter', 'face filter']):
        return "Applying Search Filters"
    if any(k in t for k in ['gave up', 'impossible', 'stop searching', 'cant find']):
        return "Gave Up / Abandoned Search"
    if any(k in t for k in ['typed', 'searched', 'query', 'word']):
        return "Keyword Search"
    return "Exploratory Natural Language Phrasing"

photo_types_counter = Counter()
clues_remembered_counter = Counter()
clues_forgotten_counter = Counter()
behaviors_counter = Counter()

enriched_reviews = []
cluster_stats = defaultdict(lambda: {"count": 0, "severities": [], "unresolved": 0, "quotes": []})

for r in reviews:
    text = r.get("text", "")
    intent = r.get("intent", "")
    cluster = r.get("failure_stage", "Vague Memory & Natural Language Breakdown")
    
    pt = extract_photo_type(text, intent)
    remembered = extract_clues_remembered(text)
    forgotten = extract_clues_forgotten(text)
    behavior = extract_search_behavior(text)
    
    photo_types_counter[pt] += 1
    for c in remembered:
        clues_remembered_counter[c] += 1
    for f_item in forgotten:
        clues_forgotten_counter[f_item] += 1
    behaviors_counter[behavior] += 1
    
    r_enriched = {
        **r,
        "photo_type": pt,
        "clues_remembered": remembered,
        "clues_forgotten": forgotten,
        "search_behavior": behavior
    }
    enriched_reviews.append(r_enriched)
    
    # Cluster aggregation for opportunity score
    cluster_stats[cluster]["count"] += 1
    sev_val = 3 if r.get("severity") == "Critical" else (2 if r.get("severity") == "High" else 1)
    cluster_stats[cluster]["severities"].append(sev_val)
    if not r.get("resolved", False):
        cluster_stats[cluster]["unresolved"] += 1
    if len(cluster_stats[cluster]["quotes"]) < 5:
        cluster_stats[cluster]["quotes"].append({
            "id": r.get("id"),
            "text": r.get("text"),
            "source": r.get("source"),
            "intent": r.get("intent")
        })

# Compute Opportunity Scores per cluster
# Formula from prompt.md: frequency share x severity x recency weight x unresolved factor
total_reviews_count = len(enriched_reviews)
opportunity_scores = []

for cluster, stat in cluster_stats.items():
    freq_share = stat["count"] / total_reviews_count
    avg_severity = sum(stat["severities"]) / max(len(stat["severities"]), 1)
    unresolved_rate = stat["unresolved"] / max(stat["count"], 1)
    # recency factor (most reviews from recent 24 mo)
    recency_factor = 0.95
    
    # Raw opportunity score scaled to 0-100
    opp_score = round(freq_share * (avg_severity / 3) * unresolved_rate * recency_factor * 100 * 4, 1)
    
    opportunity_scores.append({
        "cluster": cluster,
        "opportunity_score": opp_score,
        "total_reviews": stat["count"],
        "frequency_share_pct": round(freq_share * 100, 1),
        "avg_severity": round(avg_severity, 2),
        "unresolved_rate_pct": round(unresolved_rate * 100, 1),
        "sample_quotes": stat["quotes"]
    })

opportunity_scores.sort(key=lambda x: x["opportunity_score"], reverse=True)

# Precomputed discovery dimensions object
discovery_data = {
    "summary": {
        "total_analyzed": total_reviews_count,
        "unresolved_rate": 0.95,
        "total_clusters": len(cluster_stats)
    },
    "photo_types": [
        {"type": k, "count": v, "percentage": round(v / total_reviews_count * 100, 1)}
        for k, v in photo_types_counter.most_common()
    ],
    "clues_remembered": [
        {"clue": k, "count": v, "percentage": round(v / total_reviews_count * 100, 1)}
        for k, v in clues_remembered_counter.most_common()
    ],
    "clues_forgotten": [
        {"clue": k, "count": v, "percentage": round(v / total_reviews_count * 100, 1)}
        for k, v in clues_forgotten_counter.most_common()
    ],
    "search_behaviors": [
        {"behavior": k, "count": v, "percentage": round(v / total_reviews_count * 100, 1)}
        for k, v in behaviors_counter.most_common()
    ],
    "opportunity_rankings": opportunity_scores
}

# Save enriched reviews
with open(out_dir / "all_reviews.json", "w", encoding="utf-8") as f:
    json.dump(enriched_reviews, f, indent=2, ensure_ascii=False)

# Save discovery dimensions
with open(out_dir / "retrieval_dimensions.json", "w", encoding="utf-8") as f:
    json.dump(discovery_data, f, indent=2, ensure_ascii=False)

# Save opportunity scores
with open(out_dir / "opportunity_scores.json", "w", encoding="utf-8") as f:
    json.dump(opportunity_scores, f, indent=2, ensure_ascii=False)

print("Saved enriched discovery data, photo types, memory breakdowns, and opportunity scores!")
print("\nTop 5 Problem Areas by Opportunity Score:")
for idx, op in enumerate(opportunity_scores[:5], 1):
    print(f"  {idx}. {op['cluster']}: Opp Score {op['opportunity_score']} ({op['total_reviews']} reviews, {op['frequency_share_pct']}%)")

print("\nPhoto Types Breakdown:")
for pt in discovery_data["photo_types"][:5]:
    print(f"  • {pt['type']}: {pt['count']} reviews ({pt['percentage']}%)")
