import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.utils import setup_logger
from pipeline.processing.normalise import normalise_all
from pipeline.processing.language_detect import run_language_detection
from pipeline.processing.dedup import run_dedup
from pipeline.processing.prefilter import run_prefilter

logger = setup_logger("Phase2Runner")

def main():
    logger.info("=== Starting Phase 2: Data Cleaning & Pre-filtering ===")
    
    logger.info("1. Normalizing raw data...")
    normalise_all()
    
    logger.info("2. Running language detection...")
    run_language_detection()
    
    logger.info("3. Running exact & near deduplication...")
    run_dedup()
    
    logger.info("4. Running keyword pre-filtering...")
    run_prefilter()
    
    logger.info("=== Phase 2 Complete! Output is in data/processed/prefiltered.jsonl ===")

if __name__ == "__main__":
    main()
