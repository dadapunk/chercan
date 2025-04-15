#!/usr/bin/env python
"""Example script demonstrating basic usage of the BaseCrawler class."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.core.crawler import BaseCrawler


async def main():
    """Run a simple crawl to demonstrate the BaseCrawler class."""
    print("Testing BaseCrawler implementation...")
    
    # Create and use BaseCrawler with async context manager
    async with BaseCrawler() as crawler:
        # Simple single page crawl
        print("\n[1] Simple single page crawl:")
        result = await crawler.get_page("https://www.example.com")
        print(f"Title: {result.title}")
        print(f"Content preview: {result.markdown[:150]}...")
        print(f"Pages crawled: {result.stats.pages_crawled}")
        print(f"Total time: {result.stats.total_time:.2f} seconds")
        
        # Crawler with custom configuration
        print("\n[2] Crawl with custom browser configuration:")
        crawler.update_browser_config(
            headless=False,  # Show browser window
            slow_mo=100,     # Slow down browser actions
        )
        custom_result = await crawler.get_page("https://www.python.org")
        print(f"Title: {custom_result.title}")
        print(f"Content preview: {custom_result.markdown[:150]}...")
        print(f"Pages crawled: {custom_result.stats.pages_crawled}")
        print(f"Total time: {custom_result.stats.total_time:.2f} seconds")
        
        # Multi-page crawl
        print("\n[3] Multi-page crawl following links:")
        multi_result = await crawler.crawl(
            "https://quotes.toscrape.com",
            depth=1,
            follow_links=True,
            max_pages=3,
        )
        print(f"Title of first page: {multi_result.title}")
        print(f"Pages crawled: {multi_result.stats.pages_crawled}")
        print(f"Links found: {len(multi_result.links)}")
        print(f"Total time: {multi_result.stats.total_time:.2f} seconds")
        
        # Print all page titles
        print("\nAll crawled pages:")
        for i, page in enumerate(multi_result.pages):
            print(f"Page {i+1}: {page.title} - {page.url}")


if __name__ == "__main__":
    asyncio.run(main()) 