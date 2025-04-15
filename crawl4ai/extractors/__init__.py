"""Extractors for the Crawl4AI framework.

This package provides extractors for extracting structured data from web pages.
"""

from .base_extractor import BaseExtractor
from .css_extractor import CSSExtractor

__all__ = [
    'BaseExtractor',
    'CSSExtractor',
] 