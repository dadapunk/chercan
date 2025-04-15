"""Tests for the HTTP-only crawler implementation."""

import os
import pytest
import aiohttp
from unittest.mock import patch, MagicMock

from crawl4ai.crawlers.http_crawler import HTTPCrawler
from crawl4ai.models.page import Page


@pytest.fixture
def mock_http_response():
    """Mock HTTP response fixture."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.text.return_value = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <a href="https://example.com/page1">Link 1</a>
            <a href="/page2">Link 2</a>
            <a href="page3">Link 3</a>
        </body>
    </html>
    """
    return mock_response


@pytest.fixture
def mock_session():
    """Mock aiohttp session fixture."""
    session = MagicMock()
    return session


@pytest.mark.asyncio
async def test_http_crawler_initialization():
    """Test HTTPCrawler initialization with default and custom parameters."""
    # Test with default parameters
    crawler = HTTPCrawler()
    assert crawler.user_agent.startswith("Crawl4AI")
    assert crawler.timeout == 30
    assert crawler.retry_count == 3
    assert crawler.headers == {"User-Agent": crawler.user_agent}
    assert crawler.cookies == {}
    
    # Test with custom parameters
    custom_ua = "Custom User Agent"
    custom_timeout = 60
    custom_headers = {"User-Agent": custom_ua, "Accept": "text/html"}
    custom_cookies = {"session": "test"}
    
    crawler = HTTPCrawler(
        user_agent=custom_ua,
        timeout=custom_timeout,
        retry_count=5,
        headers=custom_headers,
        cookies=custom_cookies
    )
    
    assert crawler.user_agent == custom_ua
    assert crawler.timeout == custom_timeout
    assert crawler.retry_count == 5
    assert crawler.headers == custom_headers
    assert crawler.cookies == custom_cookies


@pytest.mark.asyncio
async def test_http_crawler_context_manager():
    """Test the context manager functionality of HTTPCrawler."""
    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session_instance = MagicMock()
        mock_session_class.return_value = mock_session_instance
        
        async with HTTPCrawler() as crawler:
            assert crawler.session is mock_session_instance
        
        # Verify session was closed
        mock_session_instance.close.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_page(mock_session, mock_http_response):
    """Test fetching a page using the HTTP crawler."""
    url = "https://example.com"
    mock_session.get.return_value.__aenter__.return_value = mock_http_response
    
    crawler = HTTPCrawler()
    crawler.session = mock_session
    
    page = await crawler.fetch_page(url)
    
    assert isinstance(page, Page)
    assert page.url == url
    assert page.status_code == 200
    assert page.title == "Test Page"
    assert len(page.links) == 3
    assert "https://example.com/page1" in page.links
    assert "https://example.com/page2" in page.links
    assert "https://example.com/page3" in page.links


@pytest.mark.asyncio
async def test_retry_mechanism():
    """Test the retry mechanism for failed requests."""
    url = "https://example.com"
    
    # Create a session mock that fails twice then succeeds
    mock_session = MagicMock()
    
    # First two calls raise an exception
    mock_session.get.side_effect = [
        aiohttp.ClientError("Connection error"),
        aiohttp.ClientError("Timeout error"),
        MagicMock()  # Third call succeeds
    ]
    
    # Setup the successful response
    success_response = MagicMock()
    success_response.status = 200
    success_response.headers = {"content-type": "text/html"}
    success_response.text.return_value = "<html><body>Success</body></html>"
    
    # Make sure the third call returns the success response
    mock_session.get.return_value.__aenter__.return_value = success_response
    
    crawler = HTTPCrawler(retry_count=3)
    crawler.session = mock_session
    
    page = await crawler.fetch_page(url)
    
    # Verify the page was successfully fetched after retries
    assert isinstance(page, Page)
    assert page.url == url
    assert page.status_code == 200
    assert mock_session.get.call_count == 3


@pytest.mark.asyncio
async def test_crawl_with_depth():
    """Test the crawl method with different depths."""
    with patch.object(HTTPCrawler, 'fetch_page') as mock_fetch:
        # Setup mock pages for different depths
        root_page = Page(
            url="https://example.com",
            html="<html><body>Root</body></html>",
            title="Root",
            links=["https://example.com/page1", "https://example.com/page2"]
        )
        
        page1 = Page(
            url="https://example.com/page1",
            html="<html><body>Page 1</body></html>",
            title="Page 1",
            links=["https://example.com/page3"]
        )
        
        page2 = Page(
            url="https://example.com/page2",
            html="<html><body>Page 2</body></html>",
            title="Page 2",
            links=[]
        )
        
        page3 = Page(
            url="https://example.com/page3",
            html="<html><body>Page 3</body></html>",
            title="Page 3",
            links=[]
        )
        
        # Configure mock to return different pages based on URL
        async def side_effect(url):
            if url == "https://example.com":
                return root_page
            elif url == "https://example.com/page1":
                return page1
            elif url == "https://example.com/page2":
                return page2
            elif url == "https://example.com/page3":
                return page3
            
        mock_fetch.side_effect = side_effect
        
        # Test with depth = 1 (only root page)
        crawler = HTTPCrawler()
        results = await crawler.crawl("https://example.com", depth=1, follow_links=True)
        
        assert len(results) == 1
        assert "https://example.com" in results
        
        # Test with depth = 2 (root + page1 + page2)
        results = await crawler.crawl("https://example.com", depth=2, follow_links=True)
        
        assert len(results) == 3
        assert "https://example.com" in results
        assert "https://example.com/page1" in results
        assert "https://example.com/page2" in results
        
        # Test with depth = 3 (all pages)
        results = await crawler.crawl("https://example.com", depth=3, follow_links=True)
        
        assert len(results) == 4
        assert "https://example.com" in results
        assert "https://example.com/page1" in results
        assert "https://example.com/page2" in results
        assert "https://example.com/page3" in results 