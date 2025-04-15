"""Crawl4AI Framework - A modular web crawling and data extraction framework.

This package provides a flexible, modular framework for web crawling and data extraction.
It is built on top of Crawl4AI v0.5.0 and provides a simple interface for common crawling tasks.
"""

# Import main components from Crawl4AI for convenience
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CrawlResult

# Import our own modules
from crawl4ai.core import BaseCrawler, CrawlerSession
from crawl4ai.strategies import (
    CrawlStrategy, 
    BFSCrawlStrategy, 
    DFSCrawlStrategy, 
    BestFirstCrawlStrategy,
    StrategyFactory
)
from crawl4ai.crawlers import StrategyCrawler

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
]
