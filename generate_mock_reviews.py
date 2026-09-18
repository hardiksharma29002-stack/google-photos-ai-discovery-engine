import json
import random
from datetime import datetime, timedelta

sources = ["Play Store", "App Store", "YouTube"]
intents = [
    "Find specific event/time", "Find pet/object", "Find recent trip", 
    "Find document", "Find specific person", "Find shared memory", 
    "Find location", "Find hidden/archived photo", "Find spouse",
    "Find old screenshot", "Search by visual description", "Find concert ticket"
]
stages = [
    "Search Retrieval Failure", "Missing Metadata", "Irrelevant Results", 
    "Face Recognition Failure", "Album Organization Confusion", "Semantic Misunderstanding"
]
severities = ["Critical", "High", "Medium", "Low"]

templates = [
    "I searched for '{keyword}' and got literally zero results, even though I know I took hundreds of photos that day.",
    "Type '{keyword}' into the search bar, it says no results found. My entire camera roll is {keyword}.",
    "All my photos from my {keyword} trip are showing up in 2014 instead of 2024. Now I can't search for them.",
    "I search for '{keyword}' and it shows me 500 memes and screenshots of texts. Completely useless.",
    "It grouped my newborn son with my 5-year-old nephew. Now when I search for my son, it's a mix of both kids.",
    "I added photos to a shared album, but when I search my own library they don't show up. Where did they go?",
    "I search for '{keyword}' and it misses half my photos because the location tags randomly disappeared.",
    "The search results are so cluttered. I asked for '{keyword}' and it showed me every photo that has a road in it.",
    "Search doesn't look inside hidden folders or archived albums, which is incredibly frustrating.",
    "Face grouping just stopped working entirely for my wife. I can't search her name anymore.",
    "Trying to find my {keyword} receipt from last month is impossible, it keeps showing me pictures of white walls.",
    "I literally typed '{keyword}' and it gave me pictures of completely unrelated things from 5 years ago."
]

keywords = ["beach sunset", "dog", "Paris", "receipts", "car", "New York", "passport", "concert", "vacation", "cat", "wedding"]

reviews = []
start_date = datetime(2026, 3, 1)

for i in range(1, 1285):
    source = random.choices(sources, weights=[65, 15, 20])[0] # play store mostly
    date = start_date + timedelta(days=random.randint(0, 180))
    template = random.choice(templates)
    keyword = random.choice(keywords)
    text = template.format(keyword=keyword)
    
    intent = random.choice(intents)
    stage = random.choice(stages)
    
    if stage == "Search Retrieval Failure":
        severity = random.choice(["High", "Critical"])
    elif stage == "Missing Metadata":
        severity = random.choice(["Medium", "High"])
    else:
        severity = random.choice(["Low", "Medium", "High"])
        
    reviews.append({
        "id": f"REV-{str(i).zfill(4)}",
        "source": source,
        "date": date.strftime("%Y-%m-%d"),
        "text": text,
        "intent": intent,
        "stage": stage,
        "severity": severity
    })

with open("ui/public/data/aggregates/all_reviews.json", "w") as f:
    json.dump(reviews, f, indent=2)

print("Generated 1284 reviews.")
