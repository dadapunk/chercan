#!/usr/bin/env python
"""
LLM Extractor Example - Demonstrating how to use LLM-based extraction

This example shows how to:
1. Create an LLM extractor with specific schemas
2. Extract structured data from HTML content using LLMs
3. Configure different LLM providers
4. Use different extraction schemas for different data types
5. Process multiple documents with LLM extraction
"""

import asyncio
import logging
import os
from typing import Dict, List, Any
from pprint import pformat

from crawl4ai.extractors import LLMExtractor
from crawl4ai.config import LLMConfig
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

# Sample news article for testing extraction
SAMPLE_NEWS = """
# Major Breakthrough in AI Research

Published on: June 15, 2023
Author: Dr. Jane Smith
Category: Technology

A team of researchers at AI Labs has announced a major breakthrough in artificial intelligence research.
The new algorithm, called DeepThought, can understand and generate human language with unprecedented accuracy.

Key points:
- 95% accuracy on language understanding benchmarks
- Requires 50% less computational resources than previous models
- Can generate creative content indistinguishable from human-written text

Dr. Smith, the lead researcher, said "This is a significant step forward in our quest to create truly intelligent machines."

The technology is expected to be commercialized within the next two years.

Read the full research paper at: https://example.com/research/deepthought
"""

async def basic_product_extraction():
    """Demonstrates basic product information extraction using an LLM"""
    logging.info("EXAMPLE 1: Basic product information extraction using LLM")
    
    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        logging.warning("OpenAI API key not found in environment variables. Skipping LLM example.")
        logging.warning("Set OPENAI_API_KEY environment variable to run this example.")
        return {"simulated": True, "title": "Awesome Laptop", "price": 999.99}
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.1  # Lower temperature for more deterministic extraction
    )
    
    # Create a product schema
    product_schema = {
        "title": "string",
        "price": "number",
        "features": ["string"],
        "rating": "number",
        "in_stock": "boolean",
        "stock_count": "number"
    }
    
    # Create an LLM extractor
    extractor = LLMExtractor(
        schema=product_schema,
        extraction_prompt="Extract product information from this HTML content. The price should be a number without currency symbols.",
        llm_config=llm_config
    )
    
    # Extract data
    try:
        result = await extractor.extract_async(SAMPLE_HTML)
        logging.info(f"Extracted product data:\n{pformat(result)}")
        return result
    except Exception as e:
        logging.error(f"Error during extraction: {e}")
        # Return simulated data for example purposes when API is not available
        return {"simulated": True, "title": "Awesome Laptop", "price": 999.99}

async def news_article_extraction():
    """Demonstrates news article extraction using an LLM"""
    logging.info("\nEXAMPLE 2: News article extraction using LLM")
    
    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        logging.warning("OpenAI API key not found in environment variables. Skipping LLM example.")
        logging.warning("Set OPENAI_API_KEY environment variable to run this example.")
        return {"simulated": True, "title": "Major Breakthrough in AI Research"}
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    # Create a news article schema
    news_schema = {
        "title": "string",
        "publication_date": "string",
        "author": "string",
        "category": "string",
        "summary": "string",
        "key_points": ["string"],
        "quotes": ["string"],
        "links": ["string"]
    }
    
    # Create an LLM extractor
    extractor = LLMExtractor(
        schema=news_schema,
        extraction_prompt="Extract news article information from this content.",
        llm_config=llm_config
    )
    
    # Extract data
    try:
        result = await extractor.extract_async(SAMPLE_NEWS)
        logging.info(f"Extracted news article data:\n{pformat(result)}")
        return result
    except Exception as e:
        logging.error(f"Error during extraction: {e}")
        # Return simulated data for example purposes when API is not available
        return {"simulated": True, "title": "Major Breakthrough in AI Research"}

async def custom_provider_extraction():
    """Demonstrates extraction using a custom LLM provider"""
    logging.info("\nEXAMPLE 3: Extraction using a custom LLM provider")
    
    # Define a custom LLM callable for demonstration
    async def custom_llm_callable(prompt: str, config: LLMConfig):
        """Custom LLM function that simulates an LLM response"""
        logging.info(f"Custom LLM received prompt: {prompt[:100]}...")
        
        # In a real implementation, this would call your custom LLM API
        # For this example, we'll just return a predefined response
        if "product" in prompt.lower():
            return """
            ```json
            {
                "title": "Awesome Laptop",
                "price": 999.99,
                "features": ["16GB RAM", "1TB SSD", "4.5GHz CPU"],
                "rating": 4.8,
                "in_stock": true,
                "stock_count": 12
            }
            ```
            """
        else:
            return """Sorry, I couldn't extract the requested information."""
    
    # Create an LLM configuration with custom provider
    llm_config = LLMConfig(
        provider="custom",
        custom_llm_callable=custom_llm_callable
    )
    
    # Create a product schema
    product_schema = {
        "title": "string",
        "price": "number",
        "features": ["string"],
        "rating": "number",
        "in_stock": "boolean",
        "stock_count": "number"
    }
    
    # Create an LLM extractor
    extractor = LLMExtractor(
        schema=product_schema,
        extraction_prompt="Extract product information from this HTML content.",
        llm_config=llm_config
    )
    
    # Extract data
    result = await extractor.extract_async(SAMPLE_HTML)
    logging.info(f"Extracted data using custom LLM:\n{pformat(result)}")
    return result

async def real_website_extraction():
    """Demonstrates extraction from a real website"""
    logging.info("\nEXAMPLE 4: Extraction from a real website")
    
    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        logging.warning("OpenAI API key not found in environment variables. Skipping LLM example.")
        logging.warning("Set OPENAI_API_KEY environment variable to run this example.")
        return {"simulated": True, "title": "Famous Quotes"}
    
    # Create a crawler to fetch HTML
    crawler = HTTPCrawler()
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    # Create a quotes website schema
    quotes_schema = {
        "page_title": "string",
        "quotes": [
            {
                "text": "string",
                "author": "string",
                "tags": ["string"]
            }
        ]
    }
    
    # Create an LLM extractor
    extractor = LLMExtractor(
        schema=quotes_schema,
        extraction_prompt="Extract quotes from this website. The quotes should include the text, author, and tags.",
        llm_config=llm_config
    )
    
    try:
        # Crawl a page
        url = "http://quotes.toscrape.com/"
        result = await crawler.fetch(url)
        
        if result.success:
            # Extract data using LLM
            try:
                extracted_data = await extractor.extract_async(result.content)
                
                logging.info(f"Page title: {extracted_data.get('page_title', 'Unknown')}")
                quotes = extracted_data.get('quotes', [])
                logging.info(f"Extracted {len(quotes)} quotes")
                
                # Show first few quotes
                for i, quote in enumerate(quotes[:3]):
                    logging.info(f"Quote {i+1}:")
                    logging.info(f"  Text: {quote.get('text', '')[:50]}...")
                    logging.info(f"  Author: {quote.get('author', 'Unknown')}")
                    logging.info(f"  Tags: {', '.join(quote.get('tags', []))}")
                
                return extracted_data
            except Exception as e:
                logging.error(f"Error during LLM extraction: {e}")
                return {"simulated": True, "title": "Famous Quotes"}
        else:
            logging.error(f"Failed to fetch {url}: {result.error}")
            return None
    except Exception as e:
        logging.error(f"Error during crawling: {e}")
        return None

async def multi_document_extraction():
    """Demonstrates extraction from multiple documents"""
    logging.info("\nEXAMPLE 5: Extraction from multiple documents")
    
    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        logging.warning("OpenAI API key not found in environment variables. Skipping LLM example.")
        logging.warning("Set OPENAI_API_KEY environment variable to run this example.")
        return [{"simulated": True}]
    
    # Create documents for extraction
    documents = [
        SAMPLE_HTML,
        SAMPLE_NEWS,
        """
        # Company Quarterly Report
        
        Q2 2023 Results
        
        Revenue: $5.2 million
        Profit: $1.8 million
        Growth: 15% YoY
        
        Main product line performance:
        - Software: $2.1M (up 20%)
        - Services: $1.8M (up 12%)
        - Hardware: $1.3M (up 10%)
        """
    ]
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    # Create a generic schema that can work for various document types
    generic_schema = {
        "document_type": "string",  # product, news, report, etc.
        "title": "string",
        "main_content_summary": "string",
        "key_facts": ["string"],
        "numerical_data": [{"label": "string", "value": "string"}]
    }
    
    # Create an LLM extractor
    extractor = LLMExtractor(
        schema=generic_schema,
        extraction_prompt="Extract key information from this document. First identify what type of document this is, then extract relevant information.",
        llm_config=llm_config
    )
    
    # Extract data from multiple documents
    try:
        results = await extractor.extract_all_async(documents)
        logging.info(f"Extracted data from {len(results)} documents")
        
        for i, result in enumerate(results):
            logging.info(f"Document {i+1} ({result.get('document_type', 'unknown')}):")
            logging.info(f"  Title: {result.get('title', 'Unknown')}")
            logging.info(f"  Summary: {result.get('main_content_summary', '')[:100]}...")
            
            numerical_data = result.get('numerical_data', [])
            if numerical_data:
                logging.info(f"  Numerical data:")
                for item in numerical_data[:3]:  # Show first few items
                    logging.info(f"    {item.get('label', '')}: {item.get('value', '')}")
        
        return results
    except Exception as e:
        logging.error(f"Error during extraction: {e}")
        return [{"simulated": True}]

async def main():
    """Run all LLM extraction examples"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("LLM-based Extraction Examples")
    logging.info("=" * 50)
    
    await basic_product_extraction()
    await news_article_extraction()
    await custom_provider_extraction()
    await real_website_extraction()
    await multi_document_extraction()
    
    logging.info("=" * 50)
    logging.info("Examples completed")

if __name__ == "__main__":
    asyncio.run(main()) 