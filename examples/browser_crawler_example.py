#!/usr/bin/env python
"""
Example of using the browser-based crawler to scrape JavaScript-heavy websites.

This example demonstrates how to use the BrowserCrawler class to crawl websites
that require JavaScript rendering, such as single-page applications (SPAs),
dynamic content loading sites, or websites with client-side rendering.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the crawl4ai package
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl4ai.crawlers import BrowserCrawler
from crawl4ai.utils.logger import setup_logger


async def basic_browser_crawl():
    """Demonstrate a basic crawl using the BrowserCrawler for a JS-heavy site."""
    # Set up logging
    setup_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Define a URL to crawl - using a site known to have JS-rendered content
    url = "https://spa-demo.vercel.app/"  # Example SPA demo site
    
    logger.info(f"Starting basic browser crawl of {url}...")
    
    # Create and use the BrowserCrawler
    async with BrowserCrawler(
        headless=True,  # Run without visible browser window
        browser_args=["--disable-gpu", "--no-sandbox"],
        user_agent="Crawl4AI/0.5.0 BrowserCrawler Example",
        timeout=30
    ) as crawler:
        # Fetch a single page, waiting for JS to render
        page = await crawler.fetch_page(url, wait_for_selector=".content")
        
        logger.info(f"Page title: {page.title}")
        logger.info(f"Found {len(page.links)} links after JS rendering")
        
        # Print the first few links
        for i, link in enumerate(page.links[:5]):
            logger.info(f"Link {i+1}: {link}")
        
        # Get content that is only available after JS execution
        js_content = page.extract_elements(".js-content")
        if js_content:
            logger.info(f"Found {len(js_content)} JS-rendered elements")
            logger.info(f"First JS content: {js_content[0].text.strip() if hasattr(js_content[0], 'text') else None}")


async def interaction_example():
    """Demonstrate browser interaction capabilities of BrowserCrawler."""
    # Set up logging
    setup_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Define a URL to crawl - a site that requires interaction
    url = "https://quotes.toscrape.com/login"
    
    logger.info(f"Starting browser interaction example on {url}...")
    
    # Create and use the BrowserCrawler
    async with BrowserCrawler(headless=True) as crawler:
        # Fetch the page
        page = await crawler.fetch_page(url)
        
        logger.info(f"Initial page title: {page.title}")
        
        # Interact with the page using browser automation
        # Login form interaction
        await crawler.browser_page.type('input[name="username"]', 'testuser')
        await crawler.browser_page.type('input[name="password"]', 'password123')
        
        # Click the login button and wait for navigation
        logger.info("Submitting login form...")
        
        # Click and wait for navigation
        await asyncio.gather(
            crawler.browser_page.click('input[type="submit"]'),
            crawler.browser_page.waitForNavigation()
        )
        
        # Get the new page content after interaction
        new_page = await crawler.get_current_page()
        logger.info(f"Page title after interaction: {new_page.title}")
        
        # Check if login was successful by looking for specific elements
        welcome_msg = new_page.extract_elements(".header-box")
        if welcome_msg:
            logger.info(f"Login result: {welcome_msg[0].text.strip() if hasattr(welcome_msg[0], 'text') else 'No welcome message'}")
        else:
            logger.info("Login may have failed - no welcome message found")


async def infinite_scroll_example():
    """Demonstrate handling of infinite scroll pages with BrowserCrawler."""
    # Set up logging
    setup_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Define a URL to an infinite scrolling page
    url = "https://infinite-scroll.com/demo/full-page/"
    
    logger.info(f"Starting infinite scroll handling on {url}...")
    
    # Create and use the BrowserCrawler
    async with BrowserCrawler(headless=True) as crawler:
        # Fetch the initial page
        page = await crawler.fetch_page(url)
        
        logger.info(f"Initial items: {len(page.extract_elements('.post'))}")
        
        # Scroll down multiple times to load more content
        for i in range(3):
            logger.info(f"Scrolling to load more content (scroll {i+1})...")
            
            # Execute scroll down JavaScript
            await crawler.browser_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait for new content to load
            await asyncio.sleep(2)  # Simple wait, could be improved with waitForSelector
            
            # Get updated page content
            page = await crawler.get_current_page()
            items = page.extract_elements('.post')
            
            logger.info(f"Items after scroll {i+1}: {len(items)}")
        
        # Get the final content
        final_page = await crawler.get_current_page()
        all_items = final_page.extract_elements('.post')
        
        logger.info(f"Total items loaded after scrolling: {len(all_items)}")
        
        # Extract some data from the items
        if all_items:
            sample_items = all_items[:3]  # First 3 items
            for i, item in enumerate(sample_items):
                title_elem = item.select_one('.entry-title')
                title = title_elem.text.strip() if title_elem and hasattr(title_elem, 'text') else "No title"
                logger.info(f"Item {i+1} title: {title}")


async def main():
    """Run the example."""
    print("1. Basic Browser Crawl (JavaScript Rendering)")
    await basic_browser_crawl()
    print("\n" + "-" * 50 + "\n")
    
    print("2. Browser Interaction Example")
    await interaction_example()
    print("\n" + "-" * 50 + "\n")
    
    print("3. Infinite Scroll Handling")
    await infinite_scroll_example()


if __name__ == "__main__":
    asyncio.run(main()) 