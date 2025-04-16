"""Pruning content filter for Crawl4AI.

This module provides a content filter that selectively prunes or removes content
based on configurable rules and criteria.
"""
from typing import Any, Dict, List, Optional, Union, Set, Pattern, Callable
import re

from crawl4ai.processing.filters.base_filter import BaseContentFilter


class PruningRule:
    """A rule for pruning content.
    
    The rule specifies conditions for when content should be pruned or removed.
    
    Attributes:
        field_pattern: Regular expression pattern to match field names
        value_pattern: Optional pattern to match field values
        min_length: Optional minimum length for text content
        max_length: Optional maximum length for text content
        min_items: Optional minimum items for lists
        max_items: Optional maximum items for lists
        custom_predicate: Optional custom function to determine pruning
    """
    
    def __init__(
        self,
        field_pattern: str,
        value_pattern: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        custom_predicate: Optional[Callable[[str, Any], bool]] = None
    ):
        """Initialize a pruning rule.
        
        Args:
            field_pattern: Regular expression pattern to match field names
            value_pattern: Optional pattern to match field values
            min_length: Optional minimum length for text content
            max_length: Optional maximum length for text content
            min_items: Optional minimum items for lists
            max_items: Optional maximum items for lists
            custom_predicate: Optional custom function that takes field name and value
                and returns True if the field should be pruned
        """
        self.field_regex = re.compile(field_pattern)
        self.value_regex = re.compile(value_pattern) if value_pattern else None
        self.min_length = min_length
        self.max_length = max_length
        self.min_items = min_items
        self.max_items = max_items
        self.custom_predicate = custom_predicate
    
    def matches_field(self, field_name: str) -> bool:
        """Check if a field name matches this rule.
        
        Args:
            field_name: The field name to check
            
        Returns:
            True if the field name matches the rule's pattern
        """
        return bool(self.field_regex.search(field_name))
    
    def should_prune(self, field_name: str, value: Any) -> bool:
        """Determine if a field should be pruned based on this rule.
        
        Args:
            field_name: The name of the field
            value: The value of the field
            
        Returns:
            True if the field should be pruned
        """
        # Check custom predicate first if provided
        if self.custom_predicate and callable(self.custom_predicate):
            if self.custom_predicate(field_name, value):
                return True
        
        # Check value pattern if specified
        if self.value_regex and isinstance(value, str):
            if self.value_regex.search(value):
                return True
        
        # Check length constraints for strings
        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                return True
            if self.max_length is not None and len(value) > self.max_length:
                return True
        
        # Check length constraints for lists
        if isinstance(value, list):
            if self.min_items is not None and len(value) < self.min_items:
                return True
            if self.max_items is not None and len(value) > self.max_items:
                return True
        
        # Don't prune by default
        return False


class PruningContentFilter(BaseContentFilter):
    """Content filter that prunes content based on rules.
    
    This filter allows selectively removing content that matches specified rules.
    It can be used to:
    - Remove fields with specific patterns
    - Limit content length or list size
    - Clean up data based on custom predicates
    
    Example:
    ```python
    # Create rules
    rules = [
        PruningRule(field_pattern=r"^_.*", value_pattern=None),  # Remove fields starting with _
        PruningRule(field_pattern=r"description", max_length=500),  # Limit description length
        PruningRule(field_pattern=r"tags", max_items=10),  # Limit tags to 10 items
    ]
    
    # Create filter
    pruning_filter = PruningContentFilter(rules=rules)
    
    # Apply the filter
    cleaned_data = pruning_filter.filter(raw_data)
    ```
    """
    
    def __init__(
        self,
        rules: Optional[List[PruningRule]] = None,
        prune_empty: bool = True,
        recursive: bool = True,
        **kwargs
    ):
        """Initialize the pruning content filter.
        
        Args:
            rules: List of pruning rules to apply
            prune_empty: Whether to automatically prune None, empty strings, lists, and dicts
            recursive: Whether to recursively process nested dictionaries
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.rules = rules or []
        self.prune_empty = prune_empty
        self.recursive = recursive
    
    def filter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pruning to the content.
        
        Args:
            content: The content to filter
            
        Returns:
            The filtered content with pruned fields removed
        """
        if not content:
            return {}
        
        result = {}
        
        # Process each field
        for field, value in content.items():
            # Skip if the field should be pruned
            if self._should_prune_field(field, value):
                continue
            
            # Process nested dictionaries recursively if configured
            if self.recursive and isinstance(value, dict):
                processed_value = self.filter(value)
                # Skip empty dictionaries if configured to prune empty
                if not processed_value and self.prune_empty:
                    continue
                result[field] = processed_value
            # Process lists recursively if configured and they contain dictionaries
            elif self.recursive and isinstance(value, list) and value and isinstance(value[0], dict):
                processed_items = []
                for item in value:
                    if isinstance(item, dict):
                        processed_item = self.filter(item)
                        if processed_item or not self.prune_empty:
                            processed_items.append(processed_item)
                    else:
                        processed_items.append(item)
                # Skip empty lists if configured to prune empty
                if not processed_items and self.prune_empty:
                    continue
                result[field] = processed_items
            else:
                # Keep the field as is
                result[field] = value
        
        return result
    
    def _should_prune_field(self, field_name: str, value: Any) -> bool:
        """Determine if a field should be pruned based on the rules.
        
        Args:
            field_name: The name of the field
            value: The value of the field
            
        Returns:
            True if the field should be pruned
        """
        # Check if the value is empty and we're configured to prune empty values
        if self.prune_empty and self._is_empty(value):
            return True
        
        # Check against each rule
        for rule in self.rules:
            if rule.matches_field(field_name) and rule.should_prune(field_name, value):
                return True
        
        # Don't prune by default
        return False
    
    def _is_empty(self, value: Any) -> bool:
        """Check if a value is considered empty.
        
        Args:
            value: The value to check
            
        Returns:
            True if the value is considered empty
        """
        if value is None:
            return True
        
        if isinstance(value, str) and not value.strip():
            return True
        
        if isinstance(value, (list, dict, set)) and not value:
            return True
        
        return False
    
    def add_rule(self, rule: PruningRule) -> None:
        """Add a pruning rule to the filter.
        
        Args:
            rule: The pruning rule to add
        """
        self.rules.append(rule)
    
    def add_field_pattern_rule(
        self,
        field_pattern: str,
        **kwargs
    ) -> None:
        """Add a new rule based on a field pattern.
        
        Args:
            field_pattern: Regular expression pattern to match field names
            **kwargs: Additional rule parameters (value_pattern, min_length, etc.)
        """
        rule = PruningRule(field_pattern=field_pattern, **kwargs)
        self.add_rule(rule)
    
    def add_length_limit_rule(
        self,
        field_pattern: str,
        max_length: int
    ) -> None:
        """Add a rule to limit text field length.
        
        Args:
            field_pattern: Regular expression pattern to match field names
            max_length: Maximum allowed length for matching fields
        """
        rule = PruningRule(field_pattern=field_pattern, max_length=max_length)
        self.add_rule(rule)
    
    def add_list_limit_rule(
        self,
        field_pattern: str,
        max_items: int
    ) -> None:
        """Add a rule to limit list item count.
        
        Args:
            field_pattern: Regular expression pattern to match field names
            max_items: Maximum allowed items for matching lists
        """
        rule = PruningRule(field_pattern=field_pattern, max_items=max_items)
        self.add_rule(rule) 