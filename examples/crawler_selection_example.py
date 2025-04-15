#!/usr/bin/env python
"""
Example demonstrating the crawler type selection mechanism.

This example shows how to use the CrawlerFactory to create different types of crawlers
based on the specific requirements of the crawling task.
"""

import asyncio
import sys
import logging
from pathlib import Path
from urllib.parse import urlparse

# Add the parent directory to the path so we can import the crawl4ai package
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl4ai.crawlers import CrawlerFactory, CrawlerType
from crawl4ai.utils.logger import setup_logger


async def html_only_crawl():
    """Demonstrate crawling a static HTML website using the HTTP crawler."""
    logger = logging.getLogger(__name__)
    logger.info("Starting HTML-only crawl example...")
    
    # Create an HTTP crawler using the factory
    crawler = CrawlerFactory.create(
        CrawlerType.HTTP,
        user_agent="Crawl4AI/0.5.0 Crawler Selection Example",
        timeout=30,
        retry_count=3
    )
    
    url = "https://example.com"
    logger.info(f"Crawling static HTML site: {url}")
    
    async with crawler:
        # Fetch a single page
        page = await crawler.get_page(url)
        
        logger.info(f"Page title: {page.pages[0].get('title', 'No title')}")
        logger.info(f"Content length: {len(page.pages[0].get('content', ''))}")
        logger.info(f"Found {len(page.links)} links")


async def javascript_site_crawl():
    """Demonstrate crawling a JavaScript-heavy website using the Playwright crawler."""
    logger = logging.getLogger(__name__)
    logger.info("Starting JavaScript-heavy site crawl example...")
    
    # Create a browser-based crawler using the factory
    crawler = CrawlerFactory.create(
        CrawlerType.BROWSER,
        browser_name="chromium",
        headless=True,
        slow_mo=100,
        viewport_width=1280,
        viewport_height=800
    )
    
    # A site that requires JavaScript
    url = "https://www.airbnb.com"
    logger.info(f"Crawling JavaScript-heavy site: {url}")
    
    async with crawler:
        # Fetch a single page
        page = await crawler.get_page(url)
        
        # The page should be fully rendered with JavaScript
        logger.info(f"Page title: {page.title}")
        logger.info(f"Content length: {len(page.markdown)}")
        logger.info(f"Found {len(page.links)} links after JS rendering")


async def strategy_based_crawl():
    """Demonstrate crawling with a specific strategy using the StrategyCrawler."""
    logger = logging.getLogger(__name__)
    logger.info("Starting strategy-based crawl example...")
    
    # Create a strategy crawler using the factory
    crawler = CrawlerFactory.create(
        CrawlerType.STRATEGY,
        strategy="bfs",  # Breadth-first search strategy
        strategy_options={"same_domain_only": True},
        user_agent="Crawl4AI/0.5.0 Strategy Crawler Example"
    )
    
    url = "https://quotes.toscrape.com"
    logger.info(f"Crawling with BFS strategy: {url}")
    
    async with crawler:
        # Crawl with strategy
        result = await crawler.crawl_with_strategy(
            url,
            max_pages=5,
            max_depth=2,
            same_domain_only=True
        )
        
        logger.info(f"Pages crawled: {result.stats.pages_crawled}")
        logger.info(f"Links found: {len(result.links)}")


async def automatic_crawler_selection():
    """Demonstrate automatic crawler selection based on the website type."""
    logger = logging.getLogger(__name__)
    logger.info("Starting automatic crawler selection example...")
    
    # List of URLs to crawl
    urls = [
        "https://example.com",  # Static HTML
        "https://www.nytimes.com",  # Dynamic content with JavaScript
        "https://quotes.toscrape.com"  # Static site with multiple pages
    ]
    
    for url in urls:
        # Determine if JavaScript is likely needed
        domain = urlparse(url).netloc
        
        # Simple heuristic for sites that likely need JavaScript
        js_likely_needed = any(js_site in domain for js_site in [
            "nytimes.com", "twitter.com", "facebook.com", "instagram.com", 
            "airbnb.com", "react", "angular", "vue", "spa"
        ])
        
        # Get recommended crawler type
        crawler_type = CrawlerFactory.get_recommended_crawler(url, js_likely_needed)
        
        logger.info(f"URL: {url}")
        logger.info(f"JavaScript likely needed: {js_likely_needed}")
        logger.info(f"Recommended crawler type: {crawler_type.value}")
        
        # Create the crawler
        crawler = CrawlerFactory.create(crawler_type)
        
        # Crawl the URL
        async with crawler:
            logger.info(f"Crawling with {crawler_type.value} crawler: {url}")
            page = await crawler.get_page(url)
            
            if crawler_type == CrawlerType.BROWSER:
                logger.info(f"Page title: {page.title}")
                logger.info(f"Content length: {len(page.markdown)}")
            else:
                logger.info(f"Page title: {page.pages[0].get('title', 'No title')}")
                logger.info(f"Content length: {len(page.pages[0].get('content', ''))}")
                
            logger.info("-" * 50)


async def main():
    """Run the crawler selection examples."""
    # Set up logging
    setup_logger(level=logging.INFO)
    
    print("\n1. HTML-Only Crawl Example")
    print("-" * 50)
    await html_only_crawl()
    
    print("\n" + "=" * 60 + "\n")
    
    print("2. JavaScript-Heavy Site Crawl Example")
    print("-" * 50)
    await javascript_site_crawl()
    
    print("\n" + "=" * 60 + "\n")
    
    print("3. Strategy-Based Crawl Example")
    print("-" * 50)
    await strategy_based_crawl()
    
    print("\n" + "=" * 60 + "\n")
    
    print("4. Automatic Crawler Selection Example")
    print("-" * 50)
    await automatic_crawler_selection()


if __name__ == "__main__":
    asyncio.run(main()) 