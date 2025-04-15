#!/usr/bin/env python
"""
Example of using performance monitoring to compare crawler types.

This example demonstrates how to use the performance monitoring features to
compare the performance of different crawler types on the same URLs.
"""

import asyncio
import sys
import logging
import os
from pathlib import Path

# Add the parent directory to the path so we can import the crawl4ai package
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl4ai.crawlers import CrawlerFactory, CrawlerType
from crawl4ai.utils.logger import setup_logger


async def compare_crawler_types():
    """Compare performance of different crawler types on the same URLs."""
    logger = logging.getLogger(__name__)
    logger.info("Starting crawler performance comparison...")
    
    # Create output directory for performance reports
    output_dir = Path("performance_reports")
    output_dir.mkdir(exist_ok=True)
    
    # URLs to test with
    urls = [
        "https://example.com",  # Simple static site
        "https://quotes.toscrape.com",  # Slightly more complex site
        "https://news.ycombinator.com"  # More complex site with lots of links
    ]
    
    # Crawler types to compare
    crawler_types = [CrawlerType.HTTP, CrawlerType.BROWSER]
    
    # Crawl each URL with each crawler type
    for url in urls:
        logger.info(f"\nTesting URL: {url}")
        
        for crawler_type in crawler_types:
            logger.info(f"  Testing with {crawler_type.value} crawler...")
            
            # Create a crawler with performance monitoring
            crawler = CrawlerFactory.create_with_monitoring(
                crawler_type=crawler_type,
                monitor_output_dir=output_dir,
                auto_generate_report=False  # We'll generate a combined report at the end
            )
            
            # Crawl the URL
            try:
                async with crawler:
                    logger.info(f"    Crawling {url}...")
                    result = await crawler.get_page(url)
                    
                    # Log basic info
                    if crawler_type == CrawlerType.BROWSER:
                        logger.info(f"    Page title: {result.title}")
                        logger.info(f"    Links found: {len(result.links)}")
                    else:
                        if result.pages:
                            logger.info(f"    Page title: {result.pages[0].get('title', 'No title')}")
                            logger.info(f"    Links found: {len(result.links)}")
                        
            except Exception as e:
                logger.error(f"    Error crawling {url} with {crawler_type.value}: {str(e)}")
    
    # Generate performance comparison report
    logger.info("\nGenerating performance comparison report...")
    report = CrawlerFactory.generate_performance_report(
        output_file=output_dir / "performance_comparison.md"
    )
    
    # Print summary
    logger.info("\nPerformance Comparison Summary:")
    comparison = CrawlerFactory.get_performance_comparison()
    
    for crawler_type, metrics in comparison.items():
        logger.info(f"  {crawler_type}:")
        logger.info(f"    Success rate: {metrics['success_rate']:.2%}")
        logger.info(f"    Avg. throughput: {metrics['avg_throughput']:.2f} pages/s")
        logger.info(f"    Avg. response time: {metrics['avg_response_time']:.4f}s")
        logger.info(f"    Avg. memory usage: {metrics['avg_memory_usage']:.2f} MB")
    
    logger.info(f"\nDetailed report saved to {output_dir / 'performance_comparison.md'}")


async def compare_with_middleware():
    """Compare performance using the middleware directly."""
    logger = logging.getLogger(__name__)
    logger.info("Demonstrating direct middleware usage...")
    
    # Create output directory
    output_dir = Path("performance_reports/middleware_example")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create crawlers
    from crawl4ai.utils.performance_monitor import PerformanceMonitor
    from crawl4ai.middleware.performance_middleware import PerformanceMonitorMiddleware
    from crawl4ai.crawlers import HTTPCrawler, PlaywrightCrawler
    
    # Create shared monitor
    monitor = PerformanceMonitor(output_dir=output_dir)
    
    # Create HTTP crawler with middleware
    http_crawler = HTTPCrawler(
        user_agent="Crawl4AI/0.5.0 HTTP Performance Test",
        timeout=30
    )
    http_middleware = PerformanceMonitorMiddleware(
        monitor=monitor,
        crawler_type="http_direct",
        auto_generate_report=False
    )
    http_crawler.add_middleware(http_middleware)
    
    # Create browser crawler with middleware
    browser_crawler = PlaywrightCrawler(
        browser_name="chromium",
        headless=True,
        user_agent="Crawl4AI/0.5.0 Browser Performance Test"
    )
    browser_middleware = PerformanceMonitorMiddleware(
        monitor=monitor,
        crawler_type="browser_direct",
        auto_generate_report=False
    )
    browser_crawler.add_middleware(browser_middleware)
    
    # URL to test
    url = "https://quotes.toscrape.com"
    
    # Crawl with HTTP crawler
    logger.info(f"Crawling {url} with HTTP crawler...")
    async with http_crawler:
        result = await http_crawler.get_page(url)
        logger.info(f"  Found {len(result.links)} links")
    
    # End monitoring for HTTP crawler
    http_middleware.end_monitoring()
    
    # Crawl with browser crawler
    logger.info(f"Crawling {url} with browser crawler...")
    async with browser_crawler:
        result = await browser_crawler.get_page(url)
        logger.info(f"  Found {len(result.links)} links")
    
    # End monitoring for browser crawler
    browser_middleware.end_monitoring()
    
    # Generate report
    report = monitor.generate_report(output_dir / "direct_middleware_report.md")
    logger.info(f"Report saved to {output_dir / 'direct_middleware_report.md'}")


async def main():
    """Run the performance monitoring examples."""
    # Set up logging
    setup_logger(level=logging.INFO)
    
    print("\n1. Crawler Type Performance Comparison")
    print("-" * 50)
    await compare_crawler_types()
    
    print("\n" + "=" * 60 + "\n")
    
    print("2. Direct Middleware Usage Example")
    print("-" * 50)
    await compare_with_middleware()


if __name__ == "__main__":
    asyncio.run(main()) 