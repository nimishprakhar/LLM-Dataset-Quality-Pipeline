"""
Command-line interface for AI Training Data Factory.
"""

import click
import json
import logging
from pathlib import Path
from typing import Optional, List

from .config import PipelineConfig, load_config
from .pipeline import DataPipeline, StreamingPipeline
from .utils import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to config file')
@click.option('--log-level', '-l', default='INFO', help='Log level')
@click.pass_context
def cli(ctx, config, log_level):
    """AI Training Data Factory - Build high-quality datasets for AI training."""
    ctx.ensure_object(dict)
    
    # Load configuration
    if config:
        ctx.obj['config'] = load_config(config)
    else:
        ctx.obj['config'] = PipelineConfig()
    
    ctx.obj['config'].log_level = log_level
    setup_logging(log_level)


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--max-pages', '-m', default=100, help='Maximum pages to crawl')
@click.option('--output', '-o', default='crawled_dataset', help='Output dataset name')
@click.pass_context
def crawl(ctx, urls, max_pages, output):
    """Crawl URLs and process the content."""
    config = ctx.obj['config']
    pipeline = DataPipeline(config)
    
    click.echo(f"Crawling {len(urls)} URLs...")
    documents = pipeline.crawl_and_process(list(urls), max_pages=max_pages)
    
    click.echo(f"Processed {len(documents)} documents")
    
    # Export
    output_paths = pipeline.export(output)
    for fmt, path in output_paths.items():
        click.echo(f"Exported to {fmt}: {path}")


@cli.command()
@click.argument('source', type=click.Choice(['wikipedia', 'arxiv', 'stackoverflow', 'github']))
@click.option('--query', '-q', help='Search query or list of items')
@click.option('--max-items', '-m', default=100, help='Maximum items to fetch')
@click.option('--output', '-o', default='ingested_dataset', help='Output dataset name')
@click.pass_context
def ingest(ctx, source, query, max_items, output):
    """Ingest data from various sources."""
    config = ctx.obj['config']
    pipeline = DataPipeline(config)
    
    click.echo(f"Ingesting from {source}...")
    
    kwargs = {}
    if source == 'wikipedia':
        kwargs['titles'] = query.split(',') if query else ['Python (programming language)']
    elif source == 'arxiv':
        kwargs['query'] = query or 'machine learning'
        kwargs['max_results'] = max_items
    elif source == 'stackoverflow':
        kwargs['tags'] = query.split(',') if query else ['python']
        kwargs['max_questions'] = max_items
    elif source == 'github':
        kwargs['query'] = query or 'machine learning'
        kwargs['max_repos'] = max_items
    
    documents = pipeline.ingest_and_process(source, **kwargs)
    
    click.echo(f"Processed {len(documents)} documents")
    
    output_paths = pipeline.export(output)
    for fmt, path in output_paths.items():
        click.echo(f"Exported to {fmt}: {path}")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='processed_dataset', help='Output dataset name')
@click.option('--text-column', '-t', default='text', help='Column name for text content')
@click.option('--streaming/--no-streaming', default=False, help='Use streaming mode')
@click.pass_context
def process(ctx, input_file, output, text_column, streaming):
    """Process a local file through the pipeline."""
    config = ctx.obj['config']
    
    input_path = Path(input_file)
    click.echo(f"Processing {input_path}...")
    
    if streaming:
        pipeline = StreamingPipeline(config)
        # For streaming, we need to export incrementally
        documents = list(pipeline.process_file_streaming(input_path, content_field=text_column))
    else:
        pipeline = DataPipeline(config)
        documents = pipeline.process_file(input_path, content_field=text_column)
    
    click.echo(f"Processed {len(documents)} documents")
    
    output_paths = pipeline.export(output, documents)
    for fmt, path in output_paths.items():
        click.echo(f"Exported to {fmt}: {path}")


@cli.command()
@click.argument('index_path', type=click.Path())
@click.option('--input-file', '-i', type=click.Path(exists=True), help='Input file to index')
@click.pass_context
def build_index(ctx, index_path, input_file):
    """Build semantic search index."""
    config = ctx.obj['config']
    pipeline = DataPipeline(config)
    
    if input_file:
        click.echo(f"Processing {input_file}...")
        documents = pipeline.process_file(Path(input_file))
    else:
        click.echo("No input file provided. Use --input-file to specify data.")
        return
    
    click.echo("Building search index...")
    count = pipeline.build_search_index(documents)
    
    click.echo(f"Indexed {count} documents")
    
    pipeline.save_index(Path(index_path))
    click.echo(f"Index saved to {index_path}")


@cli.command()
@click.argument('index_path', type=click.Path(exists=True))
@click.argument('query')
@click.option('--top-k', '-k', default=10, help='Number of results')
@click.pass_context
def search(ctx, index_path, query, top_k):
    """Search the semantic index."""
    config = ctx.obj['config']
    pipeline = DataPipeline(config)
    
    click.echo(f"Loading index from {index_path}...")
    pipeline.load_index(Path(index_path))
    
    click.echo(f"Searching for: {query}")
    results = pipeline.search(query, top_k)
    
    click.echo(f"\nTop {len(results)} results:\n")
    for i, (doc, score) in enumerate(results, 1):
        title = doc.title or doc.url or doc.doc_id[:20]
        content_preview = doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
        click.echo(f"{i}. [{score:.3f}] {title}")
        click.echo(f"   {content_preview}\n")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show pipeline statistics."""
    config = ctx.obj['config']
    pipeline = DataPipeline(config)
    
    stats = pipeline.get_stats()
    click.echo("\nPipeline Statistics:")
    click.echo(json.dumps(stats, indent=2))


@cli.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"AI Training Data Factory v{__version__}")


if __name__ == '__main__':
    cli()
