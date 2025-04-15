#!/usr/bin/env python
"""Example script demonstrating the DFS crawling strategy."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.crawlers import StrategyCrawler
from crawl4ai.strategies import DFSCrawlStrategy


async def main():
    """Demonstrate DFS crawling strategy."""
    print("===== DFS Crawling Strategy Example =====")
    
    # Create DFS strategy
    dfs_strategy = DFSCrawlStrategy(
        max_depth=3,  # Crawl up to 3 levels deep
        max_pages=10,  # Crawl up to 10 pages
        same_domain_only=True,  # Only crawl URLs within the same domain
    )
    
    # Create strategy crawler with DFS strategy
    async with StrategyCrawler(strategy=dfs_strategy) as crawler:
        print("\n[1] Crawling with DFS strategy:")
        print("This will explore each path as deeply as possible before backtracking")
        print("to explore alternative paths.")
        
        result = await crawler.crawl_with_strategy(
            "https://quotes.toscrape.com",
            max_pages=5,
            max_depth=3,
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
    
    # Compare BFS and DFS strategies (optional)
    print("\n\n===== Comparing BFS and DFS Strategies =====")
    print("Note: The key difference is in the order URLs are visited.")
    print("BFS visits all URLs at the current depth before moving to the next depth.")
    print("DFS follows a single path as deep as possible before backtracking.")
    print("This results in different crawling patterns, which can be useful for different scenarios.")


if __name__ == "__main__":
    asyncio.run(main()) 