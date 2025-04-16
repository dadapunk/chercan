"""Base content filter for Crawl4AI.

This module provides a base class for content filtering implementations.
Filters can be used to clean, modify, or validate content before further processing.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from crawl4ai.models import Page


class BaseContentFilter(ABC):
    """Base class for all content filters.
    
    Content filters are used to process, clean, or validate extracted content
    before further processing or storage. Filters can be chained together to
    create complex processing pipelines.
    
    Example:
    ```python
    class MyCustomFilter(BaseContentFilter):
        def filter(self, content):
            # Process or filter the content
            # Remove sensitive information
            if "password" in content:
                del content["password"]
            return content
    ```
    """
    
    def __init__(self, **kwargs):
        """Initialize the base content filter.
        
        Args:
            **kwargs: Additional configuration parameters for the filter
        """
        self.config = kwargs
    
    @abstractmethod
    def filter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the filter to the content.
        
        This method should be implemented by all concrete filter classes.
        
        Args:
            content: The content to filter. This is typically a dictionary of
                extracted data from a web page.
                
        Returns:
            The filtered/processed content
        """
        pass
    
    def process_page(self, page: Page) -> Page:
        """Process a full Page object.
        
        This is a convenience method that extracts content from a Page
        object, filters it, and updates the Page's data.
        
        Args:
            page: The Page object to process
            
        Returns:
            The processed Page object with filtered content
        """
        # Extract any existing content from the page
        if hasattr(page, 'data') and isinstance(page.data, dict):
            content = page.data
        else:
            content = {}
        
        # Apply the filter
        filtered_content = self.filter(content)
        
        # Update the page data
        page.data = filtered_content
        
        return page
    
    def __call__(self, content: Union[Dict[str, Any], Page]) -> Union[Dict[str, Any], Page]:
        """Make the filter callable.
        
        This allows using filter instances directly as functions.
        
        Args:
            content: Either a content dictionary or a Page object
            
        Returns:
            The filtered content or Page object
        """
        if isinstance(content, dict):
            return self.filter(content)
        elif hasattr(content, 'html') or hasattr(content, 'content'):
            return self.process_page(content)
        else:
            raise TypeError("Content must be a dictionary or Page object") 