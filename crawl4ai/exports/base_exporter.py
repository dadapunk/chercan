"""Base exporter for Crawl4AI.

This module provides a base class for exporting crawled content
into various formats.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TextIO, Iterable
import os
import json

from crawl4ai.models import Page, CrawlResult


class BaseExporter(ABC):
    """Base class for all exporters.
    
    This abstract class defines the interface for exporting crawled content
    to various formats like Markdown, JSON, CSV, etc.
    
    Exporters convert crawled data into specific output formats that can be
    saved to files or used in other applications.
    """
    
    def __init__(self, **kwargs):
        """Initialize the base exporter.
        
        Args:
            **kwargs: Additional configuration parameters for the exporter
        """
        self.config = kwargs
    
    @abstractmethod
    def export_content(self, content: Dict[str, Any]) -> str:
        """Export a single content dictionary to the target format.
        
        Args:
            content: Dictionary containing the content to export
            
        Returns:
            String representation in the target format
        """
        pass
    
    @abstractmethod
    def export_page(self, page: Page) -> str:
        """Export a Page object to the target format.
        
        Args:
            page: Page object to export
            
        Returns:
            String representation in the target format
        """
        pass
    
    def export_multiple(self, contents: Iterable[Dict[str, Any]]) -> str:
        """Export multiple content dictionaries to the target format.
        
        Args:
            contents: Iterable of content dictionaries to export
            
        Returns:
            String representation in the target format
        """
        results = []
        for content in contents:
            results.append(self.export_content(content))
        return self._join_multiple_exports(results)
    
    def export_pages(self, pages: Iterable[Page]) -> str:
        """Export multiple Page objects to the target format.
        
        Args:
            pages: Iterable of Page objects to export
            
        Returns:
            String representation in the target format
        """
        results = []
        for page in pages:
            results.append(self.export_page(page))
        return self._join_multiple_exports(results)
    
    def export_crawl_result(self, result: CrawlResult) -> str:
        """Export a CrawlResult object to the target format.
        
        Args:
            result: CrawlResult object to export
            
        Returns:
            String representation in the target format
        """
        if hasattr(result, 'pages') and result.pages:
            return self.export_pages(result.pages)
        return ""
    
    def save_to_file(
        self, 
        content: Union[Dict[str, Any], Page, Iterable[Dict[str, Any]], Iterable[Page], CrawlResult],
        file_path: str
    ) -> bool:
        """Save exported content to a file.
        
        Args:
            content: Content to export (dictionary, Page, or iterable of either)
            file_path: Path to the output file
            
        Returns:
            True if the export was successful, False otherwise
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Export the content based on its type
            if isinstance(content, dict):
                result = self.export_content(content)
            elif isinstance(content, Page):
                result = self.export_page(content)
            elif isinstance(content, CrawlResult):
                result = self.export_crawl_result(content)
            elif hasattr(content, '__iter__'):
                # Check if it's an iterable of dictionaries or Pages
                first_item = next(iter(content), None)
                if first_item is None:
                    # Empty iterable
                    result = ""
                elif isinstance(first_item, dict):
                    result = self.export_multiple(content)
                elif isinstance(first_item, Page):
                    result = self.export_pages(content)
                else:
                    raise ValueError(f"Unsupported content type in iterable: {type(first_item)}")
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result)
            
            return True
        except Exception as e:
            # Handle any errors during export
            print(f"Error exporting content: {str(e)}")
            return False
    
    def export_to_file(
        self,
        content: Union[Dict[str, Any], Page, Iterable[Dict[str, Any]], Iterable[Page], CrawlResult],
        file_path: str
    ) -> bool:
        """Alias for save_to_file for more intuitive API.
        
        Args:
            content: Content to export (dictionary, Page, or iterable of either)
            file_path: Path to the output file
            
        Returns:
            True if the export was successful, False otherwise
        """
        return self.save_to_file(content, file_path)
    
    def _join_multiple_exports(self, exports: List[str]) -> str:
        """Join multiple export results into a single string.
        
        Default implementation just joins with newlines.
        Subclasses should override this if needed.
        
        Args:
            exports: List of exported content strings
            
        Returns:
            Combined string for multiple exports
        """
        return "\n\n".join(exports) 