import os
import sys
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

Relevance = Literal["core", "adjacent", "not_relevant"]
VagueMemory = Literal["yes", "no", "unclear"]
PhotoType = Literal["screenshot", "document/receipt/ID", "medical", "travel", "family/people", "pet", "food", "event", "video", "old/scanned", "other", "unknown"]
Clue = Literal["person", "place", "event/occasion", "approx_time", "season", "object", "text_in_image", "activity", "source/context", "visual_appearance", "other"]
ClueForgotten = Literal["exact_date", "album", "location_name", "keywords/filename", "device/account", "who_is_in_it", "other"]
SearchBehavior = Literal["typed_keyword", "natural_language_query", "people_filter", "place_filter", "date_filter", "scroll_timeline", "browse_albums", "ask_photos_ai", "external_workaround", "gave_up", "other"]
FailureStage = Literal["cannot_express", "system_misunderstands", "results_hard_to_evaluate", "cannot_refine", "photo_not_indexed_or_missing", "other", "none"]
Outcome = Literal["found", "found_after_workaround", "not_found", "gave_up", "unknown"]
AIFeature = Literal["ask_photos", "gemini", "natural_language_search", "face_grouping", "text_search", "location_search", "memories", "other"]

class ExtractedReview(BaseModel):
    relevance: Relevance = Field(description="Core = search/retrieval issue. Adjacent = sync/missing/deleted issue. Not_relevant = other.")
    vague_memory: VagueMemory = Field(description="Does the user vaguely remember something but cannot fully specify it?")
    photo_type: PhotoType = Field(description="Type of photo being searched for.")
    
    clues_remembered: List[Clue] = Field(description="Context the user remembers about the photo.")
    clues_forgotten: List[ClueForgotten] = Field(description="Context the user explicitly forgot.")
    
    search_behavior: List[SearchBehavior] = Field(description="Actions taken to find the photo.")
    example_queries: List[str] = Field(description="Exact search strings typed by user.", default_factory=list)
    
    failure_stage: List[FailureStage] = Field(description="Primary failure points. First item is the primary failure stage.")
    failure_detail: str = Field(description="Explain the failure in own words (up to 25 words).")
    core_problem: str = Field(description="One sentence summarizing the root cause.")
    
    workaround: List[str] = Field(description="Workarounds attempted.", default_factory=list)
    outcome: Outcome = Field(description="End result of the search attempt.")
    
    severity: int = Field(description="1: annoyance, 2: major friction, 3: blocker", ge=1, le=3)
    regression_claim: bool = Field(description="Did they claim this used to work better?")
    ai_feature_mentioned: List[AIFeature] = Field(description="AI features explicitly mentioned.", default_factory=list)
    
    evidence_quote: str = Field(description="Exact substring of the original text proving this, up to 25 words.")
    labeler_confidence: float = Field(description="0 to 1 confidence rating.", ge=0.0, le=1.0)
    
class BatchExtractionResponse(BaseModel):
    items: List[ExtractedReview]
