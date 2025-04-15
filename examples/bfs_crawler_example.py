#!/usr/bin/env python
"""Example script demonstrating the BFS crawling strategy."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.crawlers import StrategyCrawler
from crawl4ai.strategies import BFSCrawlStrategy


async def main():
    """Demonstrate BFS crawling strategy."""
    print("===== BFS Crawling Strategy Example =====")
    
    # Create BFS strategy
    bfs_strategy = BFSCrawlStrategy(
        max_depth=2,  # Crawl up to 2 levels deep
        max_pages=10,  # Crawl up to 10 pages
        same_domain_only=True,  # Only crawl URLs within the same domain
    )
    
    # Create strategy crawler with BFS strategy
    async with StrategyCrawler(strategy=bfs_strategy) as crawler:
        print("\n[1] Crawling with BFS strategy:")
        print("This will explore all URLs at the current depth level")
        print("before moving to the next depth level.")
        
        result = await crawler.crawl_with_strategy(
            "https://quotes.toscrape.com",
            max_pages=5,
            max_depth=2,
            follow_links=True,
        )
        
        # Display results
        print(f"\nCrawl completed!")
        print(f"Title of first page: {result.title}")
        print(f"Pages crawled: {result.stats.pages_crawled}")
        print(f"Total time: {result.stats.total_time:.2f} seconds")
        
        # Print the first few links that were found
        if hasattr(result, 'links') and result.links:
            print("\nSome links found:")
            for i, link in enumerate(result.links[:5]):
                print(f"  {i+1}. {link}")


if __name__ == "__main__":
    asyncio.run(main()) 