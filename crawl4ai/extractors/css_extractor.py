"""CSS selector-based extractor for Crawl4AI.

This module provides an extractor that uses CSS selectors to extract
structured data from web pages.
"""
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from bs4 import BeautifulSoup, Tag, ResultSet
import re
import json

from crawl4ai.models import Page
from crawl4ai.extractors.base_extractor import BaseExtractor


T = TypeVar('T')


class CSSExtractor(BaseExtractor):
    """Extract data from web pages using CSS selectors.
    
    This extractor allows defining a mapping of field names to CSS selectors
    and optional transform functions to extract and process data from web pages.
    
    Example:
    ```python
    extractor = CSSExtractor({
        "title": "h1.title",
        "content": "div.content",
        "author": {
            "selector": "span.author",
            "transform": lambda x: x.split("by ")[1] if "by " in x else x
        },
        "tags": {
            "selector": "ul.tags li",
            "multiple": True
        }
    })
    
    data = extractor.extract(page)
    # {
    #   "title": "Article Title",
    #   "content": "Article content...",
    #   "author": "John Doe",
    #   "tags": ["news", "technology", "ai"]
    # }
    ```
    """
    
    def __init__(
        self,
        selectors: Dict[str, Union[str, Dict[str, Any]]] = None,
        root_selector: Optional[str] = None,
        multiple_items: bool = False
    ):
        """Initialize the CSS extractor.
        
        Args:
            selectors: Dictionary mapping field names to CSS selectors or selector configs
            root_selector: Optional CSS selector for the root element to extract from
            multiple_items: Whether to extract multiple items (returns a list of dictionaries)
        """
        self.selectors = selectors or {}
        self.root_selector = root_selector
        self.multiple_items = multiple_items
    
    def extract(self, page: Page) -> Dict[str, Any]:
        """Extract data from a web page using CSS selectors.
        
        Args:
            page: The web page to extract data from
            
        Returns:
            A dictionary containing the extracted data, or a list of dictionaries
            if multiple_items is True
        """
        # Handle case when page is already parsed HTML
        if isinstance(page, (BeautifulSoup, Tag)):
            soup = page
        # If it's a Page object with a .soup property, use that
        elif hasattr(page, 'soup') and isinstance(page.soup, (BeautifulSoup, Tag)):
            soup = page.soup
        # Otherwise, try to parse the HTML content
        else:
            html_content = getattr(page, 'html', None) or getattr(page, 'content', None)
            if not html_content:
                return {}
            soup = BeautifulSoup(html_content, 'html.parser')
        
        # If multiple items should be extracted, find all root elements and extract from each
        if self.multiple_items:
            if not self.root_selector:
                raise ValueError("Root selector is required when multiple_items is True")
                
            root_elements = soup.select(self.root_selector)
            return [self._extract_item(elem) for elem in root_elements]
        
        # If a root selector is provided, extract from that element
        if self.root_selector:
            root_element = soup.select_one(self.root_selector)
            if not root_element:
                return {}
            return self._extract_item(root_element)
        
        # Otherwise, extract from the entire document
        return self._extract_item(soup)
    
    def _extract_item(self, element: Union[BeautifulSoup, Tag]) -> Dict[str, Any]:
        """Extract data from a single element.
        
        Args:
            element: The element to extract data from
            
        Returns:
            A dictionary containing the extracted data
        """
        result = {}
        
        for field, selector_config in self.selectors.items():
            # Handle string selector
            if isinstance(selector_config, str):
                selector = selector_config
                transform = None
                multiple = False
                attr = None
                default = None
            # Handle selector config dictionary
            else:
                selector = selector_config['selector']
                transform = selector_config.get('transform')
                multiple = selector_config.get('multiple', False)
                attr = selector_config.get('attr')
                default = selector_config.get('default')
            
            # Extract the elements
            if multiple:
                elements = element.select(selector)
                if not elements and default is not None:
                    result[field] = default
                    continue
                    
                extracted_values = []
                for elem in elements:
                    value = self._extract_value(elem, attr, transform)
                    if value is not None:
                        extracted_values.append(value)
                
                result[field] = extracted_values
            else:
                found_element = element.select_one(selector)
                if not found_element:
                    result[field] = default
                    continue
                
                result[field] = self._extract_value(found_element, attr, transform)
        
        return result
    
    def _extract_value(
        self,
        element: Tag,
        attr: Optional[str] = None,
        transform: Optional[Callable[[str], Any]] = None
    ) -> Any:
        """Extract a value from an element.
        
        Args:
            element: The element to extract a value from
            attr: Optional attribute to extract (e.g., 'href', 'src')
            transform: Optional function to transform the extracted value
            
        Returns:
            The extracted value
        """
        # Extract the raw value
        if attr:
            value = element.get(attr, '')
        else:
            value = element.get_text(strip=True)
        
        # Apply transformation if provided
        if transform and callable(transform):
            try:
                return transform(value)
            except Exception:
                return value
        
        return value
    
    def add_selector(
        self,
        field: str,
        selector: Union[str, Dict[str, Any]]
    ) -> None:
        """Add a selector to the extractor.
        
        Args:
            field: Field name for the extracted data
            selector: CSS selector or selector config dictionary
        """
        self.selectors[field] = selector
    
    def remove_selector(self, field: str) -> None:
        """Remove a selector from the extractor.
        
        Args:
            field: Field name to remove
        """
        if field in self.selectors:
            del self.selectors[field]
    
    @classmethod
    def create_template(cls, page: Page, selector: str) -> 'CSSExtractor':
        """Create a template extractor based on a sample page.
        
        This method analyzes the page structure and creates an extractor
        with selectors for common elements.
        
        Args:
            page: Sample page to analyze
            selector: CSS selector for the root element
            
        Returns:
            A new CSSExtractor instance
        """
        # Parse page if needed
        if hasattr(page, 'soup') and isinstance(page.soup, BeautifulSoup):
            soup = page.soup
        else:
            html_content = getattr(page, 'html', None) or getattr(page, 'content', None)
            if not html_content:
                return cls()
            soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the root element
        root = soup.select_one(selector)
        if not root:
            return cls()
        
        # Initialize selectors dict
        selectors = {}
        
        # Look for common elements and add selectors
        # Title (h1, h2, h3, .title, etc.)
        for title_sel in ['h1', 'h2', '.title', '[class*="title" i]', '[id*="title" i]']:
            title_elem = root.select_one(title_sel)
            if title_elem:
                selectors['title'] = title_sel
                break
        
        # Content (article, .content, p, etc.)
        for content_sel in ['article', '.content', '.body', 'p', '[class*="content" i]']:
            content_elems = root.select(content_sel)
            if content_elems:
                selectors['content'] = {
                    'selector': content_sel,
                    'multiple': len(content_elems) > 1
                }
                break
        
        # Date (.date, time, etc.)
        for date_sel in ['time', '.date', '.published', '[datetime]']:
            date_elem = root.select_one(date_sel)
            if date_elem:
                selectors['date'] = {
                    'selector': date_sel,
                    'attr': 'datetime' if date_elem.has_attr('datetime') else None
                }
                break
        
        # Links (a[href])
        links = root.select('a[href]')
        if links:
            selectors['links'] = {
                'selector': 'a[href]',
                'attr': 'href',
                'multiple': True
            }
        
        # Images (img[src])
        images = root.select('img[src]')
        if images:
            selectors['images'] = {
                'selector': 'img[src]',
                'attr': 'src',
                'multiple': True
            }
        
        # Create and return the extractor
        return cls(selectors=selectors, root_selector=selector)
    
    def to_json(self) -> str:
        """Convert the extractor configuration to JSON.
        
        Returns:
            JSON string representation of the extractor configuration
        """
        config = {
            'selectors': self.selectors,
            'root_selector': self.root_selector,
            'multiple_items': self.multiple_items
        }
        return json.dumps(config, indent=2)
    
    @classmethod
    def from_json(cls, json_config: str) -> 'CSSExtractor':
        """Create an extractor from a JSON configuration.
        
        Args:
            json_config: JSON string with extractor configuration
            
        Returns:
            A new CSSExtractor instance
        """
        config = json.loads(json_config)
        return cls(
            selectors=config.get('selectors', {}),
            root_selector=config.get('root_selector'),
            multiple_items=config.get('multiple_items', False)
        ) 