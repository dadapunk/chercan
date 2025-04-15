"""Base extractor for Crawl4AI.

This module provides the base extractor class that all extractors
in the Crawl4AI framework should extend.
"""
from typing import Any, Dict, List, Optional, Union, Type
from abc import ABC, abstractmethod

from crawl4ai.models import Page


class BaseExtractor(ABC):
    """Base extractor class for extracting data from web pages.
    
    This is an abstract class that defines the interface for all extractors.
    Extractor implementations should override the extract method to implement
    specific extraction logic.
    
    Example:
    ```python
    class MyExtractor(BaseExtractor):
        def extract(self, page: Page) -> Dict[str, Any]:
            # Extract data from the page
            title = page.extract_text("h1.title")
            content = page.extract_text("div.content")
            
            return {
                "title": title,
                "content": content
            }
    ```
    """
    
    @abstractmethod
    def extract(self, page: Page) -> Dict[str, Any]:
        """Extract data from a web page.
        
        Args:
            page: The web page to extract data from
            
        Returns:
            A dictionary containing the extracted data
        """
        pass
    
    def extract_all(self, pages: List[Page]) -> List[Dict[str, Any]]:
        """Extract data from multiple web pages.
        
        Args:
            pages: List of web pages to extract data from
            
        Returns:
            A list of dictionaries containing the extracted data
        """
        return [self.extract(page) for page in pages]
    
    def extract_with_fallback(
        self,
        page: Page,
        fallback_extractors: List[Type['BaseExtractor']] = None
    ) -> Dict[str, Any]:
        """Extract data with fallback extractors.
        
        This method tries to extract data using this extractor first, and if it
        fails or returns empty data, falls back to other extractors.
        
        Args:
            page: The web page to extract data from
            fallback_extractors: List of fallback extractor classes
            
        Returns:
            A dictionary containing the extracted data
        """
        # Try with this extractor first
        try:
            data = self.extract(page)
            if data and any(data.values()):
                return data
        except Exception:
            pass
        
        # Try fallback extractors
        if fallback_extractors:
            for extractor_class in fallback_extractors:
                try:
                    extractor = extractor_class()
                    data = extractor.extract(page)
                    if data and any(data.values()):
                        return data
                except Exception:
                    continue
        
        # Return empty data if all extractors fail
        return {} 