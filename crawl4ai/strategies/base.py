"""Base crawling strategy implementation.

This module defines the base interface for all crawling strategies.
"""
from typing import List, Set, Dict, Any, Optional, Protocol, Callable, Awaitable
from abc import ABC, abstractmethod
import asyncio
from urllib.parse import urljoin, urlparse
import logging

from crawl4ai import CrawlResult
from crawl4ai.core.exceptions import StrategyError


class CrawlStrategy(ABC):
    """Base class for all crawling strategies.
    
    This abstract class defines the interface that all crawling strategies
    must implement. Strategies determine the order in which URLs are crawled.
    """
    
    def __init__(self, max_depth: int = 1, max_pages: int = 10):
        """Initialize the crawling strategy.
        
        Args:
            max_depth: Maximum crawl depth (0 for single page)
            max_pages: Maximum number of pages to crawl
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.pages_crawled = 0
        self.logger = logging.getLogger(f"crawl4ai.strategies.{self.__class__.__name__}")
    
    @abstractmethod
    async def get_next_url(self) -> Optional[str]:
        """Get the next URL to crawl according to the strategy.
        
        Returns:
            Next URL to crawl or None if no more URLs to crawl
        """
        pass
    
    @abstractmethod
    def add_urls(self, urls: List[str], source_url: str, depth: int) -> None:
        """Add new URLs to the crawl queue.
        
        Args:
            urls: List of URLs to add
            source_url: URL where these URLs were found
            depth: Current crawl depth
        """
        pass
    
    def should_visit(self, url: str) -> bool:
        """Check if a URL should be visited.
        
        Args:
            url: URL to check
            
        Returns:
            True if the URL should be visited, False otherwise
        """
        # Don't revisit URLs
        if url in self.visited_urls:
            return False
        
        # Check if we've reached the maximum number of pages
        if self.pages_crawled >= self.max_pages:
            return False
        
        return True
    
    def mark_visited(self, url: str) -> None:
        """Mark a URL as visited.
        
        Args:
            url: URL to mark as visited
        """
        self.visited_urls.add(url)
        self.pages_crawled += 1
    
    def reset(self) -> None:
        """Reset the strategy state."""
        self.visited_urls.clear()
        self.pages_crawled = 0
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize a URL for comparison.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        # Basic normalization (could be extended)
        parsed = urlparse(url)
        
        # Normalize scheme
        scheme = parsed.scheme.lower() or "http"
        
        # Normalize netloc (remove www. prefix, lowercase)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        
        # Normalize path (add trailing slash if empty)
        path = parsed.path
        if not path:
            path = "/"
        
        # Rebuild URL (ignoring fragments)
        normalized = f"{scheme}://{netloc}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        
        return normalized
    
    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:
        """Check if two URLs belong to the same domain.
        
        Args:
            url1: First URL
            url2: Second URL
            
        Returns:
            True if the URLs belong to the same domain, False otherwise
        """
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        
        # Remove www. prefix if present
        if domain1.startswith("www."):
            domain1 = domain1[4:]
        if domain2.startswith("www."):
            domain2 = domain2[4:]
        
        return domain1 == domain2 