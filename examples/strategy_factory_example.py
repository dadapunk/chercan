#!/usr/bin/env python
"""Example script demonstrating the strategy factory and selection mechanism."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.crawlers import StrategyCrawler
from crawl4ai.strategies import StrategyFactory


async def main():
    """Demonstrate strategy factory and selection mechanism."""
    print("===== Strategy Factory and Selection Example =====")
    
    # Get list of available strategies
    available_strategies = StrategyFactory.get_available_strategies()
    
    print("Available crawling strategies:")
    for strategy in available_strategies:
        print(f"  - {strategy}")
    print()
    
    # Example 1: Using the factory to create a strategy directly
    print("Example 1: Using the factory to create strategies directly")
    
    # Create BFS strategy with the factory
    bfs_strategy = StrategyFactory.create_strategy('bfs', max_depth=2, max_pages=5)
    print(f"Created BFS strategy: {bfs_strategy.__class__.__name__}")
    
    # Create DFS strategy with the factory
    dfs_strategy = StrategyFactory.create_strategy('dfs', max_depth=3, max_pages=5)
    print(f"Created DFS strategy: {dfs_strategy.__class__.__name__}")
    
    # Create Best-First strategy with custom keyword weights
    best_first_strategy = StrategyFactory.create_strategy(
        'best_first',
        max_depth=2,
        max_pages=5,
        keyword_weights={"product": 2.0, "category": 1.5, "tag": 1.0}
    )
    print(f"Created Best-First strategy: {best_first_strategy.__class__.__name__}")
    print(f"  with custom keyword weights: {best_first_strategy.keyword_weights}")
    print()
    
    # Example 2: Using the strategy name with StrategyCrawler
    print("Example 2: Using strategy names with StrategyCrawler")
    
    # Create crawler with BFS strategy by name
    async with StrategyCrawler(strategy='bfs', strategy_options={'max_depth': 2}) as crawler:
        print("Created crawler with BFS strategy by name")
        
        # Crawl a page
        print("Crawling with BFS strategy...")
        result = await crawler.crawl_with_strategy(
            "https://quotes.toscrape.com",
            max_pages=3,
            follow_links=True,
        )
        print(f"Crawl completed: {result.stats.pages_crawled} pages crawled")
        
        # Change strategy to DFS
        print("\nChanging strategy to DFS...")
        crawler.set_strategy('dfs', max_depth=3)
        
        # Crawl a different page with the new strategy
        print("Crawling with DFS strategy...")
        result = await crawler.crawl_with_strategy(
            "https://books.toscrape.com",
            max_pages=3,
            follow_links=True,
        )
        print(f"Crawl completed: {result.stats.pages_crawled} pages crawled")
    
    # Example 3: Getting strategy options
    print("\nExample 3: Inspecting strategy options")
    
    # Get options for BFS strategy
    bfs_options = StrategyFactory.get_strategy_options('bfs')
    print("BFS strategy options:")
    for name, value in bfs_options.items():
        print(f"  - {name}: {value}")
    
    # Get options for Best-First strategy
    best_options = StrategyFactory.get_strategy_options('best_first')
    print("\nBest-First strategy options:")
    for name, value in best_options.items():
        if name != 'keyword_weights':  # Skip printing the whole dictionary
            print(f"  - {name}: {value}")
        else:
            print(f"  - {name}: (dictionary with {len(value)} keywords)")


if __name__ == "__main__":
    asyncio.run(main()) 