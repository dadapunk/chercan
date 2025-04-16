#!/usr/bin/env python
"""
XPath Extractor Example - Demonstrating how to use XPath-based extraction

This example shows how to:
1. Create an XPath extractor with specific expressions
2. Extract structured data from HTML content
3. Apply transformations to extracted data
4. Work with XML namespaces
5. Extract data from multiple HTML sources
"""

import asyncio
import logging
from lxml import etree
from typing import Dict, List, Any

from crawl4ai.extractors import XPathExtractor
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

# Sample XML content with namespaces
SAMPLE_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
  <channel>
    <title>Technology News</title>
    <link>https://example.com/news</link>
    <description>Latest tech news</description>
    <item>
      <title>New AI Breakthrough</title>
      <link>https://example.com/news/ai-breakthrough</link>
      <dc:creator>John Smith</dc:creator>
      <pubDate>Mon, 20 Jun 2023 12:00:00 GMT</pubDate>
      <description>Scientists have made a significant breakthrough in AI research.</description>
      <category>Artificial Intelligence</category>
      <category>Research</category>
    </item>
    <item>
      <title>Tech Company Releases New Product</title>
      <link>https://example.com/news/new-product</link>
      <dc:creator>Jane Doe</dc:creator>
      <pubDate>Tue, 21 Jun 2023 10:30:00 GMT</pubDate>
      <description>A major tech company has released a revolutionary new product.</description>
      <category>Products</category>
      <category>Technology</category>
    </item>
  </channel>
</rss>
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

async def basic_extraction_example():
    """Demonstrates basic extraction from HTML using XPath"""
    logging.info("EXAMPLE 1: Basic extraction from HTML using XPath")
    
    # Create an XPath extractor with specific expressions
    extractor = XPathExtractor(
        xpaths={
            "title": "//h1[@class='product-title']/text()",
            "price": "//div[@class='product-price']/text()",
            "description": "//div[@class='product-description']/p/text()",
            "rating": "//div[@class='product-rating']/text()",
            "stock": "//div[@class='product-stock']/text()",
        }
    )
    
    # Extract data from HTML
    result = extractor.extract(SAMPLE_HTML)
    
    logging.info(f"Extracted data: {result}")
    return result

async def extraction_with_transformations():
    """Demonstrates extraction with transformations"""
    logging.info("\nEXAMPLE 2: Extraction with transformations")
    
    # Create an XPath extractor with transformations
    extractor = XPathExtractor(
        xpaths={
            "title": "//h1[@class='product-title']/text()",
            "price": {
                "xpath": "//div[@class='product-price']/text()",
                "transform": extract_price
            },
            "features": {
                "xpath": "//ul[@class='product-features']/li/text()",
                "multiple": True
            },
            "rating": {
                "xpath": "//div[@class='product-rating']/text()",
                "transform": extract_rating
            },
            "stock": {
                "xpath": "//div[@class='product-stock']/text()",
                "transform": extract_stock
            }
        }
    )
    
    # Extract data with transformations
    result = extractor.extract(SAMPLE_HTML)
    
    logging.info(f"Extracted and transformed data: {result}")
    return result

async def xml_namespace_extraction():
    """Demonstrates extraction from XML with namespaces"""
    logging.info("\nEXAMPLE 3: Extraction from XML with namespaces")
    
    # Create an XPath extractor with namespaces
    extractor = XPathExtractor(
        xpaths={
            "feed_title": "/rss/channel/title/text()",
            "feed_link": "/rss/channel/link/text()",
            "items": {
                "xpath": "//item",
                "multiple": True,
                "transform": lambda item: {
                    "title": etree.tostring(item.xpath("./title")[0], method="text", encoding="unicode").strip(),
                    "link": etree.tostring(item.xpath("./link")[0], method="text", encoding="unicode").strip(),
                    "author": etree.tostring(item.xpath("./dc:creator", namespaces={"dc": "http://purl.org/dc/elements/1.1/"})[0], 
                               method="text", encoding="unicode").strip(),
                    "categories": [
                        etree.tostring(cat, method="text", encoding="unicode").strip() 
                        for cat in item.xpath("./category")
                    ]
                }
            }
        },
        namespaces={
            "dc": "http://purl.org/dc/elements/1.1/"
        }
    )
    
    # Extract data from XML with namespaces
    result = extractor.extract(SAMPLE_XML)
    
    logging.info(f"Feed title: {result['feed_title']}")
    logging.info(f"Feed link: {result['feed_link']}")
    logging.info(f"Number of items: {len(result['items'])}")
    for i, item in enumerate(result['items']):
        logging.info(f"Item {i+1}:")
        logging.info(f"  Title: {item['title']}")
        logging.info(f"  Author: {item['author']}")
        logging.info(f"  Categories: {', '.join(item['categories'])}")
    
    return result

async def document_access_extraction():
    """Demonstrates accessing the document and using complex XPath expressions"""
    logging.info("\nEXAMPLE 4: Accessing the document and using complex XPath expressions")
    
    # Create an XPath extractor with more complex expressions
    extractor = XPathExtractor(
        xpaths={
            "product_info": {
                "xpath": "//div[@class='product']",
                "transform": lambda elem: {
                    "name": elem.xpath(".//h1/text()")[0],
                    "price": extract_price(elem.xpath(".//div[@class='product-price']/text()")[0]),
                    "feature_count": len(elem.xpath(".//ul[@class='product-features']/li")),
                    "first_feature": elem.xpath(".//ul[@class='product-features']/li[1]/text()")[0],
                    "last_feature": elem.xpath(".//ul[@class='product-features']/li[last()]/text()")[0]
                }
            },
            "all_text_nodes": {
                "xpath": "//text()[normalize-space()]",
                "multiple": True,
                "transform": lambda t: t.strip()
            }
        }
    )
    
    # Extract data using complex expressions
    result = extractor.extract(SAMPLE_HTML)
    
    logging.info(f"Product information:")
    logging.info(f"  Name: {result['product_info']['name']}")
    logging.info(f"  Price: ${result['product_info']['price']}")
    logging.info(f"  Feature count: {result['product_info']['feature_count']}")
    logging.info(f"  First feature: {result['product_info']['first_feature']}")
    logging.info(f"  Last feature: {result['product_info']['last_feature']}")
    
    logging.info(f"Found {len(result['all_text_nodes'])} text nodes in document")
    
    return result

async def real_website_extraction():
    """Demonstrates extraction from a real website using XPath"""
    logging.info("\nEXAMPLE 5: Extraction from a real website using XPath")
    
    # Create a crawler to fetch HTML
    crawler = HTTPCrawler()
    
    # Create XPath extractor for quotes.toscrape.com
    extractor = XPathExtractor(
        xpaths={
            "quotes": {
                "xpath": "//div[@class='quote']",
                "multiple": True,
                "transform": lambda quote_elem: {
                    "text": quote_elem.xpath("./span[@class='text']/text()")[0],
                    "author": quote_elem.xpath("./span/small[@class='author']/text()")[0],
                    "tags": [
                        tag.strip() for tag in 
                        quote_elem.xpath("./div[@class='tags']/a[@class='tag']/text()")
                    ]
                }
            },
            "page_title": "//title/text()"
        }
    )
    
    try:
        # Crawl a page
        url = "http://quotes.toscrape.com/"
        result = await crawler.fetch(url)
        
        if result.success:
            # Extract data using XPath
            extracted_data = extractor.extract(result.content)
            
            logging.info(f"Page title: {extracted_data['page_title']}")
            logging.info(f"Extracted {len(extracted_data['quotes'])} quotes from {url}")
            
            for i, quote in enumerate(extracted_data['quotes'][:3]):  # Show only first 3 quotes
                logging.info(f"Quote {i+1}:")
                logging.info(f"  Text: {quote['text'][:50]}...")
                logging.info(f"  Author: {quote['author']}")
                logging.info(f"  Tags: {', '.join(quote['tags'])}")
            
            return extracted_data
        else:
            logging.error(f"Failed to fetch {url}: {result.error}")
            return None
    except Exception as e:
        logging.error(f"Error during crawling: {e}")
        return None

async def main():
    """Run all XPath extraction examples"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("XPath Extraction Examples")
    logging.info("=" * 50)
    
    await basic_extraction_example()
    await extraction_with_transformations()
    await xml_namespace_extraction()
    await document_access_extraction()
    await real_website_extraction()
    
    logging.info("=" * 50)
    logging.info("Examples completed")

if __name__ == "__main__":
    asyncio.run(main()) 