import os
import sys
from pipeline.utils import setup_logger

logger = setup_logger("RunAll")

def main():
    logger.info("Starting Phase 1: Data Collection")
    
    # 1. Google Play Store
    try:
        from pipeline.collectors.google_play import collect_play_store_reviews
        logger.info("Running Google Play Collector...")
        collect_play_store_reviews()
    except Exception as e:
        logger.error(f"Google Play Collector failed: {e}")
        
    # 2. Apple App Store
    try:
        from pipeline.collectors.app_store import collect_app_store_reviews
        logger.info("Running Apple App Store Collector...")
        collect_app_store_reviews()
    except Exception as e:
        logger.error(f"Apple App Store Collector failed: {e}")
        
        
    # 4. Help Community
    try:
        from pipeline.collectors.help_community import collect_help_community
        logger.info("Running Help Community Collector...")
        collect_help_community()
    except Exception as e:
        logger.error(f"Help Community Collector failed: {e}")

    logger.info("Phase 1 Data Collection Complete! Check data/raw/ directory.")

if __name__ == "__main__":
    main()
