"""XPath-based extractor for Crawl4AI.

This module provides an extractor that uses XPath expressions to extract
structured data from XML/HTML content.
"""
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from lxml import etree
import json

from crawl4ai.models import Page
from crawl4ai.extractors.base_extractor import BaseExtractor


T = TypeVar('T')


class XPathExtractor(BaseExtractor):
    """Extract data from XML/HTML content using XPath expressions.
    
    This extractor allows defining a mapping of field names to XPath expressions
    and optional transform functions to extract and process data.
    
    Example:
    ```python
    extractor = XPathExtractor({
        "title": "//h1[@class='title']/text()",
        "content": "//div[@class='content']/p/text()",
        "author": {
            "xpath": "//span[@class='author']/text()",
            "transform": lambda x: x.split("by ")[1] if "by " in x else x
        },
        "tags": {
            "xpath": "//ul[@class='tags']/li/text()",
            "multiple": True
        }
    })
    
    data = extractor.extract(html_content)
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
        xpaths: Dict[str, Union[str, Dict[str, Any]]] = None,
        namespaces: Dict[str, str] = None
    ):
        """Initialize the XPath extractor.
        
        Args:
            xpaths: Dictionary mapping field names to XPath expressions or configs
            namespaces: Optional XML namespaces dictionary for namespace-aware XPath
        """
        self.xpaths = xpaths or {}
        self.namespaces = namespaces or {}
    
    def extract(self, content: Union[str, Page, etree._Element]) -> Dict[str, Any]:
        """Extract data from content using XPath expressions.
        
        Args:
            content: Content to extract data from (string, Page object, or Element)
            
        Returns:
            A dictionary containing the extracted data
        """
        # Parse the content into an element tree
        root = self._parse_content(content)
        if root is None:
            return {}
        
        return self._extract_from_element(root)
    
    def _parse_content(self, content: Union[str, Page, etree._Element]) -> Optional[etree._Element]:
        """Parse content into an element tree.
        
        Args:
            content: Content to parse (string, Page object, or Element)
            
        Returns:
            The root element of the parsed content, or None if parsing fails
        """
        # If it's already an Element, return it
        if isinstance(content, etree._Element):
            return content
        
        # If it's a Page object, get the HTML content
        if not isinstance(content, str):
            if hasattr(content, 'html'):
                html = getattr(content, 'html')
            elif hasattr(content, 'content'):
                html = getattr(content, 'content')
            else:
                return None
        else:
            html = content
        
        if not html:
            return None
        
        # Parse the HTML
        try:
            parser = etree.HTMLParser()
            return etree.fromstring(html, parser)
        except Exception:
            # Try to parse as XML if HTML parsing fails
            try:
                return etree.fromstring(html.encode('utf-8'))
            except Exception:
                return None
    
    def _extract_from_element(self, root: etree._Element) -> Dict[str, Any]:
        """Extract data from an element tree using XPath expressions.
        
        Args:
            root: The root element to extract data from
            
        Returns:
            A dictionary containing the extracted data
        """
        result = {}
        
        for field, xpath_config in self.xpaths.items():
            # Handle string XPath
            if isinstance(xpath_config, str):
                xpath = xpath_config
                transform = None
                multiple = False
                default = None
            # Handle XPath config dictionary
            else:
                xpath = xpath_config.get('xpath')
                transform = xpath_config.get('transform')
                multiple = xpath_config.get('multiple', False)
                default = xpath_config.get('default')
            
            # Extract elements using XPath
            try:
                elements = root.xpath(xpath, namespaces=self.namespaces)
            except Exception:
                result[field] = default
                continue
            
            # Process the extracted elements
            if not elements:
                result[field] = default
                continue
            
            if multiple:
                # Extract multiple values
                values = []
                for element in elements:
                    value = self._process_element(element)
                    if transform:
                        try:
                            value = transform(value)
                        except Exception:
                            pass
                    values.append(value)
                result[field] = values
            else:
                # Extract a single value
                value = self._process_element(elements[0])
                if transform:
                    try:
                        value = transform(value)
                    except Exception:
                        pass
                result[field] = value
        
        return result
    
    def _process_element(self, element: Any) -> Any:
        """Process an extracted element.
        
        Args:
            element: The element to process
            
        Returns:
            The processed value
        """
        # If it's an Element, convert to string representation
        if isinstance(element, etree._Element):
            return etree.tostring(element, encoding='unicode', method='text', with_tail=False).strip()
        return element
    
    def extract_all(self, contents: List[Union[str, Page, etree._Element]]) -> List[Dict[str, Any]]:
        """Extract data from multiple contents.
        
        Args:
            contents: List of content items to extract data from
            
        Returns:
            A list of dictionaries containing the extracted data
        """
        return [self.extract(content) for content in contents]
    
    def add_xpath(
        self,
        field: str,
        xpath: Union[str, Dict[str, Any]]
    ) -> None:
        """Add an XPath expression to the extractor.
        
        Args:
            field: Field name for the extracted data
            xpath: XPath expression or config dictionary
        """
        self.xpaths[field] = xpath
    
    def remove_xpath(self, field: str) -> None:
        """Remove an XPath expression from the extractor.
        
        Args:
            field: Field name to remove
        """
        if field in self.xpaths:
            del self.xpaths[field]
    
    def add_namespace(self, prefix: str, uri: str) -> None:
        """Add an XML namespace to the extractor.
        
        Args:
            prefix: Namespace prefix
            uri: Namespace URI
        """
        self.namespaces[prefix] = uri
    
    def remove_namespace(self, prefix: str) -> None:
        """Remove an XML namespace from the extractor.
        
        Args:
            prefix: Namespace prefix to remove
        """
        if prefix in self.namespaces:
            del self.namespaces[prefix]
    
    def to_json(self) -> str:
        """Convert the extractor configuration to JSON.
        
        Returns:
            JSON string representation of the extractor configuration
        """
        # Create a serializable config dictionary
        config = {
            "xpaths": {},
            "namespaces": self.namespaces
        }
        
        # Convert XPaths to serializable format
        for field, xpath_config in self.xpaths.items():
            if isinstance(xpath_config, str):
                config["xpaths"][field] = xpath_config
            else:
                # Create a copy without the transform function (can't be serialized)
                xpath_copy = xpath_config.copy()
                if "transform" in xpath_copy:
                    del xpath_copy["transform"]
                config["xpaths"][field] = xpath_copy
        
        return json.dumps(config, indent=2)
    
    @classmethod
    def from_json(cls, json_config: str) -> 'XPathExtractor':
        """Create an extractor from a JSON configuration.
        
        Args:
            json_config: JSON string with extractor configuration
            
        Returns:
            A new XPathExtractor instance
        """
        config = json.loads(json_config)
        return cls(
            xpaths=config.get("xpaths", {}),
            namespaces=config.get("namespaces", {})
        ) 