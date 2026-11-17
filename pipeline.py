"""
Main data pipeline orchestrating all processing stages.
"""

import logging
from typing import List, Optional, Dict, Any, Iterator
from datetime import datetime
from pathlib import Path

from .models import Document, Batch, ProcessingStats
from .config import PipelineConfig
from .acquisition import WebCrawler, APIIngester, BatchIngester
from .extraction import ContentExtractor
from .cleaning import DataCleaner
from .deduplication import Deduplicator
from .quality import QualityFilter
from .enrichment import MetadataEnricher
from .search import SemanticIndex
from .export import DatasetExporter
from .utils import setup_logging

logger = logging.getLogger(__name__)


class DataPipeline:
    """
    Main data processing pipeline for AI training data.
    
    Orchestrates the complete data processing lifecycle:
    1. Data Acquisition (crawling, API ingestion)
    2. Content Extraction (HTML parsing)
    3. Data Cleaning (normalization)
    4. Deduplication (exact, near-duplicate, semantic)
    5. Quality Filtering
    6. Metadata Enrichment
    7. Semantic Search Indexing
    8. Dataset Export
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the data pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        
        # Set up logging
        setup_logging(self.config.log_level)
        
        # Initialize components
        self.crawler = WebCrawler(self.config.crawler)
        self.api_ingester = APIIngester(self.config.crawler)
        self.batch_ingester = BatchIngester()
        
        self.extractor = ContentExtractor(self.config.extraction)
        self.cleaner = DataCleaner(self.config.cleaning)
        self.deduplicator = Deduplicator(self.config.deduplication)
        self.quality_filter = QualityFilter(self.config.quality)
        self.enricher = MetadataEnricher(self.config.enrichment)
        
        self.search_index = SemanticIndex(self.config.search)
        self.exporter = DatasetExporter(self.config.export)
        
        # Processing statistics
        self.stats = ProcessingStats()
        
        # Processed documents
        self.documents: List[Document] = []
    
    def process(self, documents: List[Document]) -> List[Document]:
        """
        Process a batch of documents through the full pipeline.
        
        Args:
            documents: List of documents to process
            
        Returns:
            Processed documents
        """
        self.stats.start_time = datetime.now()
        self.stats.total_documents = len(documents)
        
        logger.info(f"Starting pipeline with {len(documents)} documents")
        
        # Stage 1: Content Extraction
        logger.info("Stage 1: Content Extraction")
        documents = self.extractor.extract_batch(documents)
        
        # Stage 2: Cleaning
        logger.info("Stage 2: Data Cleaning")
        documents = self.cleaner.clean_batch(documents)
        
        # Filter out documents that failed cleaning
        documents = [doc for doc in documents if doc.passed_quality_filter]
        logger.info(f"After cleaning: {len(documents)} documents")
        
        # Stage 3: Deduplication
        logger.info("Stage 3: Deduplication")
        documents = self.deduplicator.deduplicate(documents)
        self.stats.duplicates_removed = self.deduplicator.total_duplicates
        
        # Stage 4: Quality Filtering
        logger.info("Stage 4: Quality Filtering")
        documents = self.quality_filter.filter_batch(documents)
        documents = [doc for doc in documents if doc.passed_quality_filter]
        self.stats.quality_filtered = self.quality_filter.total_filtered
        logger.info(f"After quality filter: {len(documents)} documents")
        
        # Stage 5: Metadata Enrichment
        logger.info("Stage 5: Metadata Enrichment")
        documents = self.enricher.enrich_batch(documents)
        
        # Update statistics
        self.stats.processed_documents = len(documents)
        self.stats.end_time = datetime.now()
        
        logger.info(f"Pipeline complete: {len(documents)} documents processed")
        self._log_stats()
        
        self.documents.extend(documents)
        return documents
    
    def crawl_and_process(self, urls: List[str], max_pages: int = 100) -> List[Document]:
        """
        Crawl URLs and process the results.
        
        Args:
            urls: List of URLs to crawl
            max_pages: Maximum pages to crawl
            
        Returns:
            Processed documents
        """
        logger.info(f"Crawling {len(urls)} URLs...")
        documents = self.crawler.crawl(urls, max_pages=max_pages)
        return self.process(documents)
    
    def ingest_and_process(self, source: str, **kwargs) -> List[Document]:
        """
        Ingest from various sources and process.
        
        Args:
            source: Source type ('wikipedia', 'arxiv', 'stackoverflow', 'github', 'urls')
            **kwargs: Source-specific arguments
            
        Returns:
            Processed documents
        """
        logger.info(f"Ingesting from {source}...")
        
        if source == "wikipedia":
            documents = self.api_ingester.ingest_wikipedia(**kwargs)
        elif source == "arxiv":
            documents = self.api_ingester.ingest_arxiv(**kwargs)
        elif source == "stackoverflow":
            documents = self.api_ingester.ingest_stackoverflow(**kwargs)
        elif source == "github":
            documents = self.api_ingester.ingest_github_repos(**kwargs)
        elif source == "urls":
            documents = self.api_ingester.ingest_from_urls(**kwargs)
        else:
            raise ValueError(f"Unknown source: {source}")
        
        return self.process(documents)
    
    def process_file(self, filepath: Path, **kwargs) -> List[Document]:
        """
        Process documents from a file.
        
        Args:
            filepath: Path to file
            **kwargs: Format-specific arguments
            
        Returns:
            Processed documents
        """
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()
        
        all_docs = []
        
        if suffix == ".jsonl":
            for batch in self.batch_ingester.ingest_jsonl(filepath, **kwargs):
                docs = self.process(batch.documents)
                all_docs.extend(docs)
        
        elif suffix == ".parquet":
            for batch in self.batch_ingester.ingest_parquet(filepath, **kwargs):
                docs = self.process(batch.documents)
                all_docs.extend(docs)
        
        elif suffix == ".csv":
            for batch in self.batch_ingester.ingest_csv(filepath, **kwargs):
                docs = self.process(batch.documents)
                all_docs.extend(docs)
        
        elif suffix == ".txt":
            for batch in self.batch_ingester.ingest_text_files(filepath.parent, filepath.name):
                docs = self.process(batch.documents)
                all_docs.extend(docs)
        
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
        
        return all_docs
    
    def build_search_index(self, documents: Optional[List[Document]] = None) -> int:
        """
        Build semantic search index.
        
        Args:
            documents: Documents to index (uses processed documents if None)
            
        Returns:
            Number of documents indexed
        """
        docs = documents or self.documents
        valid_docs = [doc for doc in docs if doc.content and not doc.is_duplicate]
        
        logger.info(f"Building search index for {len(valid_docs)} documents...")
        count = self.search_index.add_documents(valid_docs)
        logger.info(f"Indexed {count} documents")
        
        return count
    
    def search(self, query: str, top_k: int = 10) -> List[tuple]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of (document, score) tuples
        """
        return self.search_index.search(query, top_k)
    
    def export(self, name: str = "dataset", 
               documents: Optional[List[Document]] = None) -> Dict[str, Path]:
        """
        Export processed documents.
        
        Args:
            name: Dataset name
            documents: Documents to export (uses processed documents if None)
            
        Returns:
            Dictionary of format to output path
        """
        docs = documents or self.documents
        return self.exporter.export(docs, name)
    
    def save_index(self, path: Path):
        """Save semantic search index to disk."""
        self.search_index.save(path)
    
    def load_index(self, path: Path):
        """Load semantic search index from disk."""
        self.search_index.load(path)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            **self.stats.to_dict(),
            "deduplication": self.deduplicator.get_stats(),
            "quality_filter": self.quality_filter.get_stats(),
            "search_index": self.search_index.get_corpus_stats(),
        }
    
    def _log_stats(self):
        """Log processing statistics."""
        stats = self.stats
        logger.info("=" * 50)
        logger.info("Pipeline Statistics:")
        logger.info(f"  Total documents: {stats.total_documents}")
        logger.info(f"  Processed: {stats.processed_documents}")
        logger.info(f"  Duplicates removed: {stats.duplicates_removed}")
        logger.info(f"  Quality filtered: {stats.quality_filtered}")
        logger.info(f"  Duration: {stats.duration_seconds:.2f}s")
        if stats.documents_per_second:
            logger.info(f"  Speed: {stats.documents_per_second:.1f} docs/sec")
        logger.info("=" * 50)
    
    def reset(self):
        """Reset pipeline state."""
        self.deduplicator.reset()
        self.quality_filter.reset_stats()
        self.search_index.clear()
        self.documents.clear()
        self.stats = ProcessingStats()


class StreamingPipeline(DataPipeline):
    """
    Streaming version of the data pipeline for large datasets.
    Processes documents in batches to minimize memory usage.
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None, batch_size: int = 1000):
        super().__init__(config)
        self.batch_size = batch_size
    
    def process_streaming(self, document_iterator: Iterator[Document]) -> Iterator[Document]:
        """
        Process documents in streaming mode.
        
        Args:
            document_iterator: Iterator of documents
            
        Yields:
            Processed documents
        """
        batch = []
        
        for doc in document_iterator:
            batch.append(doc)
            
            if len(batch) >= self.batch_size:
                processed = self.process(batch)
                for doc in processed:
                    yield doc
                batch = []
        
        # Process remaining documents
        if batch:
            processed = self.process(batch)
            for doc in processed:
                yield doc
    
    def process_file_streaming(self, filepath: Path, **kwargs) -> Iterator[Document]:
        """
        Process file in streaming mode.
        
        Args:
            filepath: Path to file
            **kwargs: Format-specific arguments
            
        Yields:
            Processed documents
        """
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()
        
        if suffix == ".jsonl":
            for batch in self.batch_ingester.ingest_jsonl(filepath, **kwargs):
                processed = self.process(batch.documents)
                for doc in processed:
                    yield doc
        else:
            raise ValueError(f"Streaming not supported for format: {suffix}")
