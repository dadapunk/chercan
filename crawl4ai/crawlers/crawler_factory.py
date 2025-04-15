"""Crawler factory for selecting and creating different crawler types.

This module provides a factory class for creating different types of crawlers
based on the use case, such as browser-based crawling or HTTP-only crawling.
"""
from typing import Dict, List, Optional, Any, Union, Literal, Type
from enum import Enum
from pathlib import Path

from crawl4ai.core.crawler import BaseCrawler
from crawl4ai.crawlers.http_crawler import HTTPCrawler
from crawl4ai.crawlers.playwright_crawler import PlaywrightCrawler
from crawl4ai.crawlers.strategy_crawler import StrategyCrawler
from crawl4ai.core.exceptions import ConfigurationError
from crawl4ai.utils.performance_monitor import PerformanceMonitor
from crawl4ai.middleware.performance_middleware import PerformanceMonitorMiddleware


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
    
    # Create a crawler with performance monitoring
    crawler = CrawlerFactory.create_with_monitoring(
        CrawlerType.HTTP,
        monitor_output_dir="performance_reports"
    )
    ```
    """
    
    _crawler_registry = {
        CrawlerType.HTTP: HTTPCrawler,
        CrawlerType.BROWSER: PlaywrightCrawler,
        CrawlerType.STRATEGY: StrategyCrawler,
    }
    
    # Shared performance monitor instance for comparing crawler types
    _performance_monitor: Optional[PerformanceMonitor] = None
    
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
    def create_with_monitoring(
        cls,
        crawler_type: Union[CrawlerType, str],
        monitor_output_dir: Optional[Union[str, Path]] = None,
        auto_generate_report: bool = True,
        report_output_file: Optional[str] = None,
        **kwargs
    ) -> BaseCrawler:
        """Create a crawler with performance monitoring.
        
        This method creates a crawler with a performance monitoring middleware
        attached, which records metrics during crawling for later analysis.
        
        Args:
            crawler_type: Type of crawler to create
            monitor_output_dir: Directory to save performance metrics
            auto_generate_report: Whether to automatically generate a report
            report_output_file: File to save the report to
            **kwargs: Additional configuration options for the crawler
            
        Returns:
            A crawler instance with performance monitoring
            
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
        
        # Initialize performance monitor if needed
        if cls._performance_monitor is None:
            cls._performance_monitor = PerformanceMonitor(output_dir=monitor_output_dir)
        
        # Create the crawler
        crawler = cls.create(crawler_type, **kwargs)
        
        # Add performance monitoring middleware
        middleware = PerformanceMonitorMiddleware(
            monitor=cls._performance_monitor,
            crawler_type=crawler_type.value,
            auto_generate_report=auto_generate_report,
            report_output_file=report_output_file
        )
        
        # Check if the crawler has an add_middleware method
        if hasattr(crawler, 'add_middleware'):
            crawler.add_middleware(middleware)
        else:
            # Fall back to storing the middleware for later use
            if not hasattr(crawler, '_middlewares'):
                crawler._middlewares = []
            crawler._middlewares.append(middleware)
            
        return crawler
    
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
    
    @classmethod
    def get_performance_comparison(cls, url: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get performance comparison between different crawler types.
        
        This method returns a comparison of performance metrics for different crawler
        types that have been used with performance monitoring.
        
        Args:
            url: Optional URL to filter metrics by
            
        Returns:
            Dictionary mapping crawler types to their average metrics
        """
        if cls._performance_monitor is None:
            return {}
        
        return cls._performance_monitor.get_crawler_comparison(url)
    
    @classmethod
    def generate_performance_report(cls, output_file: Optional[Union[str, Path]] = None) -> str:
        """Generate a performance report for all crawler types used.
        
        Args:
            output_file: Optional file to save the report
            
        Returns:
            Report as a string
        """
        if cls._performance_monitor is None:
            return "No performance metrics available. Use create_with_monitoring() to collect metrics."
        
        return cls._performance_monitor.generate_report(output_file) 