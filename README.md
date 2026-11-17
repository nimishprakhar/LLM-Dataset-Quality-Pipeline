# AI Training Data Factory

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade data curation and processing platform for building high-quality datasets for training Large Language Models (LLMs), Retrieval-Augmented Generation (RAG) systems, and foundation models.

## Features

### Data Acquisition
- **Multi-source web crawling** with Scrapy and Selenium
- **API-based ingestion** from Wikipedia, arXiv, Stack Overflow, GitHub
- **Batch ingestion** from JSONL, Parquet, CSV, HuggingFace datasets

### Content Extraction
- Intelligent HTML parsing with noise removal
- Extracts main content, headings, tables, code blocks
- Removes ads, navigation, scripts, footers

### Data Cleaning
- Unicode normalization
- Language detection (90+ languages)
- Whitespace and HTML cleanup
- Text standardization

### Deduplication Pipeline
- **Exact deduplication** using SHA256 hashing
- **Near-duplicate detection** using MinHash LSH
- **Semantic deduplication** using embeddings (FAISS)

### Quality Filtering
- Readability scoring (Flesch-Kincaid)
- Grammar quality assessment
- Toxicity detection (Detoxify)
- PII detection and redaction (Presidio)
- Information density analysis

### Metadata Enrichment
- Language detection
- Domain/source classification
- Topic extraction (zero-shot)
- Quality scoring
- Content statistics

### Semantic Search
- FAISS-powered vector search
- Multiple index types (Flat, IVF, HNSW)
- Corpus analysis and clustering

### Dataset Export
- JSONL, Parquet, Arrow, CSV
- HuggingFace Dataset format
- Direct Hub upload support
- Streaming export for large datasets

## Installation

### Basic Installation
```bash
pip install -e .
```

### Full Installation (all features)
```bash
pip install -e ".[full]"
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from ai_training_data_factory import DataPipeline
from ai_training_data_factory.config import PipelineConfig

# Initialize pipeline
config = PipelineConfig()
pipeline = DataPipeline(config)

# Crawl and process websites
documents = pipeline.crawl_and_process(
    urls=["https://example.com"],
    max_pages=100
)

# Or ingest from APIs
documents = pipeline.ingest_and_process(
    source="wikipedia",
    titles=["Machine learning", "Deep learning"]
)

# Build search index
pipeline.build_search_index(documents)

# Search
results = pipeline.search("neural networks", top_k=10)

# Export
pipeline.export("my_dataset")
```

### Command Line

```bash
# Crawl websites
data-factory crawl https://example.com --max-pages 100 --output dataset

# Ingest from Wikipedia
data-factory ingest wikipedia --query "Python,Machine Learning" --output wiki_dataset

# Ingest from arXiv
data-factory ingest arxiv --query "transformer models" --max-items 500

# Process local file
data-factory process input.jsonl --output processed_dataset

# Build search index
data-factory build-index ./index --input-file dataset.jsonl

# Search
data-factory search ./index "machine learning algorithms"
```

### Docker

```bash
# Build image
docker build -t ai-data-factory .

# Run with docker-compose
docker-compose up -d

# Run a command
docker run -v $(pwd)/data:/app/data ai-data-factory \
    python -m ai_training_data_factory.cli crawl https://example.com
```

## Architecture

```
Web Sources
    ↓
Scrapy + Selenium (Crawling)
    ↓
Raw HTML Storage
    ↓
Content Extraction (BeautifulSoup)
    ↓
Cleaning Pipeline (Unicode, Language)
    ↓
Deduplication (SHA256 → MinHash → Embeddings)
    ↓
Quality Filtering (Readability, Toxicity, PII)
    ↓
Metadata Enrichment (Topics, Stats)
    ↓
FAISS Indexing (Semantic Search)
    ↓
Export (Parquet, JSONL, HuggingFace)
```

## Configuration

Create a `config.yaml` file:

```yaml
# Deduplication settings
deduplication:
  use_exact_dedup: true
  use_minhash: true
  minhash_threshold: 0.8
  use_semantic_dedup: true
  semantic_threshold: 0.95

# Quality filtering
quality:
  min_quality_score: 0.5
  check_toxicity: true
  max_toxicity_score: 0.3
  check_pii: true

# Export
export:
  formats:
    - jsonl
    - parquet
  compression: gzip
```

Load with:
```python
config = load_config("config.yaml")
pipeline = DataPipeline(config)
```

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Data Collection** | Scrapy, Selenium, BeautifulSoup, Requests |
| **Data Processing** | Python, Pandas, NumPy |
| **NLP** | spaCy, Transformers, Sentence-Transformers |
| **Deduplication** | MinHash (datasketch), FAISS |
| **Quality** | Detoxify, Presidio, LanguageTool |
| **Vector Search** | FAISS |
| **Storage** | Parquet, Arrow, JSONL |
| **Deployment** | Docker, Kubernetes |

## Project Structure

```
ai_training_data_factory/
├── __init__.py
├── config.py           # Configuration classes
├── models.py           # Data models (Document, Batch)
├── utils.py            # Utility functions
├── pipeline.py         # Main pipeline orchestrator
├── cli.py              # Command-line interface
├── acquisition/        # Data acquisition
│   ├── crawler.py      # Web crawling
│   ├── api_ingestion.py
│   └── batch_ingestion.py
├── extraction/         # Content extraction
│   ├── extractor.py
│   └── html_parser.py
├── cleaning/           # Data cleaning
│   ├── cleaner.py
│   └── normalizer.py
├── deduplication/      # Deduplication
│   ├── deduplicator.py
│   ├── exact_dedup.py
│   ├── minhash_dedup.py
│   └── semantic_dedup.py
├── quality/            # Quality filtering
│   ├── quality_filter.py
│   ├── metrics.py
│   ├── toxicity.py
│   └── pii.py
├── enrichment/         # Metadata enrichment
│   └── enricher.py
├── search/             # Semantic search
│   └── index.py
└── export/             # Dataset export
    └── exporter.py
```

## Performance

- Processes 10,000+ documents per minute on a single machine
- Scalable with distributed processing (Spark/Dask)
- Efficient memory usage with streaming pipelines
- GPU acceleration for embeddings (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Inspired by data pipelines used at OpenAI, Anthropic, Meta AI, and DeepMind for training foundation models.
