#!/usr/bin/env python
"""Example script demonstrating the Best-First crawling strategy."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.crawlers import StrategyCrawler
from crawl4ai.strategies import BestFirstCrawlStrategy


async def main():
    """Demonstrate Best-First crawling strategy."""
    print("===== Best-First Crawling Strategy Example =====")
    
    # Create Best-First strategy with default settings
    best_first_strategy = BestFirstCrawlStrategy(
        max_depth=3,  # Crawl up to 3 levels deep
        max_pages=10,  # Crawl up to 10 pages
        same_domain_only=True,  # Only crawl URLs within the same domain
    )
    
    # Create strategy crawler with Best-First strategy
    async with StrategyCrawler(strategy=best_first_strategy) as crawler:
        print("\n[1] Crawling with Best-First strategy (default scoring):")
        print("This will prioritize URLs based on a heuristic scoring function,")
        print("exploring the most valuable pages first based on URL patterns.")
        
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
        
        # Print the URLs and their scores
        if hasattr(best_first_strategy, 'url_scores') and best_first_strategy.url_scores:
            print("\nURL scores (sorted by score, highest first):")
            # Get all URLs and scores, excluding the start URL (which has inf score)
            scores = [(url, score) for url, score in best_first_strategy.url_scores.items() 
                      if score != float('inf')]
            # Sort by score (highest first)
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            for i, (url, score) in enumerate(sorted_scores[:5]):
                print(f"  {i+1}. {url} (score: {score:.2f})")
            
            if len(sorted_scores) > 5:
                print(f"  ... and {len(sorted_scores) - 5} more URLs")
    
    # Custom scoring function example
    print("\n\n===== Custom Scoring Function Example =====")
    
    # Define custom keyword weights focused on products and categories
    product_weights = {
        "product": 2.0,  # Higher weight for products
        "category": 1.5,
        "tag": 1.2,
        "author": 0.8,
        "about": 0.5,
    }
    
    # Create Best-First strategy with custom weights
    custom_strategy = BestFirstCrawlStrategy(
        max_depth=3,
        max_pages=10,
        same_domain_only=True,
        keyword_weights=product_weights,  # Use our custom weights
    )
    
    # Create strategy crawler with custom Best-First strategy
    async with StrategyCrawler(strategy=custom_strategy) as crawler:
        print("\n[2] Crawling with Best-First strategy (custom scoring):")
        print("This version uses custom keyword weights that prioritize")
        print("product and category pages over other content.")
        
        result = await crawler.crawl_with_strategy(
            "https://books.toscrape.com",  # Different example site with products
            max_pages=5,
            max_depth=2,
            follow_links=True,
        )
        
        # Display results
        print(f"\nCrawl completed!")
        print(f"Title of first page: {result.title}")
        print(f"Pages crawled: {result.stats.pages_crawled}")
        print(f"Total time: {result.stats.total_time:.2f} seconds")
        
        # Print the URLs and their scores
        if hasattr(custom_strategy, 'url_scores') and custom_strategy.url_scores:
            print("\nURL scores with custom weights (sorted by score, highest first):")
            # Get all URLs and scores, excluding the start URL (which has inf score)
            scores = [(url, score) for url, score in custom_strategy.url_scores.items() 
                      if score != float('inf')]
            # Sort by score (highest first)
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            for i, (url, score) in enumerate(sorted_scores[:5]):
                print(f"  {i+1}. {url} (score: {score:.2f})")


if __name__ == "__main__":
    asyncio.run(main()) 