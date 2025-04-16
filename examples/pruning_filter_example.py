#!/usr/bin/env python
"""
Pruning Content Filter Example - Demonstrating how to selectively remove content

This example demonstrates how to:
1. Create and configure pruning rules
2. Apply rules to selectively prune content based on patterns
3. Limit field lengths and list sizes
4. Use custom predicates for complex pruning logic
5. Apply pruning recursively to nested data structures
"""

import logging
from typing import Dict, Any

from crawl4ai.processing.filters import PruningRule, PruningContentFilter


# Sample data for demonstration with nested structures and various field types
MESSY_DATA = {
    "title": "Product with Extremely Long Title That Exceeds Our Desired Length Limitations and Contains Too Much Information",
    "description": "This is a product description with acceptable length.",
    "price": "$129.99",
    "internal_id": "INT12345",  # Internal field we might want to remove
    "_private_data": "This shouldn't be included in output",  # Private field to remove
    "tags": [
        "electronics", "computers", "laptops", "gaming", 
        "high-performance", "SSD", "16GB RAM", "gaming laptop",
        "RGB keyboard", "thin", "lightweight", "portable",  # Too many tags
    ],
    "specifications": {
        "processor": "Intel Core i7-11800H",
        "memory": "16GB DDR4",
        "storage": "1TB NVMe SSD",
        "display": "15.6-inch Full HD IPS",
        "graphics": "NVIDIA GeForce RTX 3060",
        "internal_notes": "Sourced from manufacturer XYZ",  # Internal field in nested dict
        "test_results": {
            "benchmark": "Passed all tests",
            "_debug_info": "Test run on server 12",  # Nested private field
        }
    },
    "reviews": [
        {
            "user": "John",
            "rating": 5,
            "comment": "Excellent product, exceeded my expectations. The performance is outstanding for gaming and professional work. Battery life is decent for a gaming laptop.",
            "verified_purchase": True,
            "helpful_votes": 12,
            "user_id": "U12345"  # User ID we might want to remove for privacy
        },
        {
            "user": "Sarah",
            "rating": 4,
            "comment": "Good laptop, but runs a bit hot when gaming.",
            "verified_purchase": True,
            "helpful_votes": 8,
            "user_id": "U54321"
        },
        {
            "user": "",  # Empty username that should be pruned
            "rating": 3,
            "comment": "",  # Empty comment that should be pruned
            "verified_purchase": False,
            "helpful_votes": 0,
            "user_id": "U99999"
        }
    ],
    "empty_field": "",
    "null_field": None,
    "empty_list": [],
    "empty_dict": {}
}


def is_sensitive_field(field_name: str, value: Any) -> bool:
    """Custom predicate to identify sensitive fields.
    
    Args:
        field_name: The name of the field
        value: The value of the field
        
    Returns:
        True if the field is considered sensitive
    """
    sensitive_patterns = ["id", "password", "key", "token", "secret"]
    return any(pattern in field_name.lower() for pattern in sensitive_patterns)


def main():
    """Run the pruning content filter examples."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logging.info("Pruning Content Filter Examples")
    logging.info("=" * 50)
    
    # Example 1: Basic pruning with default settings
    logging.info("\nEXAMPLE 1: Basic pruning (removing empty values)")
    
    # Create a filter with default settings (will prune empty values)
    basic_filter = PruningContentFilter()
    pruned_data = basic_filter.filter(MESSY_DATA)
    
    logging.info("Original data fields: %d", len(MESSY_DATA))
    logging.info("After basic pruning: %d", len(pruned_data))
    
    # List fields that were removed
    removed_fields = set(MESSY_DATA.keys()) - set(pruned_data.keys())
    logging.info("Removed fields: %s", list(removed_fields))
    
    # Example 2: Pruning with pattern rules
    logging.info("\nEXAMPLE 2: Pruning with pattern rules")
    
    # Create rules
    rules = [
        PruningRule(field_pattern=r"^_.*"),  # Fields starting with underscore
        PruningRule(field_pattern=r"internal_.*"),  # Fields starting with "internal_"
        PruningRule(field_pattern=r"title", max_length=50),  # Limit title length
        PruningRule(field_pattern=r"tags", max_items=5),  # Limit number of tags
    ]
    
    pattern_filter = PruningContentFilter(rules=rules)
    pattern_result = pattern_filter.filter(MESSY_DATA)
    
    logging.info("Pattern rules applied:")
    if "_private_data" not in pattern_result:
        logging.info("  - Successfully removed fields starting with underscore")
    
    if "internal_id" not in pattern_result:
        logging.info("  - Successfully removed fields starting with 'internal_'")
    
    if "title" in pattern_result:
        logging.info("  - Title length: %d (original: %d)", 
                    len(pattern_result["title"]), len(MESSY_DATA["title"]))
    
    if "tags" in pattern_result:
        logging.info("  - Tags count: %d (original: %d)", 
                    len(pattern_result["tags"]), len(MESSY_DATA["tags"]))
    
    # Example 3: Custom predicates
    logging.info("\nEXAMPLE 3: Using custom predicates")
    
    # Create a rule with a custom predicate
    sensitive_rule = PruningRule(
        field_pattern=r".*",  # Match any field name
        custom_predicate=is_sensitive_field  # Use our custom function
    )
    
    custom_filter = PruningContentFilter(rules=[sensitive_rule])
    custom_result = custom_filter.filter(MESSY_DATA)
    
    logging.info("Fields after removing sensitive data:")
    
    # Check if sensitive fields were removed from reviews
    if "reviews" in custom_result:
        first_review = custom_result["reviews"][0]
        if "user_id" not in first_review:
            logging.info("  - Successfully removed user_id fields")
    
    # Example 4: Recursive pruning in nested structures
    logging.info("\nEXAMPLE 4: Recursive pruning in nested structures")
    
    # Create rules targeting nested structures
    nested_rules = [
        PruningRule(field_pattern=r"^_.*"),  # Private fields
        PruningRule(field_pattern=r"internal_.*"),  # Internal fields
        PruningRule(field_pattern=r"comment", max_length=50)  # Limit comment length
    ]
    
    recursive_filter = PruningContentFilter(rules=nested_rules, recursive=True)
    recursive_result = recursive_filter.filter(MESSY_DATA)
    
    # Check nested structures
    if "specifications" in recursive_result:
        if "internal_notes" not in recursive_result["specifications"]:
            logging.info("  - Successfully pruned internal_notes in nested specifications")
        
        if "test_results" in recursive_result["specifications"]:
            if "_debug_info" not in recursive_result["specifications"]["test_results"]:
                logging.info("  - Successfully pruned _debug_info in deeply nested structure")
    
    # Check if review comments were shortened
    if "reviews" in recursive_result and recursive_result["reviews"]:
        original_comment = MESSY_DATA["reviews"][0]["comment"]
        pruned_comment = recursive_result["reviews"][0]["comment"]
        
        if len(pruned_comment) < len(original_comment):
            logging.info("  - Successfully limited comment length:")
            logging.info("    Original: %d chars, Pruned: %d chars", 
                        len(original_comment), len(pruned_comment))
    
    # Example 5: Adding rules incrementally
    logging.info("\nEXAMPLE 5: Adding rules incrementally")
    
    # Create an empty filter
    incremental_filter = PruningContentFilter(rules=[])
    
    # Add rules one by one
    incremental_filter.add_field_pattern_rule(r"^_.*")  # Private fields
    incremental_filter.add_length_limit_rule(r"title", 30)  # Shorter title
    incremental_filter.add_list_limit_rule(r"tags", 3)  # Fewer tags
    
    # Add a custom rule
    incremental_filter.add_rule(PruningRule(
        field_pattern=r"reviews",
        max_items=1  # Keep only one review
    ))
    
    incremental_result = incremental_filter.filter(MESSY_DATA)
    
    logging.info("Results after incremental rule addition:")
    if "title" in incremental_result:
        logging.info("  - Title: '%s'", incremental_result["title"])
    
    if "tags" in incremental_result:
        logging.info("  - Tags (%d): %s", len(incremental_result["tags"]), 
                   incremental_result["tags"])
    
    if "reviews" in incremental_result:
        logging.info("  - Reviews count: %d", len(incremental_result["reviews"]))
    
    logging.info("\nExamples completed")


if __name__ == "__main__":
    main() 