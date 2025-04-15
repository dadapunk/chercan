"""HTTP-only crawler implementation for Crawl4AI.

This module provides an HTTP-only crawler that doesn't rely on browser automation,
making it faster but with limited JavaScript support.
"""
from typing import Dict, List, Optional, Any, Union
import asyncio
from pathlib import Path
import aiohttp
from urllib.parse import urlparse, urljoin

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CrawlResult
from crawl4ai.core.crawler import BaseCrawler
from crawl4ai.core.exceptions import RequestError, CrawlerError
from crawl4ai.config.settings import (
    DEFAULT_USER_AGENT,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRY_COUNT,
)


class HTTPCrawler(BaseCrawler):
    """HTTP-only crawler that uses aiohttp for requests without browser automation.
    
    This crawler is faster than browser-based crawlers but has limited JavaScript support.
    It's suitable for crawling static websites or API endpoints.
    """
    
    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        cache_dir: Optional[Union[str, Path]] = None,
        crawler_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the HTTP-only crawler.
        
        Args:
            user_agent: User agent string to use for requests
            timeout: Request timeout in seconds
            retry_count: Number of times to retry failed requests
            headers: Additional HTTP headers to include in requests
            cookies: Cookies to include in requests
            cache_dir: Directory to use for caching responses
            crawler_config: Additional crawler configuration options
        """
        super().__init__(
            user_agent=user_agent,
            timeout=timeout,
            retry_count=retry_count,
            headers=headers,
            cookies=cookies,
            cache_dir=cache_dir,
            browser_config=None,  # No browser config needed
            crawler_config=crawler_config,
        )
        
        # Will be initialized in the context manager
        self._session = None
        
    async def __aenter__(self):
        """Initialize the HTTP session when entering the context manager."""
        # Create aiohttp session
        self._session = aiohttp.ClientSession(
            headers={
                "User-Agent": self.user_agent,
                **self.headers
            },
            cookies=self.cookies,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        
        # Create crawler instance
        crawler_config = CrawlerRunConfig(
            **self._crawler_config
        )
        
        self._crawler = AsyncWebCrawler(
            crawler_config=crawler_config,
            browser_config=None,  # No browser config for HTTP-only crawler
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the HTTP session when exiting the context manager."""
        if self._session:
            await self._session.close()
        if self._crawler:
            await self._crawler.aclose()
            
    async def fetch_page(self, url: str) -> Dict[str, Any]:
        """Fetch a page using HTTP requests.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary containing page content and metadata
            
        Raises:
            RequestError: If the request fails
        """
        if not self._session:
            raise CrawlerError("HTTP session not initialized, use async with context")
            
        retry_count = 0
        while retry_count <= self.retry_count:
            try:
                async with self._session.get(url) as response:
                    if response.status >= 400:
                        raise RequestError(
                            f"HTTP error: {response.status}",
                            status_code=response.status,
                            url=url
                        )
                    
                    # Get content type from headers
                    content_type = response.headers.get('Content-Type', '')
                    
                    # Parse different content types
                    if 'application/json' in content_type:
                        data = await response.json()
                        content = str(data)
                    elif 'text/' in content_type or 'application/xml' in content_type:
                        content = await response.text()
                    else:
                        # Binary content
                        content = await response.read()
                        content = f"Binary content ({len(content)} bytes)"
                    
                    # Extract links from HTML content
                    links = []
                    if 'text/html' in content_type:
                        # Simple link extraction using string methods
                        # This is a basic implementation - could be enhanced with BeautifulSoup
                        for link in self._extract_links_from_html(content, url):
                            links.append(link)
                    
                    return {
                        "url": url,
                        "content": content,
                        "status": response.status,
                        "headers": dict(response.headers),
                        "links": links
                    }
                    
            except aiohttp.ClientError as e:
                self.logger.warning(f"HTTP request failed: {str(e)}, attempt {retry_count+1}/{self.retry_count+1}")
                retry_count += 1
                if retry_count > self.retry_count:
                    raise RequestError(f"HTTP request failed after {self.retry_count} retries: {str(e)}", url=url)
                await asyncio.sleep(retry_count)  # Exponential backoff
                
    def _extract_links_from_html(self, html_content: str, base_url: str) -> List[str]:
        """Extract links from HTML content.
        
        Args:
            html_content: HTML content to extract links from
            base_url: Base URL to resolve relative links
            
        Returns:
            List of extracted and normalized links
        """
        links = []
        
        # Basic link extraction using string methods
        # Find all href attributes
        parts = html_content.split('href="')
        for i in range(1, len(parts)):
            link = parts[i].split('"')[0]
            if link and not link.startswith(('javascript:', 'mailto:', 'tel:')):
                # Resolve relative URLs
                absolute_url = urljoin(base_url, link)
                links.append(absolute_url)
                
        return links
        
    async def crawl(
        self,
        url: str,
        depth: int = 0,
        follow_links: bool = False,
        max_pages: int = 1,
        **kwargs,
    ) -> CrawlResult:
        """Crawl a URL using HTTP requests.
        
        Args:
            url: URL to crawl
            depth: Crawl depth (0 for single page)
            follow_links: Whether to follow links
            max_pages: Maximum number of pages to crawl
            **kwargs: Additional arguments (unused in HTTP crawler)
            
        Returns:
            CrawlResult object containing the crawl results
            
        Raises:
            CrawlerError: If the crawler is not initialized or an error occurs
        """
        if not self._session:
            raise CrawlerError("HTTP session not initialized, use async with context")
            
        try:
            # Log crawl operation
            self.logger.info(f"HTTP Crawling URL: {url} (depth={depth}, max_pages={max_pages})")
            
            # Single page fetch if depth is 0 or not following links
            if depth == 0 or not follow_links:
                result = await self.fetch_page(url)
                return CrawlResult(
                    pages=[result],
                    links=result.get("links", []),
                    stats={
                        "pages_crawled": 1,
                        "start_time": None,
                        "end_time": None,
                        "duration_seconds": 0,
                    }
                )
                
            # If following links, implement BFS crawl
            visited = set()
            queue = [(url, 0)]  # (url, depth)
            results = []
            
            while queue and len(results) < max_pages:
                current_url, current_depth = queue.pop(0)
                
                if current_url in visited:
                    continue
                    
                visited.add(current_url)
                
                try:
                    page_result = await self.fetch_page(current_url)
                    results.append(page_result)
                    
                    # If we haven't reached max depth, add links to queue
                    if current_depth < depth:
                        for link in page_result.get("links", []):
                            if link not in visited:
                                queue.append((link, current_depth + 1))
                                
                except Exception as e:
                    self.logger.error(f"Error fetching {current_url}: {str(e)}")
                    continue
            
            # Combine results
            all_links = []
            for result in results:
                all_links.extend(result.get("links", []))
                
            return CrawlResult(
                pages=results,
                links=all_links,
                stats={
                    "pages_crawled": len(results),
                    "start_time": None,
                    "end_time": None,
                    "duration_seconds": 0,
                }
            )
                
        except Exception as e:
            self.logger.error(f"Error during HTTP crawl: {str(e)}")
            raise RequestError(f"Error during HTTP crawl: {str(e)}", url=url) 