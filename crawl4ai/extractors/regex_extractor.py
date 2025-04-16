"""RegEx-based extractor for Crawl4AI.

This module provides an extractor that uses regular expressions to extract
structured data from text content.
"""
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Pattern
import re
import json

from crawl4ai.models import Page
from crawl4ai.extractors.base_extractor import BaseExtractor


T = TypeVar('T')


class RegExExtractor(BaseExtractor):
    """Extract data from content using regular expressions.
    
    This extractor allows defining a mapping of field names to regex patterns
    and optional transform functions to extract and process data.
    
    Example:
    ```python
    extractor = RegExExtractor({
        "title": r"<title>(.+?)</title>",
        "price": {
            "pattern": r"Price: \$(\d+\.\d+)",
            "transform": float
        },
        "tags": {
            "pattern": r"<tag>(.+?)</tag>",
            "multiple": True
        }
    })
    
    data = extractor.extract(html_content)
    # {
    #   "title": "Product Name",
    #   "price": 99.99,
    #   "tags": ["electronics", "laptop", "gaming"]
    # }
    ```
    """
    
    def __init__(
        self,
        patterns: Dict[str, Union[str, Dict[str, Any]]] = None,
        flags: int = re.DOTALL,
        use_named_groups: bool = False
    ):
        """Initialize the RegEx extractor.
        
        Args:
            patterns: Dictionary mapping field names to regex patterns or pattern configs
            flags: Regex flags to apply to all patterns
            use_named_groups: Whether to use named groups instead of indexed groups
        """
        self.patterns = patterns or {}
        self.flags = flags
        self.use_named_groups = use_named_groups
        self._compiled_patterns = {}
        
        # Compile patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile all regex patterns for better performance."""
        for field, pattern_config in self.patterns.items():
            if isinstance(pattern_config, str):
                pattern = pattern_config
                self._compiled_patterns[field] = re.compile(pattern, self.flags)
            else:
                pattern = pattern_config["pattern"]
                self._compiled_patterns[field] = re.compile(pattern, self.flags)
    
    def extract(self, content: Union[str, Page]) -> Dict[str, Any]:
        """Extract data from content using regex patterns.
        
        Args:
            content: Content to extract data from, either a string or a Page object
            
        Returns:
            A dictionary containing the extracted data
        """
        # Handle case when content is a Page object
        if hasattr(content, 'content') and not isinstance(content, str):
            content_str = getattr(content, 'content')
        # Handle case when content is a Page object with html property 
        elif hasattr(content, 'html') and not isinstance(content, str):
            content_str = getattr(content, 'html')
        # Otherwise, assume it's a string
        else:
            content_str = content
            
        if not content_str:
            return {}
        
        return self._extract_from_string(content_str)
    
    def _extract_from_string(self, content: str) -> Dict[str, Any]:
        """Extract data from a string using regex patterns.
        
        Args:
            content: String content to extract data from
            
        Returns:
            A dictionary containing the extracted data
        """
        result = {}
        
        for field, pattern_config in self.patterns.items():
            # Handle string pattern
            if isinstance(pattern_config, str):
                pattern = self._compiled_patterns[field]
                transform = None
                multiple = False
                default = None
            # Handle pattern config dictionary
            else:
                pattern = self._compiled_patterns[field]
                transform = pattern_config.get('transform')
                multiple = pattern_config.get('multiple', False)
                default = pattern_config.get('default')
            
            # Extract data using regex
            if multiple:
                matches = pattern.findall(content)
                if not matches and default is not None:
                    result[field] = default
                    continue
                
                # Handle different types of matches
                extracted_values = []
                for match in matches:
                    value = self._process_match(match)
                    if transform:
                        try:
                            value = transform(value)
                        except Exception:
                            pass
                    extracted_values.append(value)
                
                result[field] = extracted_values
            else:
                match = pattern.search(content)
                if not match:
                    result[field] = default
                    continue
                
                value = self._process_match(match)
                if transform:
                    try:
                        value = transform(value)
                    except Exception:
                        pass
                
                result[field] = value
        
        return result
    
    def _process_match(self, match: Union[re.Match, Any]) -> Any:
        """Process a regex match object.
        
        Args:
            match: The match object or value to process
            
        Returns:
            The extracted value
        """
        # If it's not a match object, return it as is
        if not isinstance(match, re.Match):
            return match
        
        # If using named groups, return a dictionary of all named groups
        if self.use_named_groups:
            named_groups = match.groupdict()
            if named_groups:
                return named_groups
        
        # If there are groups, return the first group
        groups = match.groups()
        if groups:
            if len(groups) == 1:
                return groups[0]
            return groups
        
        # Otherwise, return the full match
        return match.group(0)
    
    def extract_all(self, contents: List[Union[str, Page]]) -> List[Dict[str, Any]]:
        """Extract data from multiple contents.
        
        Args:
            contents: List of content strings or Page objects
            
        Returns:
            A list of dictionaries containing the extracted data
        """
        return [self.extract(content) for content in contents]
    
    def add_pattern(
        self,
        field: str,
        pattern: Union[str, Dict[str, Any]]
    ) -> None:
        """Add a pattern to the extractor.
        
        Args:
            field: Field name for the extracted data
            pattern: Regex pattern or pattern config dictionary
        """
        self.patterns[field] = pattern
        
        # Compile the new pattern
        if isinstance(pattern, str):
            self._compiled_patterns[field] = re.compile(pattern, self.flags)
        else:
            self._compiled_patterns[field] = re.compile(pattern["pattern"], self.flags)
    
    def remove_pattern(self, field: str) -> None:
        """Remove a pattern from the extractor.
        
        Args:
            field: Field name to remove
        """
        if field in self.patterns:
            del self.patterns[field]
            del self._compiled_patterns[field]
    
    def to_json(self) -> str:
        """Convert the extractor configuration to JSON.
        
        Returns:
            JSON string representation of the extractor configuration
        """
        # Create a serializable config dictionary
        config = {
            "patterns": {},
            "flags": self.flags,
            "use_named_groups": self.use_named_groups
        }
        
        # Convert patterns to serializable format
        for field, pattern_config in self.patterns.items():
            if isinstance(pattern_config, str):
                config["patterns"][field] = pattern_config
            else:
                # Create a copy without the transform function (can't be serialized)
                pattern_copy = pattern_config.copy()
                if "transform" in pattern_copy:
                    del pattern_copy["transform"]
                config["patterns"][field] = pattern_copy
        
        return json.dumps(config, indent=2)
    
    @classmethod
    def from_json(cls, json_config: str) -> 'RegExExtractor':
        """Create an extractor from a JSON configuration.
        
        Args:
            json_config: JSON string with extractor configuration
            
        Returns:
            A new RegExExtractor instance
        """
        config = json.loads(json_config)
        return cls(
            patterns=config.get("patterns", {}),
            flags=config.get("flags", re.DOTALL),
            use_named_groups=config.get("use_named_groups", False)
        ) 