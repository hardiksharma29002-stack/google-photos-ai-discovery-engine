import os
from pathlib import Path

# Paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"

# Collection Parameters
COUNTRIES = ["in"]

SEED_PHRASES = [
    "can't find", "cannot find", "couldn't find",
    "search not working", "search useless", "search broken", "search worse",
    "used to be able to search", "find old photo", "don't remember when",
    "which album", "scroll timeline", "search by date", "search by location",
    "search by person", "face group", "people & pets",
    "ask photos", "gemini", "natural language search",
    "describe the photo", "screenshot", "receipt", "document", "text in photo",
    "wrong results", "irrelevant results", "too many results",
    "filter", "sort", "google photos search",
    "google photos can't find photo", "find old photos google photos",
    "google photos ask photos", "google photos search not working",
]

YOUTUBE_DAILY_BUDGET = 9000  # units
DATE_WINDOW_MONTHS = 6

# Create directories if they don't exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
