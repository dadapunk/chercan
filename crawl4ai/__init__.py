"""Crawl4AI Framework - A modular web crawling and data extraction framework.

This package provides a flexible, modular framework for web crawling and data extraction.
It is built on top of Crawl4AI v0.5.0 and provides a simple interface for common crawling tasks.
"""

# Import main components from Crawl4AI for convenience
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CrawlResult

# Import our own modules
from crawl4ai.core import BaseCrawler, CrawlerSession, AsyncCrawler, Page, Request, Response
from crawl4ai.strategies import (
    CrawlStrategy, 
    BFSCrawlStrategy, 
    DFSCrawlStrategy, 
    BestFirstCrawlStrategy,
    StrategyFactory,
    BreadthFirstStrategy,
    DepthFirstStrategy,
    PriorityStrategy
)
from crawl4ai.crawlers import (
    StrategyCrawler, 
    PlaywrightCrawler, 
    HTTPCrawler,
    CrawlerFactory,
    CrawlerType
)
from crawl4ai.extractors import (
    BaseExtractor,
    CSSExtractor,
    RegExExtractor,
    XPathExtractor,
    LLMExtractor,
    ExtractorFactory
)
from crawl4ai.processing.filters import (
    BaseContentFilter,
    BasicContentFilter,
    LLMContentFilter,
    PruningRule,
    PruningContentFilter,
    FilterPipeline
)
from crawl4ai.config import LLMConfig
from crawl4ai.exports import (
    BaseExporter, 
    MarkdownExporter,
    JSONExporter,
    HTMLExporter,
    CSVExporter,
    DatabaseExporter,
    DBConnector,
    SQLiteConnector,
    MongoDBConnector,
    ExporterFactory,
    ExportFormat
)

__version__ = "0.1.0"

__all__ = [
    # Re-exported from Crawl4AI
    'AsyncWebCrawler', 
    'BrowserConfig', 
    'CrawlerRunConfig', 
    'CrawlResult',
    
    # Our own modules
    'BaseCrawler',
    'CrawlerSession',
    'CrawlStrategy',
    'BFSCrawlStrategy',
    'DFSCrawlStrategy',
    'BestFirstCrawlStrategy',
    'StrategyFactory',
    'StrategyCrawler',
    'PlaywrightCrawler',
    'HTTPCrawler',
    'CrawlerFactory',
    'CrawlerType',
    'BaseExtractor',
    'CSSExtractor',
    'RegExExtractor',
    'XPathExtractor',
    'LLMExtractor',
    'ExtractorFactory',
    'BaseContentFilter',
    'BasicContentFilter',
    'LLMContentFilter',
    'PruningRule',
    'PruningContentFilter',
    'FilterPipeline',
    'LLMConfig',
    'BaseExporter',
    'MarkdownExporter',
    'JSONExporter',
    'HTMLExporter',
    'CSVExporter',
    'ExporterFactory',
    'ExportFormat',
    'DatabaseExporter',
    'DBConnector',
    'SQLiteConnector',
    'MongoDBConnector',
    'BreadthFirstStrategy',
    'DepthFirstStrategy',
    'PriorityStrategy',
]
