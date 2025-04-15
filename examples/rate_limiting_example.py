#!/usr/bin/env python
"""
Example of implementing rate limiting with Crawl4AI.

This example demonstrates how to:
1. Use the built-in rate limiting features of Crawl4AI
2. Create a custom rate limiter for specific domains
3. Handle rate limiting errors
4. Implement backoff strategies
"""

import asyncio
import sys
import logging
import random
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the parent directory to the path so we can import the crawl4ai package
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl4ai.crawlers import HTTPCrawler
from crawl4ai.middleware import BaseMiddleware
from crawl4ai.utils.rate_limiter import RateLimiter
from crawl4ai.utils.logger import setup_logger
from crawl4ai.models import Request, Response


class DomainRateLimiter(BaseMiddleware):
    """
    Custom middleware for domain-specific rate limiting.
    This allows different rate limits for different domains.
    """
    
    def __init__(self, domain_limits: Dict[str, float] = None, default_rate: float = 1.0):
        """
        Initialize the domain rate limiter.
        
        Args:
            domain_limits: Dictionary mapping domains to requests per second
            default_rate: Default rate limit for domains not in domain_limits
        """
        self.domain_limits = domain_limits or {}
        self.default_rate = default_rate
        self.limiters = {}
        
        # Initialize limiters for each domain
        for domain, rate in self.domain_limits.items():
            self.limiters[domain] = RateLimiter(rate)
        
        # Default limiter for domains not explicitly configured
        self.default_limiter = RateLimiter(self.default_rate)
    
    async def before_request(self, request: Request) -> Request:
        """Apply rate limiting before each request."""
        from urllib.parse import urlparse
        
        # Extract domain from URL
        domain = urlparse(request.url).netloc
        
        # Get the appropriate limiter
        limiter = self.limiters.get(domain, self.default_limiter)
        
        # Wait for rate limit
        await limiter.acquire()
        
        return request


class ExponentialBackoffMiddleware(BaseMiddleware):
    """
    Middleware that implements exponential backoff on failures.
    Useful for handling rate limit errors (429) or server errors (5xx).
    """
    
    def __init__(self, max_retries: int = 3, initial_backoff: float = 1.0, max_backoff: float = 60.0):
        """
        Initialize the backoff middleware.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_backoff: Initial backoff time in seconds
            max_backoff: Maximum backoff time in seconds
        """
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.retry_counts = {}
    
    async def on_response(self, response: Response) -> Response:
        """Handle responses, implementing backoff for certain status codes."""
        # If we got a rate limit (429) or server error (5xx), apply backoff
        if response.status_code in [429] or (500 <= response.status_code < 600):
            # Get or initialize retry count
            retry_count = self.retry_counts.get(response.url, 0)
            
            if retry_count < self.max_retries:
                # Increment retry count
                retry_count += 1
                self.retry_counts[response.url] = retry_count
                
                # Calculate backoff time with jitter
                backoff = min(
                    self.max_backoff,
                    self.initial_backoff * (2 ** (retry_count - 1))
                )
                
                # Add some randomness to prevent thundering herd problem
                jitter = random.uniform(0.8, 1.2)
                backoff_with_jitter = backoff * jitter
                
                # Log the backoff
                logging.info(
                    f"Rate limit or server error ({response.status_code}) for {response.url}. "
                    f"Backing off for {backoff_with_jitter:.2f}s (retry {retry_count}/{self.max_retries})"
                )
                
                # Apply backoff
                await asyncio.sleep(backoff_with_jitter)
                
                # Flag for retry - this will be handled by the crawler
                response.retry = True
            else:
                logging.warning(
                    f"Max retries ({self.max_retries}) reached for {response.url}. "
                    f"Giving up after encountering status code {response.status_code}."
                )
        
        return response


async def basic_rate_limiting_example():
    """Demonstrate basic rate limiting with Crawl4AI."""
    logger = logging.getLogger(__name__)
    logger.info("Starting basic rate limiting example...")
    
    # Create crawler with a rate limit of 2 requests per second
    crawler = HTTPCrawler(rate_limit=2.0)
    
    # List of URLs to crawl
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
        "https://example.edu",
        "https://example.io"
    ]
    
    start_time = time.time()
    logger.info(f"Crawling {len(urls)} URLs with a rate limit of 2 requests per second...")
    
    async with crawler:
        # This will take at least 2.5 seconds due to the rate limit (5 URLs at 2 per second)
        results = await asyncio.gather(*[crawler.fetch_page(url) for url in urls])
        
        for url, page in zip(urls, results):
            if page:
                logger.info(f"Successfully crawled: {url} (Status: {page.status_code})")
            else:
                logger.warning(f"Failed to crawl: {url}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Crawling completed in {elapsed_time:.2f} seconds")
    
    # Verify rate limiting worked
    if elapsed_time < 2.5:
        logger.warning("Rate limiting might not be working as expected!")
    else:
        logger.info("Rate limiting worked as expected")


async def domain_specific_rate_limiting_example():
    """Demonstrate domain-specific rate limiting with a custom middleware."""
    logger = logging.getLogger(__name__)
    logger.info("Starting domain-specific rate limiting example...")
    
    # Configure domain-specific rate limits (requests per second)
    domain_limits = {
        "example.com": 1.0,      # 1 request per second
        "example.org": 0.5,      # 1 request every 2 seconds
        "httpbin.org": 2.0       # 2 requests per second
    }
    
    # Create a crawler with our custom middleware
    crawler = HTTPCrawler()
    crawler.add_middleware(DomainRateLimiter(domain_limits, default_rate=1.0))
    
    # List of URLs for different domains
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.org/page1",
        "https://example.org/page2",
        "https://httpbin.org/get?param1=value1",
        "https://httpbin.org/get?param2=value2",
        "https://example.net/page1"  # This will use the default rate limit
    ]
    
    start_time = time.time()
    logger.info(f"Crawling {len(urls)} URLs with domain-specific rate limits...")
    
    async with crawler:
        # The URLs will be crawled respecting the domain-specific rate limits
        results = []
        for url in urls:
            logger.info(f"Requesting: {url}")
            page = await crawler.fetch_page(url)
            if page:
                logger.info(f"Successfully crawled: {url} (Status: {page.status_code})")
                results.append(page)
            else:
                logger.warning(f"Failed to crawl: {url}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Crawling completed in {elapsed_time:.2f} seconds")
    logger.info(f"Successfully crawled {len(results)} out of {len(urls)} URLs")


async def backoff_strategy_example():
    """Demonstrate backoff strategy for handling rate limits and server errors."""
    logger = logging.getLogger(__name__)
    logger.info("Starting backoff strategy example...")
    
    # Create a crawler with our exponential backoff middleware
    crawler = HTTPCrawler()
    crawler.add_middleware(ExponentialBackoffMiddleware(max_retries=3, initial_backoff=1.0))
    
    # URLs that might trigger rate limits or errors
    urls = [
        "https://httpbin.org/status/429",  # Will return 429 Too Many Requests
        "https://httpbin.org/status/500",  # Will return 500 Internal Server Error
        "https://httpbin.org/status/503",  # Will return 503 Service Unavailable
        "https://httpbin.org/status/200"   # Will return 200 OK
    ]
    
    logger.info(f"Crawling {len(urls)} URLs with backoff strategy...")
    
    async with crawler:
        for url in urls:
            logger.info(f"Requesting: {url}")
            page = await crawler.fetch_page(url)
            
            if page:
                logger.info(
                    f"Final result for {url}: Status {page.status_code}"
                )
            else:
                logger.warning(f"Failed to crawl: {url} after retries")


async def main():
    """Run the rate limiting examples."""
    # Set up logging
    setup_logger(level=logging.INFO)
    
    print("1. Basic Rate Limiting Example")
    print("-" * 50)
    await basic_rate_limiting_example()
    
    print("\n" + "=" * 60 + "\n")
    
    print("2. Domain-Specific Rate Limiting Example")
    print("-" * 50)
    await domain_specific_rate_limiting_example()
    
    print("\n" + "=" * 60 + "\n")
    
    print("3. Backoff Strategy Example")
    print("-" * 50)
    await backoff_strategy_example()


if __name__ == "__main__":
    asyncio.run(main()) 