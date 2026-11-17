"""
AI Training Data Factory
========================

A large-scale data curation and processing platform for building high-quality 
datasets for training Large Language Models (LLMs), RAG systems, and foundation models.

Modules:
    - acquisition: Web crawling and data ingestion
    - extraction: Content extraction from raw HTML
    - cleaning: Data normalization and cleaning
    - deduplication: Exact, near-duplicate, and semantic deduplication
    - quality: Quality filtering and scoring
    - enrichment: Metadata enrichment
    - search: Semantic search indexing
    - export: Dataset export utilities
"""

__version__ = "1.0.0"
__author__ = "AI Training Data Factory Team"

from .pipeline import DataPipeline

__all__ = ["DataPipeline"]
