"""
My custom AI Training Data Factory pipeline example.
This script demonstrates how to use the pipeline for data processing.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
# my_pipeline.py is at the root of the package, need to go up one level
package_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(package_root))

from ai_training_data_factory import DataPipeline
from ai_training_data_factory.config import PipelineConfig
from ai_training_data_factory.models import Document


def main():
    """Run the custom pipeline."""
    
    print("=" * 60)
    print("AI Training Data Factory - Custom Pipeline")
    print("=" * 60)
    
    # Initialize pipeline configuration
    config = PipelineConfig()
    
    # Relax quality filters for demo purposes
    config.quality.min_word_count = 10
    config.quality.min_quality_score = 0.1
    config.quality.check_toxicity = False
    config.quality.check_pii = False
    
    # Create pipeline instance
    pipeline = DataPipeline(config)
    
    # Create sample documents
    print("\n[1] Creating sample documents...")
    documents = [
        Document(
            content="Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. Python is widely used in data science, machine learning, web development, and automation.",
            url="https://example.com/python",
            title="Introduction to Python"
        ),
        Document(
            content="Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computers to learn from data without being explicitly programmed. It has applications in image recognition, natural language processing, and predictive analytics.",
            url="https://example.com/ml",
            title="Machine Learning Basics"
        ),
        Document(
            content="Data science combines statistics, programming, and domain expertise to extract meaningful insights from data. Data scientists use tools like Python, R, and SQL to clean, analyze, and visualize data. The field is crucial for making data-driven business decisions.",
            url="https://example.com/datascience",
            title="What is Data Science"
        ),
        Document(
            content="Web development involves creating websites and web applications. Modern web development typically includes frontend technologies like HTML, CSS, and JavaScript, and backend technologies like Python, Node.js, or Java. Frameworks like Django, Flask, and React simplify web development.",
            url="https://example.com/webdev",
            title="Web Development Overview"
        ),
    ]
    
    print(f"[+] Created {len(documents)} sample documents")
    for doc in documents:
        print(f"  - {doc.title} ({len(doc.content)} chars)")
    
    # Process documents through pipeline
    print("\n[2] Processing documents through pipeline...")
    processed_documents = pipeline.process(documents)
    
    print(f"[+] Processing complete")
    print(f"  - Input: {len(documents)} documents")
    print(f"  - Output: {len(processed_documents)} documents")
    
    # Display results
    print("\n[3] Processed Documents:")
    print("-" * 60)
    for i, doc in enumerate(processed_documents, 1):
        print(f"\n{i}. {doc.title}")
        print(f"   URL: {doc.url}")
        print(f"   Content preview: {doc.content[:100]}...")
        if hasattr(doc, 'metadata') and doc.metadata:
            print(f"   Metadata: {doc.metadata}")
    
    # Show pipeline statistics
    print("\n[4] Pipeline Statistics:")
    print("-" * 60)
    if hasattr(pipeline, 'stats'):
        stats = pipeline.stats
        print(f"   Total documents: {stats.total_documents}")
        print(f"   Processed: {stats.processed_documents}")
        print(f"   Duplicates removed: {stats.duplicates_removed}")
        print(f"   Quality filtered: {stats.quality_filtered}")
    
    print("\n" + "=" * 60)
    print("[+] Pipeline execution completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
