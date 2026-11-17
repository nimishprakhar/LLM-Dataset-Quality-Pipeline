"""
Utility functions for AI Training Data Factory.
"""

import logging
import hashlib
import re
from typing import List, Iterator, Any, Optional
from pathlib import Path
import json


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger("ai_training_data_factory")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    
    return logger


def compute_hash(text: str, algorithm: str = "sha256") -> str:
    """Compute hash of text."""
    hasher = getattr(hashlib, algorithm)()
    hasher.update(text.encode("utf-8"))
    return hasher.hexdigest()


def batch_iterator(items: List[Any], batch_size: int) -> Iterator[List[Any]]:
    """Yield batches of items."""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def clean_text(text: str) -> str:
    """Basic text cleaning."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def save_jsonl(data: List[dict], filepath: Path):
    """Save data to JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def load_jsonl(filepath: Path) -> List[dict]:
    """Load data from JSONL file."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def estimate_tokens(text: str) -> int:
    """Estimate number of tokens in text (rough approximation)."""
    # Rough estimate: ~4 characters per token for English
    return len(text) // 4


def normalize_unicode(text: str) -> str:
    """Normalize unicode characters."""
    import unicodedata
    # NFKC normalization
    text = unicodedata.normalize('NFKC', text)
    return text


def remove_control_characters(text: str) -> str:
    """Remove control characters from text."""
    import unicodedata
    return ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')


def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_file_size_mb(filepath: Path) -> float:
    """Get file size in MB."""
    return filepath.stat().st_size / (1024 * 1024)


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path
