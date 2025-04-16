#!/usr/bin/env python
"""
Extractor Factory Example - Demonstrating how to use the extraction factory

This example shows how to:
1. Create and use different extractors with the factory
2. Automatically select appropriate extractors for different content types
3. Extract data with fallback strategies
4. Configure extractors with simple configuration dictionaries
5. Create and register custom extractors
"""

import asyncio
import logging
from typing import Dict, Any, Union

from crawl4ai.extractors import (
    ExtractorFactory,
    BaseExtractor,
    CSSExtractor,
    XPathExtractor,
    RegExExtractor,
    LLMExtractor
)
from crawl4ai.config import LLMConfig
from crawl4ai.models import Page
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

# Sample XML content for testing extraction
SAMPLE_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<product>
    <name>Premium Smartphone</name>
    <price currency="USD">799.99</price>
    <description>This feature-packed smartphone includes:</description>
    <features>
        <feature>8GB RAM</feature>
        <feature>256GB Storage</feature>
        <feature>Triple Camera</feature>
    </features>
    <rating>4.6</rating>
    <stock status="in_stock">5</stock>
</product>
"""

# Sample JSON content for testing extraction
SAMPLE_JSON = """
{
    "product": {
        "name": "Wireless Headphones",
        "price": 149.99,
        "description": "High-quality wireless headphones with noise cancellation",
        "features": [
            "Noise cancellation",
            "20-hour battery life",
            "Bluetooth 5.0"
        ],
        "rating": 4.7,
        "stock": {
            "status": "in_stock",
            "count": 8
        }
    }
}
"""

# Sample text content for testing extraction
SAMPLE_TEXT = """
Product: Smart Watch Pro
Price: $299.99
Description: Advanced smartwatch with health monitoring features

Features:
- Heart rate monitoring
- Sleep tracking
- GPS
- Water resistant up to 50m

Rating: 4.5/5
In Stock: 15 units
"""

async def create_specific_extractors():
    """Demonstrates creating specific extractors using the factory"""
    logging.info("EXAMPLE 1: Creating specific extractors using the factory")
    
    # Create an extractor factory
    factory = ExtractorFactory()
    
    # Create a CSS extractor
    css_extractor = factory.create_css_extractor({
        "title": ".product-title",
        "price": ".product-price",
        "description": ".product-description p",
        "features": {
            "selector": ".product-features li",
            "multiple": True
        },
        "rating": ".product-rating",
        "stock": ".product-stock"
    })
    
    # Create an XPath extractor
    xpath_extractor = factory.create_xpath_extractor({
        "name": "/product/name/text()",
        "price": "/product/price/text()",
        "features": {
            "xpath": "/product/features/feature/text()",
            "multiple": True
        },
        "rating": "/product/rating/text()",
        "stock": "/product/stock/text()"
    })
    
    # Create a RegEx extractor
    regex_extractor = factory.create_regex_extractor({
        "product": r"Product: (.+)",
        "price": r"Price: \$(\d+\.\d+)",
        "features": {
            "pattern": r"- (.+)",
            "multiple": True
        },
        "rating": r"Rating: ([\d\.]+)/5",
        "stock": r"In Stock: (\d+)"
    })
    
    # Extract data using the specific extractors
    html_result = css_extractor.extract(SAMPLE_HTML)
    xml_result = xpath_extractor.extract(SAMPLE_XML)
    text_result = regex_extractor.extract(SAMPLE_TEXT)
    
    logging.info("CSS Extractor (HTML):")
    logging.info(f"  Title: {html_result.get('title', 'N/A')}")
    logging.info(f"  Price: {html_result.get('price', 'N/A')}")
    logging.info(f"  Features: {html_result.get('features', [])}")
    
    logging.info("\nXPath Extractor (XML):")
    logging.info(f"  Name: {xml_result.get('name', 'N/A')}")
    logging.info(f"  Price: {xml_result.get('price', 'N/A')}")
    logging.info(f"  Features: {xml_result.get('features', [])}")
    
    logging.info("\nRegEx Extractor (Text):")
    logging.info(f"  Product: {text_result.get('product', 'N/A')}")
    logging.info(f"  Price: {text_result.get('price', 'N/A')}")
    logging.info(f"  Features: {text_result.get('features', [])}")
    
    return {
        "html": html_result,
        "xml": xml_result,
        "text": text_result
    }

async def auto_select_extractors():
    """Demonstrates automatic selection of extractors based on content type"""
    logging.info("\nEXAMPLE 2: Automatic selection of extractors based on content type")
    
    factory = ExtractorFactory()
    
    # Auto-select extractors for different content types
    html_extractor = factory.get_extractor_for_content(SAMPLE_HTML)
    xml_extractor = factory.get_extractor_for_content(SAMPLE_XML)
    json_extractor = factory.get_extractor_for_content(SAMPLE_JSON)
    text_extractor = factory.get_extractor_for_content(SAMPLE_TEXT)
    
    logging.info(f"HTML content: Selected {html_extractor.__class__.__name__}")
    logging.info(f"XML content: Selected {xml_extractor.__class__.__name__}")
    logging.info(f"JSON content: Selected {json_extractor.__class__.__name__}")
    logging.info(f"Text content: Selected {text_extractor.__class__.__name__}")
    
    return {
        "html_extractor": html_extractor.__class__.__name__,
        "xml_extractor": xml_extractor.__class__.__name__,
        "json_extractor": json_extractor.__class__.__name__,
        "text_extractor": text_extractor.__class__.__name__,
    }

async def extract_with_fallback():
    """Demonstrates extraction with fallback strategies"""
    logging.info("\nEXAMPLE 3: Extraction with fallback strategies")
    
    factory = ExtractorFactory()
    
    # Configure some extractors for HTML content
    css_config = {
        "selectors": {
            "title": ".product-title",
            "price": ".product-price",
            "features": {
                "selector": ".product-features li",
                "multiple": True
            }
        }
    }
    factory.create_css_extractor(**css_config)
    
    xpath_config = {
        "xpaths": {
            "title": "//h1[@class='product-title']/text()",
            "price": "//div[@class='product-price']/text()",
            "features": {
                "xpath": "//ul[@class='product-features']/li/text()",
                "multiple": True
            }
        }
    }
    factory.create_xpath_extractor(**xpath_config)
    
    # Extract with fallback (will try CSS first, then XPath, then others)
    result = factory.extract(
        SAMPLE_HTML,
        extractors=['css', 'xpath', 'regex'],
        fallback=True
    )
    
    logging.info("Extracted data with fallback strategy:")
    logging.info(f"  Title: {result.get('title', 'N/A')}")
    logging.info(f"  Price: {result.get('price', 'N/A')}")
    logging.info(f"  Features: {result.get('features', [])}")
    
    return result

async def extract_with_configuration():
    """Demonstrates extraction using configuration dictionaries"""
    logging.info("\nEXAMPLE 4: Extraction using configuration dictionaries")
    
    factory = ExtractorFactory()
    
    # Different configuration approaches for different content types
    html_config = {
        "extractor_type": "css",
        "css_config": {
            "selectors": {
                "title": ".product-title",
                "price": ".product-price",
                "features": {
                    "selector": ".product-features li",
                    "multiple": True
                }
            }
        }
    }
    
    xml_config = {
        "extractor_type": "xpath",
        "xpath_config": {
            "xpaths": {
                "name": "/product/name/text()",
                "price": "/product/price/text()",
                "features": {
                    "xpath": "/product/features/feature/text()",
                    "multiple": True
                }
            }
        }
    }
    
    text_config = {
        "extractor_type": "regex",
        "regex_config": {
            "patterns": {
                "product": r"Product: (.+)",
                "price": r"Price: \$(\d+\.\d+)",
                "features": {
                    "pattern": r"- (.+)",
                    "multiple": True
                }
            }
        }
    }
    
    # Auto-detect configuration (no extractor type specified)
    auto_config = {
        "fallback": True
    }
    
    # Extract using configurations
    html_result = factory.extract_with_configuration(SAMPLE_HTML, html_config)
    xml_result = factory.extract_with_configuration(SAMPLE_XML, xml_config)
    text_result = factory.extract_with_configuration(SAMPLE_TEXT, text_config)
    auto_result = factory.extract_with_configuration(SAMPLE_JSON, auto_config)
    
    logging.info("CSS config (HTML):")
    logging.info(f"  Title: {html_result.get('title', 'N/A')}")
    
    logging.info("\nXPath config (XML):")
    logging.info(f"  Name: {xml_result.get('name', 'N/A')}")
    
    logging.info("\nRegEx config (Text):")
    logging.info(f"  Product: {text_result.get('product', 'N/A')}")
    
    logging.info("\nAuto config (JSON):")
    if auto_result:
        if 'product' in auto_result:
            logging.info(f"  Product: {auto_result.get('product', {}).get('name', 'N/A')}")
        else:
            logging.info(f"  Auto result keys: {list(auto_result.keys())}")
    
    return {
        "html": html_result,
        "xml": xml_result,
        "text": text_result,
        "auto": auto_result
    }

async def custom_extractor_example():
    """Demonstrates creating and registering a custom extractor"""
    logging.info("\nEXAMPLE 5: Creating and registering a custom extractor")
    
    # Create a custom extractor by inheriting from BaseExtractor
    class CSVExtractor(BaseExtractor):
        """Extract data from CSV content."""
        
        def __init__(self, delimiter: str = ',', has_header: bool = True):
            self.delimiter = delimiter
            self.has_header = has_header
        
        def extract(self, content: Union[str, Page]) -> Dict[str, Any]:
            """Extract data from CSV content."""
            if not isinstance(content, str):
                if hasattr(content, 'content'):
                    content = getattr(content, 'content')
                else:
                    return {}
            
            lines = content.strip().split('\n')
            if not lines:
                return {}
            
            if self.has_header:
                header = lines[0].split(self.delimiter)
                data_lines = lines[1:]
                
                result = {}
                for line in data_lines:
                    values = line.split(self.delimiter)
                    # Create a record for each line
                    record = {}
                    for i, field in enumerate(header):
                        if i < len(values):
                            record[field.strip()] = values[i].strip()
                    
                    # Use the first column value as key if available
                    if values and values[0].strip():
                        key = values[0].strip()
                        result[key] = record
                    
                return result
            else:
                # No header, just return lines as list
                return {
                    "lines": [line.split(self.delimiter) for line in lines]
                }
    
    # Sample CSV content
    csv_content = """
    id,name,price,category
    1,Laptop,999.99,Electronics
    2,Smartphone,799.99,Electronics
    3,Headphones,149.99,Audio
    """
    
    # Create a factory and register the custom extractor
    factory = ExtractorFactory()
    factory.register_extractor('csv', CSVExtractor)
    
    # Create and use the CSV extractor
    csv_extractor = factory.create_extractor('csv', delimiter=',', has_header=True)
    result = csv_extractor.extract(csv_content.strip())
    
    logging.info("Extracted data using custom CSV extractor:")
    for key, record in result.items():
        logging.info(f"  {key}: {record}")
    
    return result

async def real_website_example():
    """Demonstrates using the factory with a real website"""
    logging.info("\nEXAMPLE 6: Using the factory with a real website")
    
    factory = ExtractorFactory()
    crawler = HTTPCrawler()
    
    # Different extractor configurations for the same website
    css_config = {
        "extractor_type": "css",
        "css_config": {
            "selectors": {
                "title": "title",
                "quotes": {
                    "selector": ".quote", 
                    "multiple": True,
                    "transform": lambda elem: {
                        "text": elem.select_one(".text").get_text() if elem.select_one(".text") else "",
                        "author": elem.select_one(".author").get_text() if elem.select_one(".author") else "",
                        "tags": [tag.get_text() for tag in elem.select(".tag")]
                    }
                }
            }
        }
    }
    
    xpath_config = {
        "extractor_type": "xpath",
        "xpath_config": {
            "xpaths": {
                "title": "//title/text()",
                "quotes": {
                    "xpath": "//div[@class='quote']",
                    "multiple": True,
                    "transform": lambda elem: {
                        "text": elem.xpath("./span[@class='text']/text()")[0] if elem.xpath("./span[@class='text']/text()") else "",
                        "author": elem.xpath("./span/small[@class='author']/text()")[0] if elem.xpath("./span/small[@class='author']/text()") else "",
                        "tags": elem.xpath("./div[@class='tags']/a[@class='tag']/text()")
                    }
                }
            }
        }
    }
    
    # Try to get content from a real website
    try:
        url = "http://quotes.toscrape.com/"
        result = await crawler.fetch(url)
        
        if result.success:
            # Extract using CSS selectors
            css_result = factory.extract_with_configuration(result.content, css_config)
            
            # Extract using XPath
            xpath_result = factory.extract_with_configuration(result.content, xpath_config)
            
            # Also try the auto-detection
            auto_result = factory.extract(
                result.content,
                fallback=True
            )
            
            # Log some results
            logging.info(f"CSS extractor found {len(css_result.get('quotes', []))} quotes")
            logging.info(f"XPath extractor found {len(xpath_result.get('quotes', []))} quotes")
            
            if css_result.get('quotes'):
                quote = css_result['quotes'][0]
                logging.info(f"First quote (CSS): \"{quote.get('text', '')[:50]}...\"")
                logging.info(f"Author (CSS): {quote.get('author', 'Unknown')}")
            
            if xpath_result.get('quotes'):
                quote = xpath_result['quotes'][0]
                logging.info(f"First quote (XPath): \"{quote.get('text', '')[:50]}...\"")
                logging.info(f"Author (XPath): {quote.get('author', 'Unknown')}")
            
            if auto_result:
                logging.info(f"Auto extractor found these keys: {list(auto_result.keys())}")
            
            return {
                "css": css_result,
                "xpath": xpath_result,
                "auto": auto_result
            }
        else:
            logging.error(f"Failed to fetch {url}: {result.error}")
            return None
    except Exception as e:
        logging.error(f"Error during crawling: {e}")
        return None

async def main():
    """Run all extractor factory examples"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("Extractor Factory Examples")
    logging.info("=" * 50)
    
    await create_specific_extractors()
    await auto_select_extractors()
    await extract_with_fallback()
    await extract_with_configuration()
    await custom_extractor_example()
    await real_website_example()
    
    logging.info("=" * 50)
    logging.info("Examples completed")

if __name__ == "__main__":
    asyncio.run(main()) 