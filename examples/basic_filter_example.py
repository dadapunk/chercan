#!/usr/bin/env python
"""
Basic Content Filter Example - Demonstrating how to use content filters

This example demonstrates how to:
1. Use the BasicContentFilter to clean and transform extracted data
2. Configure different filtering options
3. Apply filters to dictionaries and Page objects
4. Create custom transformation functions for specific fields
5. Use filters in a data processing pipeline
"""

import asyncio
import logging
from typing import Dict, Any

from crawl4ai.processing.filters import BaseContentFilter, BasicContentFilter
from crawl4ai.models import Page


# Sample data for demonstration
MESSY_DATA = {
    "title": "  Product Title with Extra Spaces  ",
    "description": "<p>This is a <b>product description</b> with HTML tags</p>",
    "price": "$129.99",
    "empty_field": "",
    "null_field": None,
    "empty_list": [],
    "features": [
        "  Feature 1  ",
        "<li>Feature 2 with HTML</li>",
        ""  # Empty feature
    ],
    "metadata": {
        "internal_id": "INT12345",
        "source": "web-scraper",
        "timestamp": "2023-04-01T12:34:56"
    },
    "UPPERCASE_FIELD": "This field has an uppercase name",
    "field with spaces": "This field name has spaces"
}


def currency_to_float(value: str) -> float:
    """Convert currency string to float.
    
    Args:
        value: Currency string (e.g., "$129.99")
        
    Returns:
        Float value
    """
    if not isinstance(value, str):
        return value
    
    # Remove currency symbols and commas, then convert to float
    clean_value = value.replace('$', '').replace('€', '').replace('£', '').replace(',', '')
    try:
        return float(clean_value)
    except ValueError:
        return value


def main():
    """Run the basic content filter examples."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("Basic Content Filter Examples")
    logging.info("=" * 50)
    
    # Example 1: Basic filtering with default settings
    logging.info("\nEXAMPLE 1: Basic filtering with default settings")
    basic_filter = BasicContentFilter()
    filtered_data = basic_filter.filter(MESSY_DATA)
    
    logging.info("Original data:")
    logging.info(f"  Fields: {list(MESSY_DATA.keys())}")
    logging.info(f"  Number of fields: {len(MESSY_DATA)}")
    
    logging.info("\nFiltered data (default settings - removes empty values):")
    logging.info(f"  Fields: {list(filtered_data.keys())}")
    logging.info(f"  Number of fields: {len(filtered_data)}")
    logging.info(f"  Title: '{filtered_data.get('title')}'")  # Note spaces are stripped
    logging.info(f"  Features: {filtered_data.get('features')}")  # Empty feature is removed
    
    # Example 2: Configure filter settings
    logging.info("\nEXAMPLE 2: Configure filter settings")
    configured_filter = BasicContentFilter(
        remove_empty=True,
        strip_strings=True,
        exclude_fields=["internal_id", "source"],
        strip_html=True,
        normalize_keys=True
    )
    
    filtered_data = configured_filter.filter(MESSY_DATA)
    
    logging.info("Filtered data with custom settings:")
    logging.info(f"  Fields: {list(filtered_data.keys())}")
    logging.info(f"  Description: '{filtered_data.get('description')}'")  # HTML tags removed
    logging.info(f"  Uppercase field: '{filtered_data.get('uppercase_field')}'")  # Normalized to lowercase
    logging.info(f"  Field with spaces: '{filtered_data.get('field_with_spaces')}'")  # Spaces replaced with _
    
    # Metadata is preserved but internal_id and source are removed from it
    if 'metadata' in filtered_data:
        logging.info(f"  Metadata fields: {list(filtered_data['metadata'].keys())}")
    
    # Example 3: Using custom transform functions
    logging.info("\nEXAMPLE 3: Using custom transform functions")
    transform_filter = BasicContentFilter(
        strip_strings=True,
        strip_html=True,
        transforms={
            "price": currency_to_float
        }
    )
    
    transformed_data = transform_filter.filter(MESSY_DATA)
    
    logging.info("Transformed data:")
    price = transformed_data.get('price')
    logging.info(f"  Price (original): '{MESSY_DATA.get('price')}'")
    logging.info(f"  Price (transformed): {price} ({type(price).__name__})")
    
    # Example 4: Processing a Page object
    logging.info("\nEXAMPLE 4: Processing a Page object")
    
    # Create a simple Page object (mocked for the example)
    page = Page(
        url="https://example.com/product",
        html="<html><body><h1>Product Page</h1></body></html>",
        content_type="text/html",
        data=MESSY_DATA
    )
    
    # Process the page
    page_filter = BasicContentFilter(
        strip_strings=True,
        strip_html=True,
        normalize_keys=True
    )
    
    processed_page = page_filter.process_page(page)
    
    logging.info("Processed Page object:")
    logging.info(f"  URL: {processed_page.url}")
    logging.info(f"  Data fields: {list(processed_page.data.keys())}")
    
    # Example 5: Chaining multiple filters
    logging.info("\nEXAMPLE 5: Chaining multiple filters")
    
    # First filter: basic cleaning
    first_filter = BasicContentFilter(
        remove_empty=True,
        strip_strings=True,
        strip_html=True
    )
    
    # Second filter: transform specific fields
    second_filter = BasicContentFilter(
        transforms={
            "price": currency_to_float
        }
    )
    
    # Third filter: normalize and exclude fields
    third_filter = BasicContentFilter(
        normalize_keys=True,
        exclude_fields=["metadata"]
    )
    
    # Apply filters in sequence
    intermediate_data = first_filter.filter(MESSY_DATA)
    intermediate_data = second_filter.filter(intermediate_data)
    final_data = third_filter.filter(intermediate_data)
    
    logging.info("Data after multiple filters:")
    logging.info(f"  Fields: {list(final_data.keys())}")
    logging.info(f"  Price: {final_data.get('price')}")
    logging.info(f"  'metadata' field present: {'metadata' in final_data}")
    
    logging.info("\nExamples completed")


if __name__ == "__main__":
    main() 