import os
import sys
import json
import hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.extraction.llm_client import ExtractionClient
from pipeline.utils import setup_logger

logger = setup_logger("BatchExtractor")

PROMPT_TEMPLATE = """
You are analyzing user feedback for Google Photos.
We are only interested in issues where users are trying to FIND or RE-FIND photos they already have.
Analyze the following batch of JSON items. For each item, return the structured extraction.

Batch of Items:
{items}
"""

class BatchExtractor:
    def __init__(self, provider="gemini"):
        self.client = ExtractionClient(provider=provider)
        
    def extract(self, batch: list) -> list:
        prompt_items = []
        for item in batch:
            prompt_items.append({
                "id": item["id"],
                "text": item["text"],
                "context": item.get("thread_context", "")
            })
            
        prompt = PROMPT_TEMPLATE.format(items=json.dumps(prompt_items, indent=2))
        
        try:
            response_json = self.client.extract_batch(prompt)
            extracted_items = response_json.get("items", [])
            
            if len(extracted_items) == len(batch):
                for i, ext in enumerate(extracted_items):
                    ext["id"] = batch[i]["id"]
            return extracted_items
        except Exception as e:
            logger.error(f"Batch extraction failed completely: {e}")
            return []
