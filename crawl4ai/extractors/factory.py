"""Extractor factory for Crawl4AI.

This module provides a factory for creating and selecting extractors
based on the content type and extraction needs.
"""
from typing import Dict, List, Any, Optional, Union, Type, Callable

from crawl4ai.models import Page
from crawl4ai.extractors.base_extractor import BaseExtractor
from crawl4ai.extractors.css_extractor import CSSExtractor
from crawl4ai.extractors.regex_extractor import RegExExtractor
from crawl4ai.extractors.xpath_extractor import XPathExtractor
from crawl4ai.extractors.llm_extractor import LLMExtractor
from crawl4ai.config import LLMConfig


class ExtractorFactory:
    """Factory for creating and selecting extractors.
    
    This class provides methods for creating different types of extractors
    and selecting the appropriate extractor based on the content.
    
    Example:
    ```python
    factory = ExtractorFactory()
    
    # Create a specific extractor
    css_extractor = factory.create_css_extractor({
        "title": "h1.title",
        "price": ".price"
    })
    
    # Get an extractor for a specific content type
    html_extractor = factory.get_extractor_for_content(
        html_content, 
        content_type="html"
    )
    
    # Extract data using the best extractor for the content
    data = factory.extract(html_content)
    ```
    """
    
    def __init__(self):
        """Initialize the extractor factory."""
        # Register default extractors
        self._extractors = {
            'css': CSSExtractor,
            'xpath': XPathExtractor,
            'regex': RegExExtractor,
            'llm': LLMExtractor
        }
        
        # Extraction strategy mappings
        self._content_type_strategies = {
            'html': ['css', 'xpath', 'llm', 'regex'],
            'xml': ['xpath', 'regex', 'llm'],
            'text': ['regex', 'llm'],
            'json': ['regex', 'llm']
        }
    
    def register_extractor(self, name: str, extractor_class: Type[BaseExtractor]) -> None:
        """Register a new extractor type.
        
        Args:
            name: Name to register the extractor under
            extractor_class: Extractor class to register
        """
        self._extractors[name] = extractor_class
    
    def create_extractor(self, extractor_type: str, *args, **kwargs) -> BaseExtractor:
        """Create an extractor of the specified type.
        
        Args:
            extractor_type: Type of extractor to create
            *args: Positional arguments to pass to the extractor constructor
            **kwargs: Keyword arguments to pass to the extractor constructor
            
        Returns:
            An instance of the requested extractor type
            
        Raises:
            ValueError: If the extractor type is not registered
        """
        if extractor_type not in self._extractors:
            raise ValueError(f"Unknown extractor type: {extractor_type}. Available types: {list(self._extractors.keys())}")
        
        return self._extractors[extractor_type](*args, **kwargs)
    
    def create_css_extractor(self, selectors: Dict[str, Any] = None, **kwargs) -> CSSExtractor:
        """Create a CSS selector-based extractor.
        
        Args:
            selectors: Dictionary mapping field names to CSS selectors
            **kwargs: Additional arguments to pass to the extractor constructor
            
        Returns:
            A configured CSS extractor
        """
        return CSSExtractor(selectors=selectors, **kwargs)
    
    def create_xpath_extractor(self, xpaths: Dict[str, Any] = None, **kwargs) -> XPathExtractor:
        """Create an XPath-based extractor.
        
        Args:
            xpaths: Dictionary mapping field names to XPath expressions
            **kwargs: Additional arguments to pass to the extractor constructor
            
        Returns:
            A configured XPath extractor
        """
        return XPathExtractor(xpaths=xpaths, **kwargs)
    
    def create_regex_extractor(self, patterns: Dict[str, Any] = None, **kwargs) -> RegExExtractor:
        """Create a RegEx-based extractor.
        
        Args:
            patterns: Dictionary mapping field names to regex patterns
            **kwargs: Additional arguments to pass to the extractor constructor
            
        Returns:
            A configured RegEx extractor
        """
        return RegExExtractor(patterns=patterns, **kwargs)
    
    def create_llm_extractor(self, schema: Dict[str, Any] = None, **kwargs) -> LLMExtractor:
        """Create an LLM-based extractor.
        
        Args:
            schema: Dictionary defining the expected extraction schema
            **kwargs: Additional arguments to pass to the extractor constructor
            
        Returns:
            A configured LLM extractor
        """
        return LLMExtractor(schema=schema, **kwargs)
    
    def get_extractor_for_content(
        self, 
        content: Union[str, Page],
        content_type: Optional[str] = None,
        extractors: Optional[List[str]] = None
    ) -> BaseExtractor:
        """Get the appropriate extractor for the given content.
        
        Args:
            content: Content to extract data from
            content_type: Optional type of content (html, xml, text, json)
            extractors: Optional list of extractor types to consider
            
        Returns:
            The most appropriate extractor for the content
        """
        # Determine content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(content)
        
        # Use the provided extractors or get from strategy map
        extractor_types = extractors or self._content_type_strategies.get(
            content_type, ['regex', 'llm']
        )
        
        # Get the first extractor in the list
        if extractor_types:
            extractor_type = extractor_types[0]
            return self.create_extractor(extractor_type)
        
        # Default to regex extractor if no strategy found
        return self.create_regex_extractor()
    
    def extract(
        self, 
        content: Union[str, Page],
        extractors: Optional[List[str]] = None,
        content_type: Optional[str] = None,
        fallback: bool = True
    ) -> Dict[str, Any]:
        """Extract data from content using appropriate extractors.
        
        Args:
            content: Content to extract data from
            extractors: Optional list of extractor types to try
            content_type: Optional content type
            fallback: Whether to try multiple extractors as fallback
            
        Returns:
            Extracted data
        """
        if content_type is None:
            content_type = self._detect_content_type(content)
        
        # Use the provided extractors or get from strategy map
        extractor_types = extractors or self._content_type_strategies.get(
            content_type, ['regex', 'llm']
        )
        
        if not fallback:
            # Just use the first extractor
            if extractor_types:
                extractor = self.create_extractor(extractor_types[0])
                return extractor.extract(content)
            return {}
        
        # Try extractors in sequence
        for extractor_type in extractor_types:
            try:
                extractor = self.create_extractor(extractor_type)
                result = extractor.extract(content)
                
                # If we got some data, return it
                if result and any(result.values()):
                    return result
            except Exception:
                # Continue to the next extractor if this one fails
                pass
        
        # Return empty dict if all extractors fail
        return {}
    
    def extract_with_configuration(
        self,
        content: Union[str, Page],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract data using a configuration dictionary.
        
        Args:
            content: Content to extract data from
            config: Configuration dictionary with extractor settings
            
        Returns:
            Extracted data
        """
        extractor_type = config.get('extractor_type', 'auto')
        
        if extractor_type == 'auto':
            # Auto-detect appropriate extractor
            content_type = config.get('content_type') or self._detect_content_type(content)
            return self.extract(
                content, 
                content_type=content_type,
                fallback=config.get('fallback', True)
            )
        
        # Create specified extractor with configuration
        extractor_config = config.get(f'{extractor_type}_config', {})
        
        if extractor_type == 'css':
            extractor = self.create_css_extractor(**extractor_config)
        elif extractor_type == 'xpath':
            extractor = self.create_xpath_extractor(**extractor_config)
        elif extractor_type == 'regex':
            extractor = self.create_regex_extractor(**extractor_config)
        elif extractor_type == 'llm':
            # Special handling for LLM config
            if 'llm_config' in extractor_config and isinstance(extractor_config['llm_config'], dict):
                llm_config_dict = extractor_config.pop('llm_config')
                llm_config = LLMConfig(**llm_config_dict)
                extractor = self.create_llm_extractor(llm_config=llm_config, **extractor_config)
            else:
                extractor = self.create_llm_extractor(**extractor_config)
        else:
            # Try to create extractor with the given type
            extractor = self.create_extractor(extractor_type, **extractor_config)
        
        return extractor.extract(content)
    
    def _detect_content_type(self, content: Union[str, Page]) -> str:
        """Detect the type of content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Detected content type (html, xml, json, text)
        """
        # If it's a Page object, check content type if available
        if hasattr(content, 'content_type'):
            content_type = getattr(content, 'content_type')
            if content_type:
                if 'html' in content_type.lower():
                    return 'html'
                elif 'xml' in content_type.lower():
                    return 'xml'
                elif 'json' in content_type.lower():
                    return 'json'
                else:
                    return 'text'
        
        # Convert to string for analysis
        if not isinstance(content, str):
            if hasattr(content, 'html'):
                content = getattr(content, 'html')
            elif hasattr(content, 'content'):
                content = getattr(content, 'content')
            else:
                return 'text'
        
        # Check for empty content
        if not content:
            return 'text'
        
        content = content.strip()
        
        # Check for HTML
        if content.startswith('<!DOCTYPE html') or content.startswith('<html') or '<body' in content:
            return 'html'
        
        # Check for XML
        if content.startswith('<?xml') or content.startswith('<') and '?>' in content[:100]:
            return 'xml'
        
        # Check for JSON
        if (content.startswith('{') and content.endswith('}')) or (content.startswith('[') and content.endswith(']')):
            return 'json'
        
        # Default to text
        return 'text' 