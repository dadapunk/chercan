#!/usr/bin/env python
"""
CSS Extractor Example - Demonstrating how to use the CSS selector-based extractor

This example shows how to:
1. Create a CSS extractor with specific selectors
2. Extract structured data from HTML content
3. Apply transformations to extracted data
4. Extract data from multiple HTML sources
5. Create extraction templates and serialize/deserialize them
"""

import asyncio
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Any

from crawl4ai.extractors import CSSExtractor
from crawl4ai.crawlers import HTTPCrawler

# Sample HTML content for testing extraction
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample Product Page</title>
</head>
<body>
    <div class="product">
        <h1 class="product-title">Awesome Laptop</h1>
        <div class="product-price">$999.99</div>
        <div class="product-description">
            <p>This amazing laptop features:</p>
            <ul class="product-features">
                <li>16GB RAM</li>
                <li>1TB SSD</li>
                <li>4.5GHz CPU</li>
            </ul>
        </div>
        <div class="product-rating">4.8/5</div>
        <div class="product-stock">In Stock: 12</div>
    </div>
</body>
</html>
"""

SAMPLE_HTML_2 = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample Product Page</title>
</head>
<body>
    <div class="product">
        <h1 class="product-title">Premium Smartphone</h1>
        <div class="product-price">$799.99</div>
        <div class="product-description">
            <p>This feature-packed smartphone includes:</p>
            <ul class="product-features">
                <li>8GB RAM</li>
                <li>256GB Storage</li>
                <li>Triple Camera</li>
            </ul>
        </div>
        <div class="product-rating">4.6/5</div>
        <div class="product-stock">In Stock: 5</div>
    </div>
</body>
</html>
"""

# Helper functions for transformations
def extract_price(price_str: str) -> float:
    """Extract numeric price value from string like '$999.99'"""
    return float(price_str.replace('$', ''))

def extract_stock(stock_str: str) -> int:
    """Extract stock quantity from string like 'In Stock: 12'"""
    return int(stock_str.split(':')[1].strip())

def extract_rating(rating_str: str) -> float:
    """Extract rating value from string like '4.8/5'"""
    return float(rating_str.split('/')[0])

def extract_features(features_html: str) -> List[str]:
    """Extract features from HTML list"""
    soup = BeautifulSoup(features_html, 'html.parser')
    return [li.text.strip() for li in soup.find_all('li')]

async def basic_extraction_example():
    """Demonstrates basic extraction from HTML"""
    logging.info("EXAMPLE 1: Basic extraction from HTML")
    
    # Create a CSS extractor with specific selectors
    extractor = CSSExtractor(
        selectors={
            "title": ".product-title",
            "price": ".product-price",
            "description": ".product-description p",
            "rating": ".product-rating",
            "stock": ".product-stock",
        }
    )
    
    # Extract data from HTML
    result = extractor.extract(SAMPLE_HTML)
    
    logging.info(f"Extracted data: {result}")
    return result

async def extraction_with_transformations():
    """Demonstrates extraction with transformations"""
    logging.info("\nEXAMPLE 2: Extraction with transformations")
    
    # Create a CSS extractor with transformations
    extractor = CSSExtractor(
        selectors={
            "title": ".product-title",
            "price": {
                "selector": ".product-price",
                "transform": extract_price
            },
            "features": {
                "selector": ".product-features",
                "transform": extract_features
            },
            "rating": {
                "selector": ".product-rating",
                "transform": extract_rating
            },
            "stock": {
                "selector": ".product-stock",
                "transform": extract_stock
            }
        }
    )
    
    # Extract data with transformations
    result = extractor.extract(SAMPLE_HTML)
    
    logging.info(f"Extracted and transformed data: {result}")
    return result

async def multiple_items_extraction():
    """Demonstrates extraction from multiple HTML sources"""
    logging.info("\nEXAMPLE 3: Extraction from multiple HTML sources")
    
    # Create extractor
    extractor = CSSExtractor(
        selectors={
            "title": ".product-title",
            "price": {
                "selector": ".product-price",
                "transform": extract_price
            },
            "rating": {
                "selector": ".product-rating",
                "transform": extract_rating
            }
        }
    )
    
    # Extract from multiple HTML sources
    results = extractor.extract_all([SAMPLE_HTML, SAMPLE_HTML_2])
    
    logging.info(f"Products extracted: {len(results)}")
    for i, result in enumerate(results):
        logging.info(f"Product {i+1}: {result}")
    
    return results

async def template_serialization_example():
    """Demonstrates template creation and serialization"""
    logging.info("\nEXAMPLE 4: Template creation and serialization")
    
    # Create a product extraction template
    extractor = CSSExtractor(
        selectors={
            "title": ".product-title",
            "price": {
                "selector": ".product-price",
                "transform": extract_price
            },
            "features": {
                "selector": ".product-features",
                "transform": extract_features
            }
        }
    )
    
    # Serialize to JSON
    template_json = extractor.to_json()
    logging.info(f"Serialized template: {template_json}")
    
    # Create a new extractor from the template (note: custom transformations need to be re-added)
    new_extractor = CSSExtractor.from_json(template_json)
    
    # Manually re-add transformations (since they can't be serialized as JSON)
    new_extractor.add_selector("price", ".product-price", transform=extract_price)
    new_extractor.add_selector("features", ".product-features", transform=extract_features)
    
    result = new_extractor.extract(SAMPLE_HTML)
    logging.info(f"Extraction using deserialized template: {result}")
    
    return result

async def real_website_extraction():
    """Demonstrates extraction from a real website using HTTPCrawler"""
    logging.info("\nEXAMPLE 5: Extraction from a real website")
    
    # Create a crawler to fetch HTML
    crawler = HTTPCrawler()
    
    # Define the extractor for a specific website
    # Example using quotes.toscrape.com
    extractor = CSSExtractor(
        selectors={
            "quote": ".quote .text",
            "author": ".quote .author",
            "tags": {
                "selector": ".quote .tags",
                "transform": lambda tags_html: [
                    tag.text.strip() for tag in 
                    BeautifulSoup(tags_html, 'html.parser').select('.tag')
                ]
            }
        }
    )
    
    try:
        # Crawl a page
        url = "http://quotes.toscrape.com/"
        result = await crawler.fetch(url)
        
        if result.success:
            # Apply multiple extraction strategy to get all quotes
            all_quotes = extractor.extract(result.content, multiple=True, container_selector=".quote")
            
            logging.info(f"Extracted {len(all_quotes)} quotes from {url}")
            for i, quote in enumerate(all_quotes[:3]):  # Show only first 3 quotes
                logging.info(f"Quote {i+1}: {quote}")
                
            return all_quotes
        else:
            logging.error(f"Failed to fetch {url}: {result.error}")
            return None
    except Exception as e:
        logging.error(f"Error during crawling: {e}")
        return None

async def main():
    """Run all CSS extraction examples"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("CSS Selector Extraction Examples")
    logging.info("=" * 50)
    
    await basic_extraction_example()
    await extraction_with_transformations()
    await multiple_items_extraction()
    await template_serialization_example()
    await real_website_extraction()
    
    logging.info("=" * 50)
    logging.info("Examples completed")

if __name__ == "__main__":
    asyncio.run(main()) 