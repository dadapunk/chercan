#!/usr/bin/env python
"""
RegEx Extractor Example - Demonstrating how to use regex-based extraction

This example shows how to:
1. Create a RegEx extractor with specific patterns
2. Extract structured data from text content
3. Apply transformations to extracted data
4. Work with named capture groups
5. Handle multiple matches with list-based extraction
"""

import asyncio
import logging
import re
from typing import Dict, List, Any

from crawl4ai.extractors import RegExExtractor
from crawl4ai.crawlers import HTTPCrawler

# Sample text content for testing extraction
SAMPLE_TEXT = """
Product: Awesome Laptop Pro 2023
SKU: ABC-12345-XYZ
Price: $999.99
Available: Yes (In Stock: 12)
Shipping: Free shipping on orders over $50

Technical Specifications:
- Memory: 16GB DDR4
- Storage: 1TB SSD
- Processor: Intel Core i7-11800H 4.5GHz
- Screen: 15.6" Full HD IPS Display

Customer Reviews:
★★★★★ 5/5 - John D. (Verified Purchase) - This laptop exceeds my expectations!
★★★★☆ 4/5 - Emily S. (Verified Purchase) - Great performance but battery life is average.
★★★★★ 5/5 - Michael R. - Perfect for gaming and development work.

Contact Information:
Email: support@example.com
Phone: +1-800-123-4567
"""

SAMPLE_TEXT_2 = """
Product: Premium Smartphone X1
SKU: SMS-98765-PRO
Price: $799.99
Available: Yes (In Stock: 5)
Shipping: Free shipping on orders over $50

Technical Specifications:
- Memory: 8GB RAM
- Storage: 256GB Flash Storage
- Processor: Snapdragon 888 2.84GHz
- Screen: 6.7" AMOLED Display

Customer Reviews:
★★★★★ 5/5 - Sarah M. (Verified Purchase) - Best phone I've ever had!
★★★☆☆ 3/5 - David T. (Verified Purchase) - Good but overpriced.
★★★★☆ 4/5 - Lisa K. - Beautiful design and good camera.

Contact Information:
Email: mobile-support@example.com
Phone: +1-800-987-6543
"""

# Helper functions for transformations
def extract_price(price_str: str) -> float:
    """Extract numeric price value from string like '$999.99'"""
    return float(price_str.replace('$', ''))

def parse_stock(availability: str) -> Dict[str, Any]:
    """Parse availability text to get stock status and count"""
    stock_match = re.search(r'In Stock: (\d+)', availability)
    return {
        "available": "Yes" in availability,
        "stock_count": int(stock_match.group(1)) if stock_match else 0
    }

def parse_review(review: str) -> Dict[str, Any]:
    """Parse a review string into structured data"""
    rating_match = re.search(r'(\d)/5', review)
    name_match = re.search(r'-\s+(.+?)\s+\(', review)
    verified = "Verified Purchase" in review
    comment = review.split('-')[-1].strip() if '-' in review else ""
    
    return {
        "rating": int(rating_match.group(1)) if rating_match else None,
        "name": name_match.group(1) if name_match else "Anonymous",
        "verified": verified,
        "comment": comment
    }

async def basic_extraction_example():
    """Demonstrates basic regex extraction"""
    logging.info("EXAMPLE 1: Basic regex extraction")
    
    # Create a RegEx extractor with specific patterns
    extractor = RegExExtractor(
        patterns={
            "product_name": r"Product: (.+)",
            "sku": r"SKU: ([A-Z]+-\d+-[A-Z]+)",
            "price": r"Price: \$(\d+\.\d+)",
            "availability": r"Available: (.+)",
        }
    )
    
    # Extract data from text
    result = extractor.extract(SAMPLE_TEXT)
    
    logging.info(f"Extracted data: {result}")
    return result

async def extraction_with_transformations():
    """Demonstrates extraction with transformations"""
    logging.info("\nEXAMPLE 2: Extraction with transformations")
    
    # Create a RegEx extractor with transformations
    extractor = RegExExtractor(
        patterns={
            "product_name": r"Product: (.+)",
            "price": {
                "pattern": r"Price: \$(\d+\.\d+)",
                "transform": float  # Simple transformation to convert to float
            },
            "availability": {
                "pattern": r"Available: (.+)",
                "transform": parse_stock  # Custom transformation
            },
        }
    )
    
    # Extract data with transformations
    result = extractor.extract(SAMPLE_TEXT)
    
    logging.info(f"Extracted and transformed data: {result}")
    return result

async def named_groups_extraction():
    """Demonstrates extraction using named capture groups"""
    logging.info("\nEXAMPLE 3: Extraction using named capture groups")
    
    # Create a RegEx extractor with named groups
    extractor = RegExExtractor(
        patterns={
            "specs": r"Memory: (?P<memory>.+)\n- Storage: (?P<storage>.+)\n- Processor: (?P<processor>.+)\n- Screen: (?P<screen>.+)",
            "contact": r"Email: (?P<email>.+)\nPhone: (?P<phone>.+)"
        },
        # Set to use named groups rather than indexed groups
        use_named_groups=True
    )
    
    # Extract data using named groups
    result = extractor.extract(SAMPLE_TEXT)
    
    logging.info(f"Extracted data with named groups: {result}")
    return result

async def multiple_matches_extraction():
    """Demonstrates extraction of multiple matches"""
    logging.info("\nEXAMPLE 4: Extraction of multiple matches")
    
    # Create a RegEx extractor for reviews with multiple matches
    extractor = RegExExtractor(
        patterns={
            "reviews": {
                "pattern": r"★.+?- .+?- .+",  # Pattern to match a review line
                "transform": parse_review,  # Transform to parse the review
                "multiple": True  # Extract all matches as a list
            }
        }
    )
    
    # Extract multiple reviews
    result = extractor.extract(SAMPLE_TEXT)
    
    logging.info(f"Extracted {len(result['reviews'])} reviews:")
    for i, review in enumerate(result["reviews"]):
        logging.info(f"Review {i+1}: {review}")
    
    return result

async def extract_from_multiple_sources():
    """Demonstrates extraction from multiple text sources"""
    logging.info("\nEXAMPLE 5: Extraction from multiple text sources")
    
    # Create a RegEx extractor
    extractor = RegExExtractor(
        patterns={
            "product_name": r"Product: (.+)",
            "price": {
                "pattern": r"Price: \$(\d+\.\d+)",
                "transform": extract_price
            },
            "specs": r"Memory: (.+)\n- Storage: (.+)",
        }
    )
    
    # Extract from multiple texts
    sources = [SAMPLE_TEXT, SAMPLE_TEXT_2]
    results = extractor.extract_all(sources)
    
    logging.info(f"Products extracted: {len(results)}")
    for i, result in enumerate(results):
        logging.info(f"Product {i+1}: {result}")
    
    return results

async def web_content_extraction():
    """Demonstrates extraction from web content"""
    logging.info("\nEXAMPLE 6: Extraction from web content")
    
    # Create a crawler to fetch content
    crawler = HTTPCrawler()
    
    # Create a RegEx extractor for GitHub information
    extractor = RegExExtractor(
        patterns={
            "title": r"<title>(.+?)</title>",
            "description": r'<meta name="description" content="(.+?)"',
            "programming_languages": {
                "pattern": r'<span class="Progress-item.+?programmingLanguage.+?>(.+?)</span>',
                "multiple": True  # Get all programming languages
            }
        }
    )
    
    try:
        # Crawl a GitHub page
        url = "https://github.com/python/cpython"
        result = await crawler.fetch(url)
        
        if result.success:
            # Extract data from HTML
            extracted_data = extractor.extract(result.content)
            
            logging.info(f"Extracted data from {url}:")
            logging.info(f"Title: {extracted_data.get('title', 'N/A')}")
            logging.info(f"Description: {extracted_data.get('description', 'N/A')}")
            logging.info(f"Programming languages: {extracted_data.get('programming_languages', [])}")
            
            return extracted_data
        else:
            logging.error(f"Failed to fetch {url}: {result.error}")
            return None
    except Exception as e:
        logging.error(f"Error during crawling: {e}")
        return None

async def main():
    """Run all RegEx extraction examples"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("RegEx Extraction Examples")
    logging.info("=" * 50)
    
    await basic_extraction_example()
    await extraction_with_transformations()
    await named_groups_extraction()
    await multiple_matches_extraction()
    await extract_from_multiple_sources()
    await web_content_extraction()
    
    logging.info("=" * 50)
    logging.info("Examples completed")

if __name__ == "__main__":
    asyncio.run(main()) 