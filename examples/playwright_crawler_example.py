#!/usr/bin/env python
"""Example script demonstrating the Playwright browser-based crawler."""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.crawlers import PlaywrightCrawler


async def main():
    """Demonstrate Playwright browser-based crawler capabilities."""
    print("===== Playwright Browser-Based Crawler Example =====")
    
    # Create output directory for screenshots if it doesn't exist
    screenshots_dir = Path("examples/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a Playwright crawler with a visible browser window (for demonstration)
    async with PlaywrightCrawler(
        browser_name="chromium",  # Use Chromium/Chrome
        headless=False,           # Show the browser window
        slow_mo=100,              # Slow down actions by 100ms for visibility
        viewport_width=1280,      # Set window size
        viewport_height=800,
    ) as crawler:
        print("\n[1] Basic page crawling:")
        print("Crawling a simple page with Playwright...")
        
        # Crawl a simple page
        result = await crawler.get_page("https://www.example.com")
        print(f"Title: {result.title}")
        print(f"Content preview: {result.markdown[:150]}...")
        
        # Take a screenshot
        screenshot_path = screenshots_dir / "example_com.png"
        await crawler.take_screenshot("https://www.example.com", screenshot_path)
        print(f"Screenshot saved to {screenshot_path.relative_to(Path.cwd())}")
        
        # Example with infinite scrolling (Twitter-like sites)
        print("\n\n[2] Handling lazy-loaded content with scrolling:")
        print("Crawling a page with lazy-loaded content and scrolling to the bottom...")
        
        # Quotes to Scrape has pagination, not infinite scroll,
        # but we'll use it as an example
        scroll_result = await crawler.scroll_to_bottom(
            "https://quotes.toscrape.com",
            scroll_delay=0.5  # 500ms between scrolls
        )
        print(f"Title after scrolling: {scroll_result.title}")
        print(f"Content length after scrolling: {len(scroll_result.markdown)} characters")
        
        # Take a screenshot after scrolling
        screenshot_path = screenshots_dir / "quotes_after_scroll.png"
        await crawler.take_screenshot("https://quotes.toscrape.com", screenshot_path)
        print(f"Screenshot saved to {screenshot_path.relative_to(Path.cwd())}")
        
        # Example with form submission
        print("\n\n[3] Form submission example:")
        print("Filling and submitting a login form...")
        
        # Login form on Quotes to Scrape
        form_result = await crawler.fill_form(
            "https://quotes.toscrape.com/login",
            form_data={
                'input[name="username"]': "testuser",
                'input[name="password"]': "testpassword"
            },
            submit_selector='input[type="submit"]',
            wait_for_navigation=True
        )
        print(f"Page title after form submission: {form_result.title}")
        
        # Take a screenshot after form submission
        screenshot_path = screenshots_dir / "after_login_attempt.png"
        await crawler.take_screenshot(form_result._crawler.current_url, screenshot_path)
        print(f"Screenshot saved to {screenshot_path.relative_to(Path.cwd())}")
        
        # Execute JavaScript example
        print("\n\n[4] JavaScript execution example:")
        print("Executing JavaScript to extract page information...")
        
        # Simple JavaScript to get page metrics
        js_result = await crawler.execute_javascript(
            "https://www.example.com",
            """
            () => {
                return {
                    title: document.title,
                    url: window.location.href,
                    links: Array.from(document.querySelectorAll('a')).length,
                    paragraphs: Array.from(document.querySelectorAll('p')).length,
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight,
                    userAgent: navigator.userAgent
                };
            }
            """
        )
        
        print("JavaScript execution results:")
        for key, value in js_result.items():
            print(f"  {key}: {value}")
        
        # Try a different browser
        print("\n\n[5] Using different browsers:")
        print("Switching to Firefox browser...")
        
        # Switch to Firefox
        crawler.set_browser("firefox")
        
        # Crawl the same page with Firefox
        firefox_result = await crawler.get_page("https://www.example.com")
        print(f"Firefox: Title of page: {firefox_result.title}")
        
        # Take a screenshot with Firefox
        screenshot_path = screenshots_dir / "firefox_example.png"
        await crawler.take_screenshot("https://www.example.com", screenshot_path)
        print(f"Firefox screenshot saved to {screenshot_path.relative_to(Path.cwd())}")


if __name__ == "__main__":
    asyncio.run(main()) 