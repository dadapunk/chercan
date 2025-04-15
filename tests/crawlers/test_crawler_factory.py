"""Tests for the crawler factory and type selection mechanism."""

import pytest
from unittest.mock import patch, MagicMock

from crawl4ai.crawlers import CrawlerFactory, CrawlerType
from crawl4ai.crawlers.http_crawler import HTTPCrawler
from crawl4ai.crawlers.playwright_crawler import PlaywrightCrawler
from crawl4ai.crawlers.strategy_crawler import StrategyCrawler
from crawl4ai.core.exceptions import ConfigurationError


def test_crawler_factory_http():
    """Test creating an HTTP crawler using the factory."""
    crawler = CrawlerFactory.create(CrawlerType.HTTP)
    assert isinstance(crawler, HTTPCrawler)


def test_crawler_factory_browser():
    """Test creating a browser-based crawler using the factory."""
    crawler = CrawlerFactory.create(CrawlerType.BROWSER)
    assert isinstance(crawler, PlaywrightCrawler)


def test_crawler_factory_strategy():
    """Test creating a strategy crawler using the factory."""
    crawler = CrawlerFactory.create(CrawlerType.STRATEGY)
    assert isinstance(crawler, StrategyCrawler)


def test_crawler_factory_string_type():
    """Test creating a crawler using a string type."""
    crawler = CrawlerFactory.create("http")
    assert isinstance(crawler, HTTPCrawler)
    
    crawler = CrawlerFactory.create("BROWSER")  # Case-insensitive
    assert isinstance(crawler, PlaywrightCrawler)
    
    crawler = CrawlerFactory.create("strategy")
    assert isinstance(crawler, StrategyCrawler)


def test_crawler_factory_invalid_type():
    """Test error handling for invalid crawler types."""
    with pytest.raises(ConfigurationError):
        CrawlerFactory.create("invalid_type")


def test_crawler_factory_invalid_config():
    """Test error handling for invalid configuration."""
    with pytest.raises(ConfigurationError):
        # PlaywrightCrawler requires valid browser_name
        CrawlerFactory.create(CrawlerType.BROWSER, browser_name="invalid_browser")


def test_crawler_factory_registration():
    """Test registering a new crawler type."""
    # Create a mock crawler class
    MockCrawler = MagicMock()
    
    # Register the new crawler type
    CrawlerFactory.register_crawler("mock", MockCrawler)
    
    # Create a crawler of the new type
    CrawlerFactory.create("mock")
    
    # Verify the mock crawler was instantiated
    MockCrawler.assert_called_once()
    
    # Test registering an existing type
    with pytest.raises(ConfigurationError):
        CrawlerFactory.register_crawler("mock", MockCrawler)


def test_get_crawler_types():
    """Test getting available crawler types."""
    types = CrawlerFactory.get_crawler_types()
    assert "http" in types
    assert "browser" in types
    assert "strategy" in types


def test_get_recommended_crawler():
    """Test getting the recommended crawler for a URL."""
    # For non-JavaScript sites
    crawler_type = CrawlerFactory.get_recommended_crawler("https://example.com")
    assert crawler_type == CrawlerType.HTTP
    
    # For JavaScript-heavy sites
    crawler_type = CrawlerFactory.get_recommended_crawler(
        "https://example.com", 
        javascript_required=True
    )
    assert crawler_type == CrawlerType.BROWSER 