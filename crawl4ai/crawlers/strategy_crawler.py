"""Strategy-aware crawler implementation.

This module provides a crawler that can use different crawling strategies
to determine the order in which URLs are crawled.
"""
from typing import Dict, List, Optional, Any, Union, Type
import asyncio
from pathlib import Path
import json
import re
from urllib.parse import urljoin, urlparse

from crawl4ai import CrawlResult
from crawl4ai.core.crawler import BaseCrawler
from crawl4ai.strategies import (
    CrawlStrategy, 
    BFSCrawlStrategy, 
    DFSCrawlStrategy,
    BestFirstCrawlStrategy,
    StrategyFactory
)
from crawl4ai.core.exceptions import StrategyError, CrawlerError


class StrategyCrawler(BaseCrawler):
    """Strategy-aware crawler that can use different crawling strategies.
    
    This crawler extends BaseCrawler to support different crawling strategies
    that determine the order in which URLs are crawled.
    """
    
    def __init__(
        self,
        strategy: Optional[Union[CrawlStrategy, str]] = None,
        strategy_options: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Initialize the strategy crawler.
        
        Args:
            strategy: Crawling strategy to use (either a strategy instance or a strategy name)
            strategy_options: Options for the strategy (if strategy is a name)
            **kwargs: Additional arguments to pass to BaseCrawler.__init__()
        """
        super().__init__(**kwargs)
        
        # Set up strategy
        strategy_options = strategy_options or {}
        
        if isinstance(strategy, str):
            # Create strategy from name using factory
            self.strategy = StrategyFactory.create_strategy(strategy, **strategy_options)
            self.logger.info(f"Created {strategy} crawling strategy")
        elif isinstance(strategy, CrawlStrategy):
            # Use provided strategy instance
            self.strategy = strategy
            self.logger.info(f"Using provided crawling strategy: {strategy.__class__.__name__}")
        else:
            # Default to BFS
            self.strategy = BFSCrawlStrategy()
            self.logger.info(f"Using default BFS crawling strategy")
    
    def set_strategy(self, strategy: Union[CrawlStrategy, str], **options) -> None:
        """Set the crawling strategy.
        
        Args:
            strategy: Crawling strategy to use (either a strategy instance or a strategy name)
            **options: Options for the strategy (if strategy is a name)
        """
        if isinstance(strategy, str):
            # Create strategy from name using factory
            self.strategy = StrategyFactory.create_strategy(strategy, **options)
            self.logger.info(f"Changed to {strategy} crawling strategy")
        elif isinstance(strategy, CrawlStrategy):
            # Use provided strategy instance
            self.strategy = strategy
            self.logger.info(f"Changed to provided crawling strategy: {strategy.__class__.__name__}")
        else:
            raise TypeError(f"Strategy must be a string or CrawlStrategy instance, got {type(strategy)}")
    
    async def crawl_with_strategy(
        self,
        url: str,
        max_pages: int = 10,
        max_depth: int = 1,
        same_domain_only: bool = True,
        follow_links: bool = True,
        **kwargs,
    ) -> CrawlResult:
        """Crawl a website using the configured strategy.
        
        Args:
            url: Starting URL to crawl
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum crawl depth
            same_domain_only: Whether to only crawl URLs in the same domain
            follow_links: Whether to follow links
            **kwargs: Additional arguments to pass to crawler.arun()
            
        Returns:
            CrawlResult object containing the crawl results
            
        Raises:
            CrawlerError: If the crawler is not initialized
            StrategyError: If there's an error with the strategy
        """
        if not self._crawler:
            raise CrawlerError("Crawler not initialized, use async with context")
        
        # Configure strategy
        self.strategy.max_pages = max_pages
        self.strategy.max_depth = max_depth
        if hasattr(self.strategy, 'same_domain_only'):
            self.strategy.same_domain_only = same_domain_only
        
        # Reset strategy
        self.strategy.reset()
        
        # Add starting URL
        if hasattr(self.strategy, 'add_start_url'):
            self.strategy.add_start_url(url)
        else:
            # Fallback for strategies without add_start_url method
            self.strategy.add_urls([url], url, 0)
        
        # If not following links, just crawl the starting URL
        if not follow_links:
            return await self.crawl(url, **kwargs)
        
        # Initialize results
        results = []
        page_count = 0
        
        # Start crawling
        self.logger.info(f"Starting crawl with strategy: {self.strategy.__class__.__name__}")
        
        while page_count < max_pages:
            # Get next URL from strategy
            next_url = await self.strategy.get_next_url()
            if not next_url:
                self.logger.info("No more URLs to crawl")
                break
            
            # Crawl the URL
            self.logger.info(f"Crawling URL: {next_url}")
            try:
                result = await self.crawl(next_url, **kwargs)
                results.append(result)
                page_count += 1
                
                # Mark URL as visited
                self.strategy.mark_visited(next_url)
                
                # Extract links from the page
                if hasattr(result, 'links') and result.links:
                    # Find current depth
                    current_depth = 0
                    for depth_url, depth in getattr(self.strategy, 'queue', []):
                        if depth_url == next_url:
                            current_depth = depth
                            break
                    
                    # Add new URLs to the strategy
                    self.strategy.add_urls(result.links, next_url, current_depth)
                
            except Exception as e:
                self.logger.error(f"Error crawling {next_url}: {str(e)}")
                # Continue with next URL
                continue
        
        self.logger.info(f"Crawl completed: {page_count} pages crawled")
        
        # Combine results
        # For now, just return the first result (this would need to be enhanced)
        if results:
            return results[0]
        else:
            raise CrawlerError("No pages were successfully crawled")
    
    async def crawl(
        self,
        url: str,
        depth: int = 0,
        follow_links: bool = False,
        max_pages: int = 1,
        **kwargs,
    ) -> CrawlResult:
        """Override crawl method to use strategy if follow_links is True.
        
        Args:
            url: URL to crawl
            depth: Crawl depth (0 for single page)
            follow_links: Whether to follow links
            max_pages: Maximum number of pages to crawl
            **kwargs: Additional arguments to pass to crawler.arun()
            
        Returns:
            CrawlResult object containing the crawl results
        """
        if follow_links and depth > 0:
            return await self.crawl_with_strategy(
                url, 
                max_pages=max_pages,
                max_depth=depth,
                follow_links=follow_links,
                **kwargs
            )
        else:
            return await super().crawl(url, depth, follow_links, max_pages, **kwargs) 