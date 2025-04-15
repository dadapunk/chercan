"""Crawling strategies for the Crawl4AI framework.

This package provides different crawling strategies that determine
the order in which URLs are crawled.
"""

from .base import CrawlStrategy
from .bfs import BFSCrawlStrategy
from .dfs import DFSCrawlStrategy

__all__ = [
    'CrawlStrategy',
    'BFSCrawlStrategy',
    'DFSCrawlStrategy',
]
