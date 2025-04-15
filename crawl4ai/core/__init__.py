"""Core module for Crawl4AI framework.

This package provides core functionality for the framework,
including base classes and utilities.
"""

from .exceptions import (
    Crawl4AIError,
    ConfigurationError,
    CrawlerError,
    RequestError,
    BrowserError,
    StrategyError,
    ExtractorError,
    FilterError,
    ExportError,
    ResourceLimitError,
    AuthenticationError,
)

from .crawler import BaseCrawler
from .session import CrawlerSession

__all__ = [
    'Crawl4AIError',
    'ConfigurationError',
    'CrawlerError',
    'RequestError',
    'BrowserError',
    'StrategyError',
    'ExtractorError',
    'FilterError',
    'ExportError',
    'ResourceLimitError',
    'AuthenticationError',
    'BaseCrawler',
    'CrawlerSession',
]
