"""Base crawler implementation using AsyncWebCrawler from Crawl4AI.

This module provides a base crawler class that can be extended for different crawling strategies.
"""
from typing import Dict, List, Optional, Any, Union
import asyncio
from pathlib import Path
import json

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CrawlResult

from crawl4ai.config import logger, get_logger
from crawl4ai.config.settings import (
    DEFAULT_USER_AGENT,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRY_COUNT,
)
from crawl4ai.core.exceptions import CrawlerError, RequestError


class BaseCrawler:
    """Base crawler class that wraps AsyncWebCrawler from Crawl4AI.
    
    This class provides a consistent interface for all crawler implementations
    and handles common configuration options.
    """
    
    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        cache_dir: Optional[Union[str, Path]] = None,
        browser_config: Optional[Dict[str, Any]] = None,
        crawler_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the base crawler.
        
        Args:
            user_agent: User agent string to use for requests
            timeout: Request timeout in seconds
            retry_count: Number of times to retry failed requests
            headers: Additional HTTP headers to include in requests
            cookies: Cookies to include in requests
            cache_dir: Directory to use for caching responses
            browser_config: Additional browser configuration options
            crawler_config: Additional crawler configuration options
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.retry_count = retry_count
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        # Set up logging
        self.logger = get_logger("core.crawler")
        
        # Configure browser options
        self._browser_config = {
            "user_agent": self.user_agent,
            "timeout": self.timeout,
        }
        if browser_config:
            self._browser_config.update(browser_config)
        
        # Configure crawler options
        self._crawler_config = {
            "retry_count": self.retry_count,
        }
        if crawler_config:
            self._crawler_config.update(crawler_config)
        
        # Will be initialized in the context manager
        self._crawler = None
    
    async def __aenter__(self):
        """Async context manager entry.
        
        Returns:
            Self instance with initialized crawler
        """
        try:
            # Create browser config
            browser_config = BrowserConfig(**self._browser_config)
            
            # Create crawler config
            crawler_config = CrawlerRunConfig(**self._crawler_config)
            
            # Initialize the crawler
            self._crawler = AsyncWebCrawler(
                browser_config=browser_config,
            )
            
            # Enter the crawler context
            await self._crawler.__aenter__()
            
            self.logger.info("Crawler initialized successfully")
            return self
        except Exception as e:
            self.logger.error(f"Failed to initialize crawler: {str(e)}")
            raise CrawlerError(f"Failed to initialize crawler: {str(e)}")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self._crawler:
            await self._crawler.__aexit__(exc_type, exc_val, exc_tb)
            self._crawler = None
        self.logger.info("Crawler closed")
    
    async def crawl(
        self,
        url: str,
        depth: int = 0,
        follow_links: bool = False,
        max_pages: int = 1,
        **kwargs,
    ) -> CrawlResult:
        """Crawl a URL and return the result.
        
        Args:
            url: URL to crawl
            depth: Crawl depth (0 for single page)
            follow_links: Whether to follow links
            max_pages: Maximum number of pages to crawl
            **kwargs: Additional arguments to pass to crawler.arun()
            
        Returns:
            CrawlResult object containing the crawl results
            
        Raises:
            CrawlerError: If the crawler is not initialized or an error occurs
        """
        if not self._crawler:
            raise CrawlerError("Crawler not initialized, use async with context")
        
        try:
            # Set up crawl parameters
            crawl_params = {
                "url": url,
                "depth": depth,
                "follow_links": follow_links,
                "max_pages": max_pages,
            }
            
            # Add additional parameters
            crawl_params.update(kwargs)
            
            # Log crawl operation
            self.logger.info(f"Crawling URL: {url} (depth={depth}, max_pages={max_pages})")
            
            # Execute the crawl
            result = await self._crawler.arun(**crawl_params)
            
            self.logger.info(f"Crawl completed: {result.stats.pages_crawled} pages crawled")
            return result
        except Exception as e:
            self.logger.error(f"Error during crawl: {str(e)}")
            raise RequestError(f"Error during crawl: {str(e)}", url=url)
    
    async def get_page(self, url: str, **kwargs) -> CrawlResult:
        """Get a single page without following links.
        
        Args:
            url: URL to fetch
            **kwargs: Additional arguments to pass to crawl()
            
        Returns:
            CrawlResult object containing the page content
        """
        return await self.crawl(url, depth=0, follow_links=False, max_pages=1, **kwargs)
    
    def get_browser_config(self) -> Dict[str, Any]:
        """Get the current browser configuration.
        
        Returns:
            Dictionary with browser configuration options
        """
        return self._browser_config.copy()
    
    def get_crawler_config(self) -> Dict[str, Any]:
        """Get the current crawler configuration.
        
        Returns:
            Dictionary with crawler configuration options
        """
        return self._crawler_config.copy()
    
    def update_browser_config(self, **kwargs) -> None:
        """Update browser configuration options.
        
        Args:
            **kwargs: Configuration options to update
        """
        self._browser_config.update(kwargs)
    
    def update_crawler_config(self, **kwargs) -> None:
        """Update crawler configuration options.
        
        Args:
            **kwargs: Configuration options to update
        """
        self._crawler_config.update(kwargs) 