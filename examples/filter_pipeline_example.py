#!/usr/bin/env python
"""
Filter Pipeline Example - Demonstrating how to combine multiple filters

This example demonstrates how to:
1. Create a filter pipeline combining multiple content filters
2. Apply filters in sequence to process content
3. Create complex filter combinations using different approaches
4. Modify pipelines dynamically at runtime
5. Create reusable filter chains for different purposes
"""

import logging
from typing import Dict, Any, List

from crawl4ai.processing.filters import (
    BasicContentFilter,
    LLMContentFilter,
    PruningRule,
    PruningContentFilter,
    FilterPipeline
)
from crawl4ai.config import LLMConfig
from crawl4ai.models import Page


# Sample data for demonstration
PRODUCT_DATA = {
    "title": "  Professional DSLR Camera with 24-70mm Lens Kit and Accessories  ",
    "description": "<p>This high-end <b>DSLR camera</b> features a 45MP full-frame sensor, 4K video recording capabilities, and comes with a versatile 24-70mm f/2.8 lens. Perfect for professional photographers!</p>",
    "price": "$2,599.99",
    "internal_id": "PROD-12345",
    "_source": "inventory_system",
    "specifications": {
        "sensor": "45MP Full-Frame CMOS",
        "processor": "DIGIC X",
        "iso_range": "100-51,200 (expandable to 50-102,400)",
        "shutter_speed": "1/8000 to 30 sec",
        "weight": "890g (body only)",
        "_internal_note": "New model replacing XC320"
    },
    "features": [
        "  45 megapixel full-frame sensor  ",
        "<li>4K video recording at 60fps</li>",
        "Weather-sealed body",
        "",  # Empty feature
        "Dual card slots"
    ],
    "tags": [
        "camera", "professional", "dslr", "full-frame", "photography", 
        "video", "4k", "high-resolution", "weather-sealed", "premium"
    ],
    "customer_review": "I've been using this camera for about 3 months now and I'm very satisfied with the purchase. The image quality is outstanding, especially in low light. The autofocus is fast and accurate. Battery life could be better though. My email is john.smith@example.com if anyone has questions.",
    "return_policy": "This product can be returned within 30 days of purchase for a full refund. Please keep all original packaging and accessories."
}


def main():
    """Run the filter pipeline examples."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("Filter Pipeline Examples")
    logging.info("=" * 50)
    
    # Example 1: Creating a basic filter pipeline
    logging.info("\nEXAMPLE 1: Creating a basic filter pipeline")
    
    # Create individual filters
    basic_filter = BasicContentFilter(
        remove_empty=True,
        strip_strings=True,
        strip_html=True
    )
    
    # Create pruning rules
    pruning_rules = [
        PruningRule(field_pattern=r"^_.*"),  # Remove fields starting with underscore
        PruningRule(field_pattern=r"internal_.*"),  # Remove internal fields
        PruningRule(field_pattern=r"tags", max_items=5)  # Limit tags to 5
    ]
    pruning_filter = PruningContentFilter(rules=pruning_rules, recursive=True)
    
    # Create a pipeline with these filters
    basic_pipeline = FilterPipeline([basic_filter, pruning_filter], name="Basic Pipeline")
    
    # Apply the pipeline
    basic_result = basic_pipeline.filter(PRODUCT_DATA)
    
    logging.info("Created pipeline: %s", basic_pipeline)
    logging.info("After basic pipeline processing:")
    logging.info("  - Original fields: %d", len(PRODUCT_DATA))
    logging.info("  - Processed fields: %d", len(basic_result))
    
    if "description" in basic_result:
        logging.info("  - Description (cleaned, HTML removed): '%s'", basic_result["description"])
    
    if "_source" not in basic_result:
        logging.info("  - Successfully removed fields starting with underscore")
    
    if "specifications" in basic_result and "_internal_note" not in basic_result["specifications"]:
        logging.info("  - Successfully removed nested fields starting with underscore")
    
    if "tags" in basic_result:
        logging.info("  - Tags limited to %d (from %d)", len(basic_result["tags"]), len(PRODUCT_DATA["tags"]))
    
    # Example 2: Creating a pipeline with factory methods
    logging.info("\nEXAMPLE 2: Creating a pipeline with factory methods")
    
    # Create a currency transform filter
    price_transform_filter = BasicContentFilter(
        transforms={
            "price": lambda x: float(x.replace("$", "").replace(",", "")) if isinstance(x, str) else x
        }
    )
    
    # Create using the from_filters factory method
    factory_pipeline = FilterPipeline.from_filters(
        basic_filter,
        pruning_filter,
        price_transform_filter,
        name="Factory Pipeline"
    )
    
    # Apply the pipeline
    factory_result = factory_pipeline.filter(PRODUCT_DATA)
    
    logging.info("Created pipeline: %s", factory_pipeline)
    logging.info("After factory pipeline processing:")
    if "price" in factory_result:
        logging.info("  - Price transformed: %s (%s)", 
                   factory_result["price"], type(factory_result["price"]).__name__)
    
    # Example 3: Using the + operator to combine pipelines
    logging.info("\nEXAMPLE 3: Using the + operator to combine pipelines")
    
    # Create separate pipelines for different purposes
    cleaning_pipeline = FilterPipeline([
        BasicContentFilter(remove_empty=True, strip_strings=True)
    ], name="Cleaning Pipeline")
    
    security_pipeline = FilterPipeline([
        PruningContentFilter(rules=[
            PruningRule(field_pattern=r".*email.*", custom_predicate=lambda f, v: isinstance(v, str) and "@" in v),
            PruningRule(field_pattern=r".*customer_review", max_length=100)  # Limit review length
        ])
    ], name="Security Pipeline")
    
    # Combine them using the + operator
    combined_pipeline = cleaning_pipeline + security_pipeline
    
    # Apply the combined pipeline
    combined_result = combined_pipeline.filter(PRODUCT_DATA)
    
    logging.info("Created combined pipeline: %s", combined_pipeline)
    logging.info("After combined pipeline processing:")
    
    if "customer_review" in combined_result:
        original_length = len(PRODUCT_DATA["customer_review"])
        processed_length = len(combined_result["customer_review"])
        logging.info("  - Review truncated: %d chars (from %d)", processed_length, original_length)
    
    # Example 4: Modifying pipelines at runtime
    logging.info("\nEXAMPLE 4: Modifying pipelines at runtime")
    
    # Start with a basic pipeline
    dynamic_pipeline = FilterPipeline([basic_filter], name="Dynamic Pipeline")
    logging.info("Initial pipeline: %s", dynamic_pipeline)
    
    # Add a new filter
    dynamic_pipeline.add_filter(pruning_filter)
    logging.info("After adding pruning filter: %s", dynamic_pipeline)
    
    # Create an LLM filter for enhancing the description
    try:
        # Skip LLM initialization if no API key is available
        llm_filter = LLMContentFilter(
            mode="enhance",
            fields=["description"],
            llm_config=LLMConfig(provider="openai", model="gpt-3.5-turbo")
        )
        dynamic_pipeline.add_filter(llm_filter)
        logging.info("After adding LLM filter: %s", dynamic_pipeline)
    except Exception as e:
        logging.warning("Skipped adding LLM filter due to: %s", e)
    
    # Remove a filter
    removed_filter = dynamic_pipeline.remove_filter(0)  # Remove the first filter
    if removed_filter:
        logging.info("Removed filter: %s", removed_filter.__class__.__name__)
    
    logging.info("Final pipeline: %s", dynamic_pipeline)
    
    # Example 5: Processing a Page object
    logging.info("\nEXAMPLE 5: Processing a Page object")
    
    # Create a simple Page object
    page = Page(
        url="https://example.com/products/dslr-camera",
        html=f"<html><body><div class='product'>{PRODUCT_DATA['description']}</div></body></html>",
        content_type="text/html",
        data=PRODUCT_DATA
    )
    
    # Create a processing pipeline
    page_pipeline = FilterPipeline([
        BasicContentFilter(strip_html=True, strip_strings=True),
        PruningContentFilter(rules=[
            PruningRule(field_pattern=r"^_.*"),
            PruningRule(field_pattern=r"internal_.*")
        ])
    ])
    
    # Process the page
    processed_page = page_pipeline.process_page(page)
    
    logging.info("Processed Page object:")
    logging.info("  - URL: %s", processed_page.url)
    logging.info("  - Original data fields: %d", len(PRODUCT_DATA))
    logging.info("  - Processed data fields: %d", len(processed_page.data))
    
    # Example 6: Creating reusable filter combinations
    logging.info("\nEXAMPLE 6: Creating reusable filter combinations")
    
    def create_ecommerce_pipeline() -> FilterPipeline:
        """Create a standard pipeline for e-commerce product data."""
        return FilterPipeline([
            # Basic cleaning
            BasicContentFilter(
                remove_empty=True,
                strip_strings=True,
                strip_html=True
            ),
            # Security and privacy
            PruningContentFilter(rules=[
                PruningRule(field_pattern=r"^_.*"),
                PruningRule(field_pattern=r"internal_.*"),
                PruningRule(field_pattern=r".*email.*", 
                           custom_predicate=lambda f, v: isinstance(v, str) and "@" in v)
            ]),
            # Transform price
            BasicContentFilter(
                transforms={
                    "price": lambda x: float(x.replace("$", "").replace(",", "")) 
                            if isinstance(x, str) else x
                }
            )
        ], name="E-commerce Standard Pipeline")
    
    # Create and use a reusable pipeline
    ecommerce_pipeline = create_ecommerce_pipeline()
    ecommerce_result = ecommerce_pipeline.filter(PRODUCT_DATA)
    
    logging.info("Using reusable e-commerce pipeline: %s", ecommerce_pipeline)
    logging.info("Processed fields: %s", list(ecommerce_result.keys()))
    logging.info("Processed price: %s (%s)", 
               ecommerce_result.get("price"), 
               type(ecommerce_result.get("price", "")).__name__)
    
    logging.info("\nExamples completed")


if __name__ == "__main__":
    main() 