"""Crawler factory for selecting and creating different crawler types.

This module provides a factory class for creating different types of crawlers
based on the use case, such as browser-based crawling or HTTP-only crawling.
"""
from typing import Dict, List, Optional, Any, Union, Literal, Type
from enum import Enum

from crawl4ai.core.crawler import BaseCrawler
from crawl4ai.crawlers.http_crawler import HTTPCrawler
from crawl4ai.crawlers.playwright_crawler import PlaywrightCrawler
from crawl4ai.crawlers.strategy_crawler import StrategyCrawler
from crawl4ai.core.exceptions import ConfigurationError


class CrawlerType(Enum):
    """Enum for different crawler types."""
    
    HTTP = "http"
    BROWSER = "browser"
    STRATEGY = "strategy"


class CrawlerFactory:
    """Factory for creating different types of crawlers.
    
    This factory provides a simple interface for creating crawler instances
    based on the desired crawler type and configuration.
    
    Example usage:
    ```python
    # Create an HTTP crawler
    http_crawler = CrawlerFactory.create(CrawlerType.HTTP, timeout=30)
    
    # Create a browser-based crawler
    browser_crawler = CrawlerFactory.create(
        CrawlerType.BROWSER, 
        browser_name="chromium",
        headless=True
    )
    
    # Create a strategy crawler with BFS strategy
    strategy_crawler = CrawlerFactory.create(
        CrawlerType.STRATEGY,
        strategy="bfs",
        strategy_options={"same_domain_only": True}
    )
    ```
    """
    
    _crawler_registry = {
        CrawlerType.HTTP: HTTPCrawler,
        CrawlerType.BROWSER: PlaywrightCrawler,
        CrawlerType.STRATEGY: StrategyCrawler,
    }
    
    @classmethod
    def create(
        cls,
        crawler_type: Union[CrawlerType, str],
        **kwargs
    ) -> BaseCrawler:
        """Create a crawler instance of the specified type.
        
        Args:
            crawler_type: Type of crawler to create
            **kwargs: Configuration options for the crawler
            
        Returns:
            An instance of the requested crawler type
            
        Raises:
            ConfigurationError: If the crawler type is invalid or configuration is incorrect
        """
        # Convert string to enum if necessary
        if isinstance(crawler_type, str):
            try:
                crawler_type = CrawlerType(crawler_type.lower())
            except ValueError:
                valid_types = [t.value for t in CrawlerType]
                raise ConfigurationError(
                    f"Invalid crawler type: {crawler_type}. "
                    f"Valid types are: {', '.join(valid_types)}"
                )
        
        # Get the crawler class
        if crawler_type not in cls._crawler_registry:
            valid_types = [t.value for t in CrawlerType]
            raise ConfigurationError(
                f"Invalid crawler type: {crawler_type}. "
                f"Valid types are: {', '.join(valid_types)}"
            )
        
        crawler_class = cls._crawler_registry[crawler_type]
        
        # Create and return the crawler instance
        try:
            return crawler_class(**kwargs)
        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration for {crawler_type.value} crawler: {str(e)}")
    
    @classmethod
    def register_crawler(
        cls,
        crawler_type: Union[CrawlerType, str],
        crawler_class: Type[BaseCrawler]
    ) -> None:
        """Register a new crawler type.
        
        Args:
            crawler_type: Type identifier for the crawler
            crawler_class: Crawler class to register
            
        Raises:
            ConfigurationError: If the crawler type is already registered
        """
        # Convert string to enum if necessary
        if isinstance(crawler_type, str):
            crawler_type = CrawlerType(crawler_type.lower())
        
        if crawler_type in cls._crawler_registry:
            raise ConfigurationError(f"Crawler type {crawler_type.value} is already registered")
        
        cls._crawler_registry[crawler_type] = crawler_class
    
    @classmethod
    def get_crawler_types(cls) -> List[str]:
        """Get a list of available crawler types.
        
        Returns:
            List of crawler type names
        """
        return [t.value for t in cls._crawler_registry.keys()]
    
    @classmethod
    def get_recommended_crawler(cls, url: str, javascript_required: bool = False) -> CrawlerType:
        """Get the recommended crawler type for a given URL.
        
        Args:
            url: URL to be crawled
            javascript_required: Whether JavaScript execution is required
            
        Returns:
            Recommended crawler type
        """
        if javascript_required:
            return CrawlerType.BROWSER
        else:
            return CrawlerType.HTTP 