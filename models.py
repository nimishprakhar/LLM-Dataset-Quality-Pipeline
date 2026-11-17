"""
Data models for AI Training Data Factory.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json


@dataclass
class Document:
    """Represents a single document in the pipeline."""
    
    # Core content
    content: str
    url: Optional[str] = None
    title: Optional[str] = None
    
    # Identifiers
    doc_id: Optional[str] = None
    content_hash: Optional[str] = None
    
    # Raw data
    raw_html: Optional[str] = None
    
    # Extracted elements
    headings: List[str] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    code_blocks: List[Dict[str, str]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    quality_score: Optional[float] = None
    readability_score: Optional[float] = None
    toxicity_score: Optional[float] = None
    language: Optional[str] = None
    language_confidence: Optional[float] = None
    
    # Processing flags
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    passed_quality_filter: bool = True
    
    # Timestamps
    crawled_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.doc_id is None:
            self.doc_id = self._generate_id()
        if self.content_hash is None and self.content:
            self.content_hash = self._compute_hash()
    
    def _generate_id(self) -> str:
        """Generate a unique document ID."""
        unique_str = f"{self.url or ''}{self.content[:100] if self.content else ''}{datetime.now().isoformat()}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def _compute_hash(self) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(self.content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "url": self.url,
            "title": self.title,
            "content_hash": self.content_hash,
            "headings": self.headings,
            "tables": self.tables,
            "code_blocks": self.code_blocks,
            "links": self.links,
            "images": self.images,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "readability_score": self.readability_score,
            "toxicity_score": self.toxicity_score,
            "language": self.language,
            "language_confidence": self.language_confidence,
            "is_duplicate": self.is_duplicate,
            "duplicate_of": self.duplicate_of,
            "passed_quality_filter": self.passed_quality_filter,
            "crawled_at": self.crawled_at.isoformat() if self.crawled_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create document from dictionary."""
        # Handle datetime fields
        if data.get("crawled_at"):
            data["crawled_at"] = datetime.fromisoformat(data["crawled_at"])
        if data.get("processed_at"):
            data["processed_at"] = datetime.fromisoformat(data["processed_at"])
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert document to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Document":
        """Create document from JSON string."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class Batch:
    """Represents a batch of documents for processing."""
    
    documents: List[Document]
    batch_id: str = field(default_factory=lambda: hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8])
    created_at: datetime = field(default_factory=datetime.now)
    
    def __len__(self) -> int:
        return len(self.documents)
    
    def __iter__(self):
        return iter(self.documents)
    
    def __getitem__(self, idx: int) -> Document:
        return self.documents[idx]
    
    def filter_valid(self) -> "Batch":
        """Return a new batch with only valid (non-duplicate, passed quality) documents."""
        valid_docs = [
            doc for doc in self.documents 
            if not doc.is_duplicate and doc.passed_quality_filter
        ]
        return Batch(documents=valid_docs)


@dataclass
class ProcessingStats:
    """Statistics for pipeline processing."""
    
    total_documents: int = 0
    processed_documents: int = 0
    duplicates_removed: int = 0
    quality_filtered: int = 0
    errors: int = 0
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def update(self, processed: int = 0, duplicates: int = 0, filtered: int = 0, errors: int = 0):
        """Update statistics."""
        self.processed_documents += processed
        self.duplicates_removed += duplicates
        self.quality_filtered += filtered
        self.errors += errors
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def documents_per_second(self) -> Optional[float]:
        """Get processing speed."""
        duration = self.duration_seconds
        if duration and duration > 0:
            return self.processed_documents / duration
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_documents": self.total_documents,
            "processed_documents": self.processed_documents,
            "duplicates_removed": self.duplicates_removed,
            "quality_filtered": self.quality_filtered,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds,
            "documents_per_second": self.documents_per_second,
        }
