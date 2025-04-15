#!/usr/bin/env python
"""Example script comparing BFS and DFS crawling strategies side by side."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.crawlers import StrategyCrawler
from crawl4ai.strategies import BFSCrawlStrategy, DFSCrawlStrategy


async def crawl_with_strategy(strategy_name, strategy, url, max_pages=5, max_depth=2):
    """Crawl a website with the specified strategy and print results.
    
    Args:
        strategy_name: Name of the strategy for display
        strategy: Strategy instance
        url: URL to crawl
        max_pages: Maximum pages to crawl
        max_depth: Maximum depth to crawl
    """
    print(f"\n==== Crawling with {strategy_name} Strategy ====")
    
    async with StrategyCrawler(strategy=strategy) as crawler:
        # Start crawling
        start_time = asyncio.get_event_loop().time()
        result = await crawler.crawl_with_strategy(
            url,
            max_pages=max_pages,
            max_depth=max_depth,
            follow_links=True,
        )
        end_time = asyncio.get_event_loop().time()
        
        # Display results
        print(f"Pages crawled: {result.stats.pages_crawled}")
        print(f"Total time: {result.stats.total_time:.2f} seconds")
        print(f"First page title: {result.title}")
        
        # Show visited URLs in order (if available)
        if hasattr(strategy, 'visited_urls') and strategy.visited_urls:
            print("\nURLs visited (in order):")
            for i, url in enumerate(list(strategy.visited_urls)[:5]):
                print(f"  {i+1}. {url}")
            
            if len(strategy.visited_urls) > 5:
                print(f"  ... and {len(strategy.visited_urls) - 5} more URLs")
    
    return result


async def main():
    """Compare BFS and DFS crawling strategies side by side."""
    print("===== Comparing Crawling Strategies =====")
    print("This example demonstrates the difference between BFS and DFS crawling strategies.")
    
    # URL to crawl
    test_url = "https://quotes.toscrape.com"
    max_pages = 5
    max_depth = 2
    
    # Create strategies
    bfs_strategy = BFSCrawlStrategy(
        max_depth=max_depth,
        max_pages=max_pages,
        same_domain_only=True,
    )
    
    dfs_strategy = DFSCrawlStrategy(
        max_depth=max_depth,
        max_pages=max_pages,
        same_domain_only=True,
    )
    
    # Crawl with BFS strategy
    await crawl_with_strategy("Breadth-First Search", bfs_strategy, test_url, max_pages, max_depth)
    
    # Crawl with DFS strategy
    await crawl_with_strategy("Depth-First Search", dfs_strategy, test_url, max_pages, max_depth)
    
    # Explain the difference
    print("\n===== Strategy Comparison =====")
    print("BFS (Breadth-First Search):")
    print("  - Explores all URLs at the current depth before moving to the next depth")
    print("  - Good for thorough exploration of a website level by level")
    print("  - Useful for collecting a broad overview of site content")
    print("\nDFS (Depth-First Search):")
    print("  - Follows a single path as deep as possible before backtracking")
    print("  - Good for finding deep content quickly")
    print("  - Useful for exploring hierarchical structures")
    print("\nChoose the strategy that best fits your crawling needs!")


if __name__ == "__main__":
    asyncio.run(main()) 