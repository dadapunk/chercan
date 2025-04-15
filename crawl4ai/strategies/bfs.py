"""Breadth-First Search (BFS) crawling strategy implementation.

This module implements the BFS crawling strategy, which visits pages level by level,
exploring all pages at the current depth before moving to the next depth.
"""
from typing import List, Dict, Optional, Tuple, Set, Deque
from collections import deque
from urllib.parse import urljoin

from .base import CrawlStrategy


class BFSCrawlStrategy(CrawlStrategy):
    """Breadth-First Search (BFS) crawling strategy.
    
    This strategy explores all pages at the current depth before moving
    to the next depth. This is often useful for comprehensive exploration
    of a website structure.
    """
    
    def __init__(self, max_depth: int = 1, max_pages: int = 10, same_domain_only: bool = True):
        """Initialize the BFS crawling strategy.
        
        Args:
            max_depth: Maximum crawl depth (0 for single page)
            max_pages: Maximum number of pages to crawl
            same_domain_only: Whether to only crawl URLs in the same domain
        """
        super().__init__(max_depth, max_pages)
        self.same_domain_only = same_domain_only
        
        # Initialize queue with (url, depth) tuples
        self.queue: Deque[Tuple[str, int]] = deque()
        self.start_url: Optional[str] = None
    
    def add_start_url(self, url: str) -> None:
        """Add the starting URL to the queue.
        
        Args:
            url: Starting URL
        """
        self.start_url = self.normalize_url(url)
        self.queue.append((self.start_url, 0))  # Start at depth 0
        self.logger.info(f"Added start URL: {self.start_url}")
    
    async def get_next_url(self) -> Optional[str]:
        """Get the next URL to crawl according to BFS strategy.
        
        Returns:
            Next URL to crawl or None if no more URLs to crawl
        """
        if not self.queue:
            return None
        
        url, _ = self.queue.popleft()  # Get URL from the left (FIFO)
        
        if self.should_visit(url):
            return url
        else:
            # If we can't visit this URL, try the next one
            return await self.get_next_url()
    
    def add_urls(self, urls: List[str], source_url: str, depth: int) -> None:
        """Add new URLs to the crawl queue according to BFS strategy.
        
        Args:
            urls: List of URLs to add
            source_url: URL where these URLs were found
            depth: Current crawl depth
        """
        # If we've reached max depth, don't add more URLs
        if depth >= self.max_depth:
            return
        
        next_depth = depth + 1
        source_url = self.normalize_url(source_url)
        
        for url in urls:
            # Handle relative URLs
            if not url.startswith(('http://', 'https://')):
                url = urljoin(source_url, url)
            
            # Normalize URL
            url = self.normalize_url(url)
            
            # Skip URLs that have already been visited or queued
            if url in self.visited_urls or any(url == queued_url for queued_url, _ in self.queue):
                continue
            
            # Skip URLs from different domains if same_domain_only is True
            if self.same_domain_only and self.start_url and not self.is_same_domain(url, self.start_url):
                self.logger.debug(f"Skipping URL from different domain: {url}")
                continue
            
            # Add URL to queue with its depth
            self.queue.append((url, next_depth))
            self.logger.debug(f"Added URL to queue: {url} (depth={next_depth})")
    
    def reset(self) -> None:
        """Reset the strategy state."""
        super().reset()
        self.queue.clear()
        self.start_url = None 