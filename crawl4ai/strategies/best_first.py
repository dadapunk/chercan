"""Best-First Search crawling strategy implementation.

This module implements the Best-First Search crawling strategy, which prioritizes
URLs based on a heuristic scoring function to visit the most valuable pages first.
"""
from typing import List, Dict, Optional, Tuple, Set, Callable, Any, Union
import re
from urllib.parse import urljoin, urlparse
import heapq
from functools import partial

from .base import CrawlStrategy


class BestFirstCrawlStrategy(CrawlStrategy):
    """Best-First Search crawling strategy.
    
    This strategy prioritizes URLs based on a heuristic scoring function,
    always choosing to visit the URL with the highest score next. This is useful
    for efficiently finding the most valuable content on a website.
    """
    
    def __init__(
        self, 
        max_depth: int = 3, 
        max_pages: int = 10, 
        same_domain_only: bool = True,
        scoring_function: Optional[Callable[[str, str, int], float]] = None,
        keyword_weights: Optional[Dict[str, float]] = None,
    ):
        """Initialize the Best-First crawling strategy.
        
        Args:
            max_depth: Maximum crawl depth (0 for single page)
            max_pages: Maximum number of pages to crawl
            same_domain_only: Whether to only crawl URLs in the same domain
            scoring_function: Custom function to score URLs (str, source_url, depth) -> float
            keyword_weights: Dictionary of keywords to weights for default scoring
        """
        super().__init__(max_depth, max_pages)
        self.same_domain_only = same_domain_only
        
        # Use custom scoring function if provided, otherwise use default
        self.scoring_function = scoring_function or self._default_scoring_function
        
        # Keywords for scoring (if no custom function)
        self.keyword_weights = keyword_weights or {
            # Common valuable content indicators
            "product": 1.5,
            "category": 1.2,
            "article": 1.0,
            "blog": 0.9,
            "about": 0.7,
            "contact": 0.5,
            "index": 0.3,
            "page": 0.2,
        }
        
        # Priority queue for URLs:
        # We use a list of (-score, url, depth) tuples
        # The negative score is because heapq is a min-heap, but we want highest scores first
        self.queue: List[Tuple[float, str, int]] = []
        
        # Track URL scores for debugging
        self.url_scores: Dict[str, float] = {}
        
        # Start URL
        self.start_url: Optional[str] = None
    
    def add_start_url(self, url: str) -> None:
        """Add the starting URL to the queue.
        
        Args:
            url: Starting URL
        """
        self.start_url = self.normalize_url(url)
        # Start URL gets maximum score
        score = float('inf')  # Ensures start URL is crawled first
        self.url_scores[self.start_url] = score
        heapq.heappush(self.queue, (-score, self.start_url, 0))
        self.logger.info(f"Added start URL: {self.start_url}")
    
    async def get_next_url(self) -> Optional[str]:
        """Get the next URL to crawl according to Best-First strategy.
        
        Returns:
            Next URL to crawl or None if no more URLs to crawl
        """
        if not self.queue:
            return None
        
        # Get URL with highest score
        _, url, _ = heapq.heappop(self.queue)
        
        if self.should_visit(url):
            return url
        else:
            # If we can't visit this URL, try the next one
            return await self.get_next_url()
    
    def add_urls(self, urls: List[str], source_url: str, depth: int) -> None:
        """Add new URLs to the crawl queue according to Best-First strategy.
        
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
            if url in self.visited_urls or url in self.url_scores:
                continue
            
            # Skip URLs from different domains if same_domain_only is True
            if self.same_domain_only and self.start_url and not self.is_same_domain(url, self.start_url):
                self.logger.debug(f"Skipping URL from different domain: {url}")
                continue
            
            # Score the URL
            score = self.scoring_function(url, source_url, next_depth)
            
            # Store score for debugging
            self.url_scores[url] = score
            
            # Add URL to queue with its score (negative because heapq is a min-heap)
            heapq.heappush(self.queue, (-score, url, next_depth))
            self.logger.debug(f"Added URL to queue: {url} (depth={next_depth}, score={score:.2f})")
    
    def _default_scoring_function(self, url: str, source_url: str, depth: int) -> float:
        """Default scoring function for URLs.
        
        The default scoring system considers:
        1. URL keywords (e.g., 'product', 'category')
        2. URL depth (shorter URLs score higher)
        3. Depth in crawl (earlier depths score higher)
        
        Args:
            url: URL to score
            source_url: Source URL where this URL was found
            depth: Current crawl depth
            
        Returns:
            Score value (higher is better)
        """
        # Base score starts at 1.0
        score = 1.0
        
        # Parse URL for analysis
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # 1. Check for valuable keywords in the URL
        for keyword, weight in self.keyword_weights.items():
            if keyword.lower() in path:
                score += weight
        
        # 2. Prefer shorter URLs (fewer path segments)
        path_segments = [s for s in path.split('/') if s]
        segment_penalty = 0.1 * len(path_segments)
        score -= segment_penalty
        
        # 3. Prefer URLs at earlier depths
        depth_penalty = 0.2 * depth
        score -= depth_penalty
        
        # 4. Prefer URLs with few or no query parameters
        if parsed.query:
            query_penalty = 0.1 * len(parsed.query.split('&'))
            score -= query_penalty
        
        # 5. Bonus for URLs that might be listing pages
        if re.search(r'/(category|product|list|catalog)/', path):
            score += 0.5
        
        # Ensure score is positive
        return max(0.1, score)
    
    def reset(self) -> None:
        """Reset the strategy state."""
        super().reset()
        self.queue = []
        self.url_scores = {}
        self.start_url = None 