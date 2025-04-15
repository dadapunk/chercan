#!/usr/bin/env python
"""
Example of using custom data extraction and processing with Crawl4AI.

This example demonstrates how to:
1. Create custom extractors to pull specific data from web pages
2. Process and transform extracted data using processors
3. Chain multiple processors together for complex data transformations
4. Save extracted data to different output formats
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the parent directory to the path so we can import the crawl4ai package
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl4ai.crawlers import HTTPCrawler
from crawl4ai.extractors import BaseExtractor
from crawl4ai.processors import BaseProcessor
from crawl4ai.utils.logger import setup_logger
from crawl4ai.models import Page, CrawlResult


class ProductExtractor(BaseExtractor):
    """Custom extractor for e-commerce product data."""
    
    def extract(self, page: Page) -> Dict[str, Any]:
        """Extract product information from a page."""
        products = []
        
        # Find all product containers
        product_elements = page.extract_elements(".product")
        
        for elem in product_elements:
            title_elem = elem.select_one(".product-title")
            price_elem = elem.select_one(".product-price")
            image_elem = elem.select_one(".product-image")
            
            # Extract data with fallbacks
            product = {
                "title": title_elem.text.strip() if title_elem and hasattr(title_elem, "text") else "Unknown",
                "price": price_elem.text.strip() if price_elem and hasattr(price_elem, "text") else "N/A",
                "image_url": image_elem.get("src") if image_elem else None,
                "url": page.url,
                "extracted_at": datetime.now().isoformat()
            }
            
            products.append(product)
        
        return {"products": products, "page_title": page.title, "source_url": page.url}


class NewsArticleExtractor(BaseExtractor):
    """Custom extractor for news articles."""
    
    def extract(self, page: Page) -> Dict[str, Any]:
        """Extract news article information from a page."""
        # Extract article metadata
        title = page.extract_text("h1.article-title") or page.title
        
        # Extract author information
        author_elem = page.extract_elements(".author-name")
        author = author_elem[0].text.strip() if author_elem and hasattr(author_elem[0], "text") else "Unknown"
        
        # Extract publication date
        date_elem = page.extract_elements(".pub-date")
        pub_date = date_elem[0].text.strip() if date_elem and hasattr(date_elem[0], "text") else None
        
        # Extract article content
        content_elems = page.extract_elements(".article-content p")
        content = "\n\n".join([
            elem.text.strip() for elem in content_elems
            if hasattr(elem, "text") and elem.text.strip()
        ])
        
        # Extract image URLs
        image_elems = page.extract_elements(".article-content img")
        images = [img.get("src") for img in image_elems if img.get("src")]
        
        return {
            "title": title,
            "author": author,
            "published_date": pub_date,
            "content": content,
            "images": images,
            "url": page.url,
            "extracted_at": datetime.now().isoformat()
        }


class PriceNormalizer(BaseProcessor):
    """Process product prices to normalize format."""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize price formats in the data."""
        if "products" not in data:
            return data
        
        for product in data["products"]:
            if "price" in product:
                # Remove currency symbols and normalize
                price_text = product["price"]
                # Remove common currency symbols
                for symbol in ["$", "€", "£", "¥"]:
                    price_text = price_text.replace(symbol, "")
                
                # Remove whitespace
                price_text = price_text.strip()
                
                try:
                    # Convert to float if possible
                    product["price_value"] = float(price_text)
                    product["price_original"] = product["price"]
                    product["price_normalized"] = True
                except ValueError:
                    # If conversion fails, keep original and add normalized flag
                    product["price_value"] = None
                    product["price_original"] = product["price"]
                    product["price_normalized"] = False
        
        return data


class ContentCleaner(BaseProcessor):
    """Clean and normalize article content."""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean article content by removing extra whitespace and normalizing paragraphs."""
        if "content" in data:
            # Remove excessive newlines
            content = data["content"]
            if content:
                # Replace multiple newlines with double newline
                import re
                content = re.sub(r'\n{3,}', '\n\n', content)
                
                # Trim whitespace
                content = content.strip()
                
                data["content"] = content
                data["content_length"] = len(content)
                
                # Add reading time estimate (average reading speed: 200 words per minute)
                word_count = len(content.split())
                data["word_count"] = word_count
                data["reading_time_minutes"] = round(word_count / 200, 1)
        
        return data


class JsonSaver(BaseProcessor):
    """Save extracted data to JSON files."""
    
    def __init__(self, output_dir: str, filename_prefix: str = "crawl_data"):
        """Initialize the processor with output directory and filename prefix."""
        self.output_dir = output_dir
        self.filename_prefix = filename_prefix
        os.makedirs(output_dir, exist_ok=True)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save data to a JSON file and return the original data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.filename_prefix}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Add file info to data
        data["saved_to_file"] = filepath
        
        return data


async def product_extraction_example():
    """Demonstrate extracting product data from an e-commerce site."""
    # Set up logging
    setup_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting product extraction example...")
    
    # Create crawler
    async with HTTPCrawler() as crawler:
        # Define processors pipeline
        processors = [
            PriceNormalizer(),
            JsonSaver(output_dir="data/products", filename_prefix="products")
        ]
        
        # For demonstration, we'll use a fake e-commerce URL
        # In a real scenario, you'd use an actual e-commerce site
        url = "https://webscraper.io/test-sites/e-commerce/allinone"
        
        # Set up the product extractor
        extractor = ProductExtractor()
        
        # Fetch the page
        page = await crawler.fetch_page(url)
        
        # Extract product data
        logger.info(f"Extracting product data from {url}...")
        data = extractor.extract(page)
        
        # Process the data through the pipeline
        for processor in processors:
            logger.info(f"Processing data with {processor.__class__.__name__}...")
            data = processor.process(data)
        
        # Log results
        product_count = len(data.get("products", []))
        logger.info(f"Extracted {product_count} products from {url}")
        
        # Show a sample of the data
        if product_count > 0:
            logger.info(f"Sample product: {json.dumps(data['products'][0], indent=2)}")
        
        # Show where the data was saved
        if "saved_to_file" in data:
            logger.info(f"Data saved to: {data['saved_to_file']}")
        
        return data


async def news_article_example():
    """Demonstrate extracting and processing news article content."""
    # Set up logging
    setup_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting news article extraction example...")
    
    # Create crawler
    async with HTTPCrawler() as crawler:
        # For demonstration, we'll use a sample news article
        url = "https://demo.getbootstrap.com/docs/5.0/examples/blog/"
        
        # Set up the article extractor
        extractor = NewsArticleExtractor()
        
        # Set up processors
        processors = [
            ContentCleaner(),
            JsonSaver(output_dir="data/articles", filename_prefix="article")
        ]
        
        # Fetch the page
        page = await crawler.fetch_page(url)
        
        # Extract article data
        logger.info(f"Extracting article data from {url}...")
        data = extractor.extract(page)
        
        # Process the data through the pipeline
        for processor in processors:
            logger.info(f"Processing data with {processor.__class__.__name__}...")
            data = processor.process(data)
        
        # Log results
        logger.info(f"Article title: {data.get('title', 'Unknown')}")
        logger.info(f"Author: {data.get('author', 'Unknown')}")
        
        if "word_count" in data:
            logger.info(f"Word count: {data['word_count']}")
        
        if "reading_time_minutes" in data:
            logger.info(f"Estimated reading time: {data['reading_time_minutes']} minutes")
        
        # Show where the data was saved
        if "saved_to_file" in data:
            logger.info(f"Data saved to: {data['saved_to_file']}")
        
        return data


async def main():
    """Run the example."""
    print("1. Product Data Extraction and Processing")
    print("-" * 50)
    await product_extraction_example()
    
    print("\n" + "=" * 60 + "\n")
    
    print("2. News Article Extraction and Processing")
    print("-" * 50)
    await news_article_example()


if __name__ == "__main__":
    # Create output directories
    os.makedirs("data/products", exist_ok=True)
    os.makedirs("data/articles", exist_ok=True)
    
    # Run the examples
    asyncio.run(main()) 