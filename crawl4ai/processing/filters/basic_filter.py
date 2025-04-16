"""Basic content filter implementation for Crawl4AI.

This module provides a basic content filter implementation that handles
common content cleaning, validation, and transformation operations.
"""
from typing import Any, Dict, List, Optional, Union, Set, Callable

from crawl4ai.processing.filters.base_filter import BaseContentFilter


class BasicContentFilter(BaseContentFilter):
    """Basic content filter with common filtering operations.
    
    This filter handles typical content processing operations like:
    - Removing empty values
    - Stripping whitespace from string values
    - Excluding specified fields
    - Removing HTML tags from text
    - Normalizing field names
    - Transforming values with custom functions
    
    Example:
    ```python
    filter = BasicContentFilter(
        remove_empty=True,
        strip_strings=True,
        exclude_fields=["internal_id", "session_data"],
        strip_html=True
    )
    
    # Apply the filter
    clean_data = filter.filter(raw_data)
    ```
    """
    
    def __init__(
        self,
        remove_empty: bool = True,
        strip_strings: bool = True,
        exclude_fields: Optional[List[str]] = None,
        strip_html: bool = False,
        normalize_keys: bool = False,
        transforms: Optional[Dict[str, Callable]] = None,
        **kwargs
    ):
        """Initialize the basic content filter.
        
        Args:
            remove_empty: Whether to remove None, empty strings, lists, and dicts
            strip_strings: Whether to strip whitespace from string values
            exclude_fields: List of field names to exclude from the filtered content
            strip_html: Whether to remove HTML tags from string values
            normalize_keys: Whether to normalize field names (lowercase, replace spaces with _)
            transforms: Dictionary mapping field names to transform functions
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.remove_empty = remove_empty
        self.strip_strings = strip_strings
        self.exclude_fields = set(exclude_fields or [])
        self.strip_html = strip_html
        self.normalize_keys = normalize_keys
        self.transforms = transforms or {}
    
    def filter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply basic filtering to the content.
        
        Args:
            content: The content to filter
            
        Returns:
            The filtered content
        """
        if not content:
            return {}
        
        result = {}
        
        # Process each field
        for key, value in content.items():
            # Skip excluded fields
            if key in self.exclude_fields:
                continue
            
            # Normalize key if needed
            if self.normalize_keys:
                new_key = self._normalize_key(key)
            else:
                new_key = key
            
            # Process value
            processed_value = self._process_value(value)
            
            # Skip empty values if configured to do so
            if self.remove_empty and self._is_empty(processed_value):
                continue
            
            # Apply any field-specific transforms
            if new_key in self.transforms and callable(self.transforms[new_key]):
                processed_value = self.transforms[new_key](processed_value)
            
            # Add to result
            result[new_key] = processed_value
        
        return result
    
    def _process_value(self, value: Any) -> Any:
        """Process a single value based on filter settings.
        
        Args:
            value: The value to process
            
        Returns:
            The processed value
        """
        if isinstance(value, str):
            # Handle string processing
            processed = value
            
            # Strip HTML if configured
            if self.strip_html:
                processed = self._strip_html_tags(processed)
            
            # Strip whitespace if configured
            if self.strip_strings:
                processed = processed.strip()
            
            return processed
        
        elif isinstance(value, list):
            # Process list items
            return [self._process_value(item) for item in value if not self.remove_empty or not self._is_empty(item)]
        
        elif isinstance(value, dict):
            # Recursively process dictionary
            return self.filter(value)
        
        # Return other types as is
        return value
    
    def _is_empty(self, value: Any) -> bool:
        """Check if a value is considered empty.
        
        Args:
            value: The value to check
            
        Returns:
            True if the value is considered empty, False otherwise
        """
        if value is None:
            return True
        
        if isinstance(value, str) and not value.strip():
            return True
        
        if isinstance(value, (list, dict, set)) and not value:
            return True
        
        return False
    
    def _normalize_key(self, key: str) -> str:
        """Normalize a field name.
        
        Args:
            key: The field name to normalize
            
        Returns:
            The normalized field name
        """
        if not isinstance(key, str):
            return key
        
        # Convert to lowercase and replace spaces with underscores
        return key.lower().replace(' ', '_').replace('-', '_')
    
    def _strip_html_tags(self, text: str) -> str:
        """Remove HTML tags from a string.
        
        Args:
            text: The text to process
            
        Returns:
            Text with HTML tags removed
        """
        # Simple HTML tag removal, more complex cases might require BeautifulSoup
        import re
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Replace HTML entities
        entities = {
            '&nbsp;': ' ', '&lt;': '<', '&gt;': '>', '&amp;': '&',
            '&quot;': '"', '&apos;': "'"
        }
        
        for entity, replacement in entities.items():
            clean_text = clean_text.replace(entity, replacement)
        
        return clean_text 