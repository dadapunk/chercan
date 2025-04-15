#!/usr/bin/env python
"""Example script demonstrating configuration handling for Crawl4AI."""

import os
import json
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.config import (
    BrowserConfiguration,
    CrawlerConfiguration,
    load_browser_config,
    load_crawler_config,
)


def create_sample_config_files():
    """Create sample configuration files for the examples."""
    # Sample browser configuration
    browser_config = BrowserConfiguration(
        browser_name="firefox",
        headless=False,
        viewport_width=1920,
        viewport_height=1080,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    )
    
    # Save to file
    browser_config.to_json("browser_config.json")
    print(f"Sample browser configuration saved to browser_config.json")
    
    # Sample crawler configuration
    crawler_config = CrawlerConfiguration(
        follow_links=True,
        max_pages=5,
        max_depth=2,
        retry_count=5,
        same_domain_only=True,
        rate_limit=10,
    )
    
    # Save to file
    crawler_config.to_json("crawler_config.json")
    print(f"Sample crawler configuration saved to crawler_config.json")


def demonstrate_config_usage():
    """Demonstrate different ways to use the configuration classes."""
    print("\n[1] Loading browser configuration from file:")
    browser_config = load_browser_config(config_file="browser_config.json")
    print(f"  Browser: {browser_config.browser_name}")
    print(f"  Headless: {browser_config.headless}")
    print(f"  User Agent: {browser_config.user_agent}")
    
    print("\n[2] Loading crawler configuration with overrides:")
    crawler_config = load_crawler_config(
        config_file="crawler_config.json",
        max_pages=20,  # Override the value from file
        timeout=60,    # Override the default value
    )
    print(f"  Max Pages: {crawler_config.max_pages}")
    print(f"  Max Depth: {crawler_config.max_depth}")
    print(f"  Timeout: {crawler_config.timeout}")
    
    print("\n[3] Using environment variables:")
    # Set environment variables for testing
    os.environ["BROWSER_HEADLESS"] = "true"
    os.environ["BROWSER_TIMEOUT"] = "45"
    os.environ["CRAWLER_FOLLOW_LINKS"] = "true"
    
    # Load with environment variables
    browser_env_config = load_browser_config(env_vars=True)
    crawler_env_config = load_crawler_config(env_vars=True)
    
    print(f"  Browser Headless: {browser_env_config.headless}")
    print(f"  Browser Timeout: {browser_env_config.timeout}")
    print(f"  Crawler Follow Links: {crawler_env_config.follow_links}")
    
    # Clean up environment variables
    del os.environ["BROWSER_HEADLESS"]
    del os.environ["BROWSER_TIMEOUT"]
    del os.environ["CRAWLER_FOLLOW_LINKS"]


def main():
    """Run configuration examples."""
    print("Demonstrating Crawl4AI configuration handling...\n")
    
    # Create sample configuration files
    create_sample_config_files()
    
    # Demonstrate configuration usage
    demonstrate_config_usage()
    
    # Clean up sample files
    print("\nCleaning up sample files...")
    Path("browser_config.json").unlink(missing_ok=True)
    Path("crawler_config.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main() 