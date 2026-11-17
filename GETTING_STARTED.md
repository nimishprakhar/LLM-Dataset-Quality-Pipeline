# Getting Started with AI Training Data Factory

This guide walks you through setting up and running the project.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- (Optional) Git for version control
- (Optional) Docker for containerized setup

## Installation

### Option 1: Minimal Installation (Recommended for first-time setup)

This installs only core dependencies:

```bash
cd c:\Users\nimish\Desktop\ai_training_data_factory
pip install -e .
```

This gives you basic functionality for:
- Data loading and processing
- Quality filtering basics
- CSV/JSONL export

### Option 2: Full Installation (All features)

For all capabilities including web crawling, semantic search, and advanced deduplication:

```bash
pip install -e ".[full]"
```

This additionally provides:
- Web crawling (Scrapy, Selenium)
- Advanced NLP (spaCy, Transformers)
- Semantic deduplication (FAISS)
- Semantic search
- Advanced quality checks (Detoxify, Presidio)

### Option 3: Development Installation

For contributing or modifying the code:

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Run the Example Script

The easiest way to see it in action:

```bash
cd c:\Users\nimish\Desktop\ai_training_data_factory
python examples/basic_usage.py
```

This will:
- Create sample documents
- Run them through the cleaning pipeline
- Demonstrate deduplication
- Show quality filtering

### 2. Use the Python API

Create a new file `my_script.py`:

```python
from ai_training_data_factory import DataPipeline
from ai_training_data_factory.config import PipelineConfig

# Initialize pipeline
config = PipelineConfig()
pipeline = DataPipeline(config)

# Create a simple document
from ai_training_data_factory.models import Document

doc = Document(
    content="Machine learning is a subset of artificial intelligence.",
    url="https://example.com",
    title="ML Intro"
)

# Process it
processed = pipeline.process_document(doc)
print(f"Processed: {processed.content[:100]}...")
```

Run it:
```bash
python my_script.py
```

### 3. Use the Command-Line Interface

```bash
# Ingest from Wikipedia
data-factory ingest wikipedia --query "Machine Learning" --max-items 10 --output ml_dataset

# Process a local file
data-factory process input.jsonl --output processed_data

# View help
data-factory --help
```

### 4. Try with Docker

```bash
# Build the Docker image
docker build -t ai-data-factory .

# Run a quick test
docker run ai-data-factory python -m ai_training_data_factory.cli --help
```

## Troubleshooting

### Issue: "ModuleNotFoundError" when running

**Solution:** Make sure you installed the package in editable mode:
```bash
pip install -e .
```

### Issue: Missing optional dependencies (e.g., "No module named 'scrapy'")

**Solution:** Install the full version:
```bash
pip install -e ".[full]"
```

### Issue: Permission errors on Windows

**Solution:** Run your terminal as Administrator, or use a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
pip install -e ".[full]"
```

## Project Structure Overview

```
ai_training_data_factory/
├── acquisition/      → Web crawling & API ingestion
├── extraction/       → HTML parsing & content extraction
├── cleaning/         → Text normalization & cleanup
├── deduplication/    → Exact, MinHash, and semantic deduplication
├── quality/          → Readability, toxicity, PII checks
├── enrichment/       → Metadata & topic enrichment
├── search/           → FAISS-powered semantic search
├── export/           → Export to Parquet, JSONL, HuggingFace
└── examples/         → Example scripts
```

## Next Steps

1. **Run the example**: `python examples/basic_usage.py`
2. **Read the README**: Detailed features and architecture
3. **Check the examples**: More realistic use cases
4. **Explore the code**: Each module has docstrings
5. **Configure**: Edit `config.yaml` for custom settings

## Common Tasks

### Process a CSV file
```python
import pandas as pd
from ai_training_data_factory import DataPipeline

pipeline = DataPipeline()
df = pd.read_csv("data.csv")
documents = pipeline.process_texts(df['text'].tolist())
```

### Build a search index
```python
pipeline = DataPipeline()
# ... process documents ...
pipeline.build_search_index(documents)
results = pipeline.search("your query")
```

### Export in different formats
```python
# Export to multiple formats
pipeline.export("my_dataset")  # Creates JSONL and Parquet by default
```

## Getting Help

- Check the docstrings in each module
- Review `examples/basic_usage.py`
- See `README.md` for architecture details
- Configuration is in `config.yaml`

---

**Happy data processing! 🚀**
