import os
import json
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google import genai
from google.genai import types
from groq import Groq
from pipeline.extraction.schema import BatchExtractionResponse

logger = logging.getLogger("LLMClient")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class RateLimitError(Exception):
    pass

class ExtractionClient:
    def __init__(self, provider="gemini"):
        self.provider = provider
        
        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set")
            self.client = genai.Client(api_key=api_key)
            self.model = os.getenv("LLM_EXTRACTION_MODEL", "gemini-2.5-flash")
            
        elif self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set")
            self.client = Groq(api_key=api_key)
            self.model = os.getenv("LLM_AGREEMENT_MODEL", "llama-3.1-8b-instant")
            
    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=30),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(RateLimitError)
    )
    def extract_batch(self, prompt: str) -> dict:
        try:
            if self.provider == "gemini":
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=BatchExtractionResponse,
                        temperature=0.1
                    ),
                )
                return json.loads(response.text)
                
            elif self.provider == "groq":
                # Groq doesn't support strict schema generation as cleanly out of the box in the same way,
                # but we can enforce JSON mode
                response = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a data extraction AI. Output strictly valid JSON matching the requested schema."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=self.model,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
                
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower():
                logger.warning(f"Rate limit hit on {self.provider}. Backing off...")
                raise RateLimitError(f"Rate limit exceeded: {e}")
            else:
                logger.error(f"LLM extraction failed: {e}")
                raise
