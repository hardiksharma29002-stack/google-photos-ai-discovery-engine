import json
import logging
import hashlib
from typing import Dict, Any, List
from .config import CHECKPOINT_DIR

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def save_checkpoint(source: str, state: Dict[str, Any]):
    path = CHECKPOINT_DIR / f"{source}_checkpoint.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)

def load_checkpoint(source: str) -> Dict[str, Any]:
    path = CHECKPOINT_DIR / f"{source}_checkpoint.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def append_jsonl(filepath, item: Dict[str, Any]):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def generate_id(source: str, identifier: str) -> str:
    """Generate a short unique ID for an item."""
    hash_object = hashlib.md5(identifier.encode())
    return f"{source}-{hash_object.hexdigest()[:8]}"
