import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.utils import setup_logger
from pipeline.analysis.aggregates import compute_aggregates
from pipeline.index_builder.embeddings import generate_embeddings
from pipeline.analysis.clustering import run_clustering
from pipeline.analysis.opportunity_score import run_opportunity_scoring
from pipeline.analysis.audit_generator import generate_audit

from pipeline.analysis.agreement_check import run_agreement_check
from pipeline.index_builder.bm25_index import build_index

logger = setup_logger("Phase4Runner")

def main():
    logger.info("=== Starting Phase 4: Aggregation & Analysis ===")
    
    logger.info("1. Computing Aggregates...")
    compute_aggregates()
    
    logger.info("2. Generating Embeddings...")
    generate_embeddings()
    
    logger.info("3. Running HDBSCAN Clustering...")
    run_clustering()
    
    logger.info("4. Calculating Opportunity Scores...")
    run_opportunity_scoring()
    
    logger.info("5. Generating Trust Audit File...")
    generate_audit()
    
    logger.info("6. Running Model Agreement Check (Gemini vs Groq)...")
    run_agreement_check()
    
    logger.info("7. Building BM25 Search Index...")
    build_index()
    
    logger.info("=== Phase 4 Complete! ===")

if __name__ == "__main__":
    main()
