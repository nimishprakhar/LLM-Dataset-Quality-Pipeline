"""
Configuration settings for AI Training Data Factory.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import os


@dataclass
class CrawlerConfig:
    """Configuration for web crawling."""
    user_agent: str = "AITrainingDataFactory/1.0 (+https://github.com/ai-data-factory)"
    concurrent_requests: int = 16
    download_delay: float = 0.5
    respect_robots_txt: bool = True
    max_depth: int = 3
    allowed_domains: List[str] = field(default_factory=list)
    start_urls: List[str] = field(default_factory=list)
    request_timeout: int = 30


@dataclass
class ExtractionConfig:
    """Configuration for content extraction."""
    remove_scripts: bool = True
    remove_styles: bool = True
    remove_navigation: bool = True
    remove_ads: bool = True
    remove_footers: bool = True
    extract_tables: bool = True
    extract_code_blocks: bool = True
    min_text_length: int = 100


@dataclass
class CleaningConfig:
    """Configuration for data cleaning."""
    normalize_unicode: bool = True
    normalize_whitespace: bool = True
    remove_html_tags: bool = True
    detect_language: bool = True
    min_language_confidence: float = 0.8
    target_languages: List[str] = field(default_factory=lambda: ["en"])


@dataclass
class DeduplicationConfig:
    """Configuration for deduplication."""
    # Exact deduplication
    use_exact_dedup: bool = True
    hash_algorithm: str = "sha256"
    
    # Near-duplicate detection
    use_minhash: bool = True
    minhash_num_perm: int = 128
    minhash_threshold: float = 0.8
    
    # Semantic deduplication
    use_semantic_dedup: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    semantic_threshold: float = 0.95
    batch_size: int = 32


@dataclass
class QualityConfig:
    """Configuration for quality filtering."""
    min_quality_score: float = 0.5
    check_readability: bool = True
    check_grammar: bool = True
    check_toxicity: bool = True
    check_pii: bool = True
    max_toxicity_score: float = 0.3
    min_readability_score: float = 30.0  # Flesch reading ease
    min_word_count: int = 50
    max_word_count: int = 100000


@dataclass
class EnrichmentConfig:
    """Configuration for metadata enrichment."""
    extract_language: bool = True
    extract_domain: bool = True
    extract_topics: bool = True
    calculate_quality_score: bool = True
    calculate_readability: bool = True
    topic_model: str = "zero-shot"


@dataclass
class SearchConfig:
    """Configuration for semantic search."""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    index_type: str = "IVF"  # IVF, Flat, HNSW
    nlist: int = 100  # Number of clusters for IVF
    nprobe: int = 10  # Number of clusters to search
    dimension: int = 384


@dataclass
class ExportConfig:
    """Configuration for dataset export."""
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    formats: List[str] = field(default_factory=lambda: ["jsonl", "parquet"])
    compression: Optional[str] = "gzip"
    chunk_size: int = 10000
    push_to_hub: bool = False
    hub_repo_id: Optional[str] = None


@dataclass
class PipelineConfig:
    """Main configuration for the entire pipeline."""
    crawler: CrawlerConfig = field(default_factory=CrawlerConfig)
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    cleaning: CleaningConfig = field(default_factory=CleaningConfig)
    deduplication: DeduplicationConfig = field(default_factory=DeduplicationConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    enrichment: EnrichmentConfig = field(default_factory=EnrichmentConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    
    # General settings
    data_dir: Path = field(default_factory=lambda: Path("./data"))
    log_level: str = "INFO"
    num_workers: int = field(default_factory=lambda: os.cpu_count() or 4)
    
    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.export.output_dir = Path(self.export.output_dir)
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export.output_dir.mkdir(parents=True, exist_ok=True)


def load_config(config_path: Optional[str] = None) -> PipelineConfig:
    """Load configuration from file or use defaults."""
    if config_path:
        import yaml
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        # Convert dict to config objects
        return PipelineConfig(**config_dict)
    return PipelineConfig()
