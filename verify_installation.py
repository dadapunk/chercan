#!/usr/bin/env python
"""Verification script to test Crawl4AI installation."""

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    """Run a simple crawl to verify installation."""
    print("Testing Crawl4AI installation...")
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.example.com",
        )
        print("Crawl completed successfully!")
        print("\nContent preview (first 300 chars):")
        print("-" * 50)
        print(result.markdown[:300])
        print("-" * 50)
        print("\nCrawl statistics:")
        print(f"  Pages crawled: {result.stats.pages_crawled}")
        print(f"  Total time: {result.stats.total_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
