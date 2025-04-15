#!/usr/bin/env python
"""
Example of using the HTTP-only crawler to scrape web pages.

This example demonstrates how to use the HTTPCrawler class to crawl websites
without the need for a browser engine, which is more lightweight and faster
for basic web scraping tasks.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the crawl4ai package
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl4ai.crawlers import HTTPCrawler
from crawl4ai.utils.logger import setup_logger


async def basic_crawl_example():
    """Demonstrate a basic crawl using the HTTPCrawler."""
    # Set up logging
    setup_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Define a URL to crawl
    url = "https://example.com"
    
    logger.info(f"Starting basic crawl of {url}...")
    
    # Create and use the HTTPCrawler
    async with HTTPCrawler(
        user_agent="Crawl4AI/0.5.0 HTTPCrawler Example",
        timeout=30,
        retry_count=3
    ) as crawler:
        # Fetch a single page
        page = await crawler.fetch_page(url)
        
        logger.info(f"Page title: {page.title}")
        logger.info(f"Found {len(page.links)} links on the page")
        
        # Print the first few links
        for i, link in enumerate(page.links[:5]):
            logger.info(f"Link {i+1}: {link}")


async def depth_crawl_example():
    """Demonstrate crawling with depth using the HTTPCrawler."""
    # Set up logging
    setup_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Define a URL to crawl
    url = "https://quotes.toscrape.com"
    
    logger.info(f"Starting depth crawl of {url}...")
    
    # Create and use the HTTPCrawler
    async with HTTPCrawler() as crawler:
        # Crawl with depth=2 (homepage and one level deep)
        pages = await crawler.crawl(
            url, 
            depth=2,
            follow_links=True,
            max_pages=10  # Limit to 10 pages for the example
        )
        
        logger.info(f"Crawled {len(pages)} pages:")
        
        # Print info about each crawled page
        for page_url, page in pages.items():
            logger.info(f"Page: {page_url}")
            logger.info(f"  Title: {page.title}")
            logger.info(f"  Links: {len(page.links)}")
            
            # Extract some content - for this example, we'll look for quote text
            if "quotes.toscrape.com" in page_url:
                quotes = page.extract_elements(".quote .text")
                if quotes:
                    logger.info(f"  Found {len(quotes)} quotes")
                    # Print first quote
                    if quotes:
                        logger.info(f"  First quote: {quotes[0]}")


async def custom_extraction_example():
    """Demonstrate custom data extraction using the HTTPCrawler."""
    # Set up logging
    setup_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Define a URL to crawl
    url = "https://news.ycombinator.com"
    
    logger.info(f"Starting custom extraction from {url}...")
    
    # Create and use the HTTPCrawler
    async with HTTPCrawler() as crawler:
        # Fetch the page
        page = await crawler.fetch_page(url)
        
        # Extract story titles and links
        story_elements = page.extract_elements(".titleline")
        
        logger.info(f"Found {len(story_elements)} stories")
        
        # Process the first 5 stories
        for i, element in enumerate(story_elements[:5]):
            # Extract the story title and URL (assumes the format is consistent)
            title = element.text.strip() if hasattr(element, 'text') else "No title"
            
            # Find the anchor tag and get its href
            link_element = page.soup.select_one(f".titleline:nth-of-type({i+1}) a")
            link = link_element.get('href') if link_element else "No link"
            
            logger.info(f"Story {i+1}: {title}")
            logger.info(f"  Link: {link}")


async def main():
    """Run the example."""
    print("1. Basic Crawl Example")
    await basic_crawl_example()
    print("\n" + "-" * 50 + "\n")
    
    print("2. Depth Crawl Example")
    await depth_crawl_example()
    print("\n" + "-" * 50 + "\n")
    
    print("3. Custom Extraction Example")
    await custom_extraction_example()


if __name__ == "__main__":
    asyncio.run(main()) 