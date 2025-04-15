"""Playwright browser-based crawler implementation.

This module provides a specialized crawler that uses Playwright for browser
automation to handle JavaScript-heavy websites and complex interactions.
"""
from typing import Dict, List, Optional, Any, Union, Literal
import asyncio
from pathlib import Path
import json
import logging

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CrawlResult
from crawl4ai.core.crawler import BaseCrawler
from crawl4ai.core.exceptions import CrawlerError, BrowserError


class PlaywrightCrawler(BaseCrawler):
    """Specialized crawler that uses Playwright for browser automation.
    
    This crawler extends BaseCrawler with additional Playwright-specific features
    for handling JavaScript-heavy websites and complex interactions.
    """
    
    def __init__(
        self,
        browser_name: Literal["chromium", "firefox", "webkit"] = "chromium",
        headless: bool = True,
        slow_mo: int = 0,
        viewport_width: int = 1280,
        viewport_height: int = 720,
        wait_until: Literal["load", "domcontentloaded", "networkidle"] = "networkidle",
        ignore_https_errors: bool = False,
        java_script_enabled: bool = True,
        **kwargs,
    ):
        """Initialize the Playwright crawler.
        
        Args:
            browser_name: Browser to use (chromium, firefox, or webkit)
            headless: Whether to run browser in headless mode
            slow_mo: Slow down browser actions by the specified amount of milliseconds
            viewport_width: Viewport width in pixels
            viewport_height: Viewport height in pixels
            wait_until: When to consider navigation succeeded
            ignore_https_errors: Whether to ignore HTTPS errors
            java_script_enabled: Whether JavaScript is enabled
            **kwargs: Additional arguments to pass to BaseCrawler.__init__()
        """
        # Set up Playwright-specific browser configuration
        browser_config = {
            "browser_name": browser_name,
            "headless": headless,
            "slow_mo": slow_mo,
            "viewport_width": viewport_width,
            "viewport_height": viewport_height,
            "wait_until": wait_until,
            "ignore_https_errors": ignore_https_errors,
            "java_script_enabled": java_script_enabled,
        }
        
        # Initialize base crawler with Playwright browser config
        super().__init__(browser_config=browser_config, **kwargs)
        
        # Set up additional attributes
        self.browser_name = browser_name
        self.headless = headless
        self.logger = logging.getLogger("crawl4ai.crawlers.playwright")
    
    async def take_screenshot(self, url: str, output_path: Union[str, Path], **kwargs) -> Path:
        """Take a screenshot of a webpage.
        
        Args:
            url: URL to capture
            output_path: Path to save the screenshot
            **kwargs: Additional arguments to pass to crawler.arun()
            
        Returns:
            Path to the saved screenshot
            
        Raises:
            CrawlerError: If the crawler is not initialized
            BrowserError: If the screenshot cannot be taken
        """
        if not self._crawler:
            raise CrawlerError("Crawler not initialized, use async with context")
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Crawl the page
            self.logger.info(f"Taking screenshot of {url}")
            result = await self.get_page(url, **kwargs)
            
            # Access the page and take a screenshot
            page = getattr(result, "_page", None)
            if not page:
                raise BrowserError("Unable to access browser page from crawl result")
            
            # Take a screenshot
            await page.screenshot(path=str(output_path))
            self.logger.info(f"Screenshot saved to {output_path}")
            
            return output_path
        except Exception as e:
            self.logger.error(f"Error taking screenshot of {url}: {str(e)}")
            raise BrowserError(f"Error taking screenshot: {str(e)}")
    
    async def scroll_to_bottom(self, url: str, scroll_delay: float = 1.0, **kwargs) -> CrawlResult:
        """Scroll to the bottom of a page to trigger lazy loading content.
        
        Args:
            url: URL to scroll
            scroll_delay: Delay between scrolls in seconds
            **kwargs: Additional arguments to pass to crawler.arun()
            
        Returns:
            CrawlResult after scrolling
            
        Raises:
            CrawlerError: If the crawler is not initialized
            BrowserError: If the scrolling cannot be performed
        """
        if not self._crawler:
            raise CrawlerError("Crawler not initialized, use async with context")
        
        try:
            # Crawl the page
            self.logger.info(f"Scrolling to bottom of {url}")
            result = await self.get_page(url, **kwargs)
            
            # Access the page to perform scrolling
            page = getattr(result, "_page", None)
            if not page:
                raise BrowserError("Unable to access browser page from crawl result")
            
            # Scroll to the bottom
            await page.evaluate("""
                async () => {
                    await new Promise((resolve) => {
                        let totalHeight = 0;
                        const distance = 100;
                        const scrollDelay = $SCROLL_DELAY;
                        
                        const timer = setInterval(() => {
                            const scrollHeight = document.body.scrollHeight;
                            window.scrollBy(0, distance);
                            totalHeight += distance;
                            
                            if (totalHeight >= scrollHeight) {
                                clearInterval(timer);
                                resolve();
                            }
                        }, scrollDelay);
                    });
                }
            """.replace("$SCROLL_DELAY", str(int(scroll_delay * 1000))))
            
            self.logger.info(f"Scrolled to bottom of {url}")
            
            # Return the updated result (with potentially more content)
            return result
        except Exception as e:
            self.logger.error(f"Error scrolling {url}: {str(e)}")
            raise BrowserError(f"Error scrolling: {str(e)}")
    
    async def execute_javascript(self, url: str, script: str, **kwargs) -> Any:
        """Execute JavaScript on a webpage.
        
        Args:
            url: URL to execute script on
            script: JavaScript code to execute
            **kwargs: Additional arguments to pass to crawler.arun()
            
        Returns:
            Result of the JavaScript execution
            
        Raises:
            CrawlerError: If the crawler is not initialized
            BrowserError: If the script cannot be executed
        """
        if not self._crawler:
            raise CrawlerError("Crawler not initialized, use async with context")
        
        try:
            # Crawl the page
            self.logger.info(f"Executing JavaScript on {url}")
            result = await self.get_page(url, **kwargs)
            
            # Access the page to execute JavaScript
            page = getattr(result, "_page", None)
            if not page:
                raise BrowserError("Unable to access browser page from crawl result")
            
            # Execute the script
            js_result = await page.evaluate(script)
            self.logger.info(f"JavaScript executed on {url}")
            
            return js_result
        except Exception as e:
            self.logger.error(f"Error executing JavaScript on {url}: {str(e)}")
            raise BrowserError(f"Error executing JavaScript: {str(e)}")
    
    async def fill_form(
        self,
        url: str,
        form_data: Dict[str, str],
        submit_selector: Optional[str] = None,
        wait_for_navigation: bool = True,
        **kwargs,
    ) -> CrawlResult:
        """Fill and submit a form on a webpage.
        
        Args:
            url: URL with the form
            form_data: Dictionary of {selector: value} pairs
            submit_selector: CSS selector for the submit button (optional)
            wait_for_navigation: Whether to wait for navigation after submit
            **kwargs: Additional arguments to pass to crawler.arun()
            
        Returns:
            CrawlResult after form submission
            
        Raises:
            CrawlerError: If the crawler is not initialized
            BrowserError: If the form cannot be filled or submitted
        """
        if not self._crawler:
            raise CrawlerError("Crawler not initialized, use async with context")
        
        try:
            # Crawl the page
            self.logger.info(f"Filling form on {url}")
            result = await self.get_page(url, **kwargs)
            
            # Access the page to fill the form
            page = getattr(result, "_page", None)
            if not page:
                raise BrowserError("Unable to access browser page from crawl result")
            
            # Fill form fields
            for selector, value in form_data.items():
                await page.fill(selector, value)
                self.logger.debug(f"Filled {selector} with {value}")
            
            # Submit the form
            if submit_selector:
                if wait_for_navigation:
                    # Wait for navigation after clicking
                    async with page.expect_navigation():
                        await page.click(submit_selector)
                else:
                    # Just click without waiting
                    await page.click(submit_selector)
                
                self.logger.info(f"Form submitted on {url}")
                
                # Get the updated result after submission
                # There are various ways to get the new result; this is a simplified approach
                # that might need adjustments based on Crawl4AI's internal implementation
                return await self.get_page(page.url, **kwargs)
            
            return result
        except Exception as e:
            self.logger.error(f"Error filling form on {url}: {str(e)}")
            raise BrowserError(f"Error filling form: {str(e)}")
    
    def set_browser(
        self,
        browser_name: Literal["chromium", "firefox", "webkit"],
        **browser_options,
    ) -> None:
        """Change the browser used by the crawler.
        
        Args:
            browser_name: Browser to use (chromium, firefox, or webkit)
            **browser_options: Additional browser configuration options
        """
        # Update browser configuration
        self.update_browser_config(browser_name=browser_name, **browser_options)
        self.browser_name = browser_name
        self.logger.info(f"Browser set to {browser_name}")
        
        # Note: The actual browser change will take effect on the next crawl
        # as the browser is initialized in __aenter__ 