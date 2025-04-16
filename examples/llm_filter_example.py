#!/usr/bin/env python
"""
LLM Content Filter Example - Demonstrating how to use LLM for filtering content

This example demonstrates how to:
1. Configure and use the LLMContentFilter for different processing tasks
2. Use different LLM providers (OpenAI, Anthropic, etc.)
3. Process various types of content with LLMs
4. Implement custom prompt templates
5. Apply LLM filters asynchronously for better performance
"""

import asyncio
import logging
import os
from typing import Dict, Any

from crawl4ai.processing.filters import LLMContentFilter
from crawl4ai.config import LLMConfig
from crawl4ai.models import Page


# Sample data for demonstration
PRODUCT_DATA = {
    "title": "Professional DSLR Camera with 24-70mm Lens",
    "description": "This high-end DSLR camera features a 45MP full-frame sensor, 4K video recording capabilities, and comes with a versatile 24-70mm f/2.8 lens. Perfect for professional photographers and videographers looking for exceptional image quality and performance.",
    "features": [
        "45 megapixel full-frame sensor",
        "4K video recording at 60fps",
        "Weather-sealed body",
        "Dual card slots",
        "3.2-inch touchscreen LCD"
    ],
    "customer_review": "I've been using this camera for about 3 months now and I'm very satisfied with the purchase. The image quality is outstanding, especially in low light. The autofocus is fast and accurate. Battery life could be better though. I bought this to replace my old Canon 5D Mark III and the improvement is significant. My email is john.smith@example.com if anyone has questions.",
    "technical_specs": {
        "sensor": "45MP Full-Frame CMOS",
        "processor": "DIGIC X",
        "iso_range": "100-51,200 (expandable to 50-102,400)",
        "shutter_speed": "1/8000 to 30 sec",
        "weight": "890g (body only)"
    }
}

NEWS_ARTICLE = """
In a significant technological breakthrough announced today, researchers at MIT have developed a new type of battery that can charge in under 5 minutes and last for days on a single charge. The team, led by Dr. Sarah Johnson, published their findings in the journal Nature Energy.

"This is a game-changer for electric vehicles and mobile devices," said Dr. Johnson. "The new battery technology uses a novel composite material that allows for much faster ion transfer while maintaining stability."

The research was funded by a $10 million grant from the Department of Energy and involved collaboration with teams from Stanford University and the National Renewable Energy Laboratory.

Industry experts predict the technology could reach consumer products within 3-5 years, potentially revolutionizing everything from smartphones to electric vehicles. Tesla, Apple, and Samsung have already expressed interest in licensing the technology.

For more information, contact the MIT press office at press@mit.edu or call (617) 555-1234.
"""


async def basic_llm_filter_example():
    """Demonstrates basic usage of the LLMContentFilter."""
    logging.info("\nEXAMPLE 1: Basic LLM content filtering")
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",  # Using OpenAI by default
        model="gpt-3.5-turbo",
        temperature=0.1  # Low temperature for more deterministic results
    )
    
    # Create a filter for summarizing content
    summarize_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="summarize",
        fields=["description"],
        max_length=50
    )
    
    # Apply the filter to product data
    filtered_data = summarize_filter.filter(PRODUCT_DATA)
    
    logging.info("Original description:")
    logging.info(f"  Length: {len(PRODUCT_DATA['description'])} characters")
    logging.info(f"  Content: '{PRODUCT_DATA['description']}'")
    
    logging.info("\nSummarized description:")
    logging.info(f"  Length: {len(filtered_data['description'])} characters")
    logging.info(f"  Content: '{filtered_data['description']}'")
    
    return filtered_data


async def multiple_modes_example():
    """Demonstrates different filtering modes."""
    logging.info("\nEXAMPLE 2: Different filtering modes")
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    # Create filters with different modes
    pii_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="remove_pii",
        fields=["customer_review"]
    )
    
    enhance_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="enhance",
        fields=["title"]
    )
    
    categorize_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="categorize",
        fields=["description"],
        categories=["Photography", "Electronics", "Professional Equipment", "Consumer Goods"]
    )
    
    # Apply the PII filter
    pii_result = pii_filter.filter(PRODUCT_DATA)
    logging.info("PII Removal:")
    logging.info(f"  Original: '{PRODUCT_DATA['customer_review'][:100]}...'")
    logging.info(f"  Filtered: '{pii_result['customer_review'][:100]}...'")
    
    # Apply the enhance filter
    enhance_result = enhance_filter.filter(PRODUCT_DATA)
    logging.info("\nTitle Enhancement:")
    logging.info(f"  Original: '{PRODUCT_DATA['title']}'")
    logging.info(f"  Enhanced: '{enhance_result['title']}'")
    
    # Apply the categorize filter
    categorize_result = categorize_filter.filter(PRODUCT_DATA)
    logging.info("\nCategorization:")
    logging.info(f"  Category: '{categorize_result['description']}'")
    
    return {
        "pii_removed": pii_result['customer_review'],
        "enhanced_title": enhance_result['title'],
        "category": categorize_result['description']
    }


async def custom_prompt_example():
    """Demonstrates using custom prompt templates."""
    logging.info("\nEXAMPLE 3: Custom prompt templates")
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.3
    )
    
    # Custom prompt for extracting key specifications
    custom_prompt_template = """
    Extract the 3 most important technical specifications from the following {field}:
    
    {text}
    
    Format the output as a bulleted list with only the 3 most important specs.
    """
    
    # Create a filter with the custom prompt
    custom_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="custom",
        fields=["technical_specs"],
        prompt_template=custom_prompt_template
    )
    
    # Apply the custom filter
    result = custom_filter.filter(PRODUCT_DATA)
    
    logging.info("Custom filter result:")
    if isinstance(result.get('technical_specs'), str):
        # If the result is a string (LLM output)
        logging.info(f"  Extracted specs:\n{result['technical_specs']}")
    else:
        # If the structure was preserved (e.g., still a dict)
        logging.info(f"  Result: {result['technical_specs']}")
    
    return result


async def async_processing_example():
    """Demonstrates asynchronous processing of multiple fields."""
    logging.info("\nEXAMPLE 4: Asynchronous processing")
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    # Create a filter with async processing enabled
    async_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="summarize",
        fields=["description", "customer_review", "technical_specs"],
        max_length=30,
        async_processing=True  # Enable async processing
    )
    
    # Apply the filter
    start_time = asyncio.get_event_loop().time()
    result = await async_filter._process_fields_async(
        PRODUCT_DATA, 
        {"description", "customer_review"}
    )
    end_time = asyncio.get_event_loop().time()
    
    logging.info(f"Async processing completed in {end_time - start_time:.2f} seconds")
    logging.info("Results:")
    logging.info(f"  Description: '{result['description']}'")
    logging.info(f"  Review: '{result['customer_review']}'")
    
    return result


async def news_article_example():
    """Demonstrates processing a news article."""
    logging.info("\nEXAMPLE 5: Processing a news article")
    
    # Create a Page object with the news article
    page = Page(
        url="https://example.com/news/new-battery-technology",
        html=f"<html><body><article>{NEWS_ARTICLE}</article></body></html>",
        content_type="text/html",
        data={"content": NEWS_ARTICLE, "source": "Example News"}
    )
    
    # Create an LLM configuration
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    # Create multiple filters for different tasks
    summarize_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="summarize",
        fields=["content"],
        max_length=50
    )
    
    pii_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="remove_pii",
        fields=["content"]
    )
    
    # Apply filters in sequence
    summarized_page = summarize_filter.process_page(page)
    anonymized_page = pii_filter.process_page(summarized_page)
    
    logging.info("Original article length: %d characters", len(NEWS_ARTICLE))
    logging.info("Summarized article length: %d characters", 
                len(summarized_page.data.get('content', '')))
    
    logging.info("\nSummarized and anonymized content:")
    logging.info(anonymized_page.data.get('content', ''))
    
    return anonymized_page.data


async def main():
    """Run all LLM content filter examples."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("LLM Content Filter Examples")
    logging.info("=" * 50)
    
    # Specify API key for examples
    if not os.environ.get('OPENAI_API_KEY'):
        logging.warning("OPENAI_API_KEY environment variable not set.")
        logging.warning("Set this variable to run the examples with actual API calls.")
        logging.warning("For now, examples will run in simulation mode.")
        logging.warning("=" * 50)
    
    try:
        await basic_llm_filter_example()
        await multiple_modes_example()
        await custom_prompt_example()
        await async_processing_example()
        await news_article_example()
    except Exception as e:
        logging.error(f"Error during examples: {e}")
    
    logging.info("=" * 50)
    logging.info("Examples completed")


if __name__ == "__main__":
    asyncio.run(main()) 