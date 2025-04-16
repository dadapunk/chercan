"""JSON exporter for Crawl4AI.

This module provides functionality for exporting crawled content
into JSON format.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Iterable
import json
import os
from datetime import datetime

from crawl4ai.exports.base_exporter import BaseExporter
from crawl4ai.models import Page


class JSONExporter(BaseExporter):
    """Exporter for JSON format.
    
    This class converts crawled content into well-formatted JSON
    that can be used for data exchange, storage, or further processing.
    
    Example:
    ```python
    # Create a JSON exporter
    exporter = JSONExporter(indent=2, include_metadata=True)
    
    # Export content to JSON
    json_content = exporter.export_content(content)
    
    # Save to a file
    exporter.save_to_file(content, "output.json")
    ```
    """
    
    def __init__(
        self,
        indent: Optional[int] = 2,
        include_metadata: bool = True,
        include_export_time: bool = True,
        include_version: bool = True,
        sort_keys: bool = False,
        ensure_ascii: bool = False,
        metadata_key: str = "_metadata",
        exclude_fields: Optional[List[str]] = None,
        include_fields: Optional[List[str]] = None,
        default_serializer: Optional[Callable[[Any], Any]] = None,
        datetime_format: str = "%Y-%m-%d %H:%M:%S",
        **kwargs
    ):
        """Initialize the JSON exporter.
        
        Args:
            indent: Number of spaces for indentation (None for compact JSON)
            include_metadata: Whether to include metadata in the output
            include_export_time: Whether to include the export timestamp
            include_version: Whether to include the Crawl4AI version
            sort_keys: Whether to sort dictionary keys alphabetically
            ensure_ascii: Whether to escape non-ASCII characters
            metadata_key: Key to use for storing metadata
            exclude_fields: Fields to exclude from the output
            include_fields: Only include these fields (if provided)
            default_serializer: Custom function for serializing non-JSON types
            datetime_format: Format for datetime objects
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.indent = indent
        self.include_metadata = include_metadata
        self.include_export_time = include_export_time
        self.include_version = include_version
        self.sort_keys = sort_keys
        self.ensure_ascii = ensure_ascii
        self.metadata_key = metadata_key
        self.exclude_fields = set(exclude_fields or [])
        self.include_fields = set(include_fields or [])
        self.default_serializer = default_serializer or self._default_json_serializer
        self.datetime_format = datetime_format
    
    def export_content(self, content: Dict[str, Any]) -> str:
        """Export a single content dictionary to JSON.
        
        Args:
            content: Dictionary containing the content to export
            
        Returns:
            JSON string representation of the content
        """
        if not content:
            return json.dumps({}, indent=self.indent, ensure_ascii=self.ensure_ascii)
        
        # Create a copy to avoid modifying the original
        export_data = {}
        
        # Filter fields based on configuration
        for field_name, value in content.items():
            if self._should_include_field(field_name):
                export_data[field_name] = value
        
        # Add metadata if configured
        if self.include_metadata:
            export_data[self.metadata_key] = self._generate_metadata(content)
        
        # Convert to JSON
        return json.dumps(
            export_data,
            indent=self.indent,
            sort_keys=self.sort_keys,
            ensure_ascii=self.ensure_ascii,
            default=self.default_serializer
        )
    
    def export_page(self, page: Page) -> str:
        """Export a Page object to JSON.
        
        Args:
            page: Page object to export
            
        Returns:
            JSON string representation of the page
        """
        # Extract basic page attributes into a dictionary
        export_data = {"url": getattr(page, "url", None)}
        
        # Add page data if available
        if hasattr(page, "data") and isinstance(page.data, dict):
            # Filter fields if needed
            data = {}
            for field_name, value in page.data.items():
                if self._should_include_field(field_name):
                    data[field_name] = value
            export_data["data"] = data
        
        # Add additional page attributes if they exist
        for attr in ["title", "status_code", "content_type", "depth", "headers"]:
            if hasattr(page, attr) and getattr(page, attr) is not None:
                export_data[attr] = getattr(page, attr)
        
        # Add metadata if configured
        if self.include_metadata:
            export_data[self.metadata_key] = self._generate_page_metadata(page)
        
        # Convert to JSON
        return json.dumps(
            export_data,
            indent=self.indent,
            sort_keys=self.sort_keys,
            ensure_ascii=self.ensure_ascii,
            default=self.default_serializer
        )
    
    def save_to_file(self, data: Union[Dict[str, Any], Page, List[Dict[str, Any]], List[Page]], output_path: str) -> None:
        """Save exported content to a file.
        
        Args:
            data: Content to export, can be a single item or a list
            output_path: Path where the output should be saved
            
        Raises:
            IOError: If there was an error writing to the file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Export the data
        if isinstance(data, list):
            json_content = self.export_multiple(data)
        elif isinstance(data, Page):
            json_content = self.export_page(data)
        else:
            json_content = self.export_content(data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(json_content)
    
    def export_multiple(self, items: Union[List[Dict[str, Any]], List[Page]]) -> str:
        """Export multiple content items to a single JSON array.
        
        Args:
            items: List of content dictionaries or Page objects to export
            
        Returns:
            JSON string representation of the items
        """
        if not items:
            return json.dumps([], indent=self.indent, ensure_ascii=self.ensure_ascii)
        
        # Create a list to hold all exported items
        export_list = []
        
        # Process each item
        for item in items:
            # Convert each item to a dictionary
            if isinstance(item, Page):
                # For Page objects, convert to dict representation
                item_data = {"url": getattr(item, "url", None)}
                
                # Add page data if available
                if hasattr(item, "data") and isinstance(item.data, dict):
                    # Filter fields if needed
                    data = {}
                    for field_name, value in item.data.items():
                        if self._should_include_field(field_name):
                            data[field_name] = value
                    item_data["data"] = data
                
                # Add additional page attributes
                for attr in ["title", "status_code", "content_type", "depth", "headers"]:
                    if hasattr(item, attr) and getattr(item, attr) is not None:
                        item_data[attr] = getattr(item, attr)
                
            elif isinstance(item, dict):
                # For dictionaries, filter fields based on configuration
                item_data = {}
                for field_name, value in item.items():
                    if self._should_include_field(field_name):
                        item_data[field_name] = value
            else:
                # For other types, just use as is
                item_data = item
            
            # Add metadata if configured and possible
            if self.include_metadata and isinstance(item_data, dict):
                if isinstance(item, Page):
                    item_data[self.metadata_key] = self._generate_page_metadata(item)
                elif isinstance(item, dict):
                    item_data[self.metadata_key] = self._generate_metadata(item)
            
            export_list.append(item_data)
        
        # Add wrapper metadata if configured
        if self.include_metadata:
            collection_metadata = {
                "count": len(export_list),
                "export_time": datetime.now().strftime(self.datetime_format)
            }
            
            if self.include_version:
                try:
                    from crawl4ai import __version__
                    collection_metadata["crawl4ai_version"] = __version__
                except (ImportError, AttributeError):
                    pass
                    
            return json.dumps(
                {
                    "items": export_list,
                    self.metadata_key: collection_metadata
                },
                indent=self.indent,
                sort_keys=self.sort_keys,
                ensure_ascii=self.ensure_ascii,
                default=self.default_serializer
            )
        
        # Without metadata, just return the list
        return json.dumps(
            export_list,
            indent=self.indent,
            sort_keys=self.sort_keys,
            ensure_ascii=self.ensure_ascii,
            default=self.default_serializer
        )
    
    def _generate_metadata(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata for the content.
        
        Args:
            content: Content dictionary
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            "fields_count": len(content),
        }
        
        # Add export time if configured
        if self.include_export_time:
            metadata["export_time"] = datetime.now().strftime(self.datetime_format)
        
        # Add Crawl4AI version if configured
        if self.include_version:
            try:
                from crawl4ai import __version__
                metadata["crawl4ai_version"] = __version__
            except (ImportError, AttributeError):
                pass
        
        return metadata
    
    def _generate_page_metadata(self, page: Page) -> Dict[str, Any]:
        """Generate metadata for a Page object.
        
        Args:
            page: Page object
            
        Returns:
            Dictionary with metadata
        """
        metadata = {}
        
        # Add page attributes that are useful as metadata
        if hasattr(page, "content_type") and page.content_type:
            metadata["content_type"] = page.content_type
            
        if hasattr(page, "status_code") and page.status_code:
            metadata["status_code"] = page.status_code
        
        if hasattr(page, "depth") and page.depth is not None:
            metadata["depth"] = page.depth
        
        # Add data fields count
        if hasattr(page, "data") and isinstance(page.data, dict):
            metadata["fields_count"] = len(page.data)
        
        # Add export time if configured
        if self.include_export_time:
            metadata["export_time"] = datetime.now().strftime(self.datetime_format)
        
        # Add Crawl4AI version if configured
        if self.include_version:
            try:
                from crawl4ai import __version__
                metadata["crawl4ai_version"] = __version__
            except (ImportError, AttributeError):
                pass
        
        return metadata
    
    def _should_include_field(self, field_name: str) -> bool:
        """Determine if a field should be included based on include/exclude rules.
        
        Args:
            field_name: Name of the field
            
        Returns:
            True if the field should be included, False otherwise
        """
        # If include_fields is provided, only include those fields
        if self.include_fields:
            return field_name in self.include_fields
        
        # Otherwise, include all fields except excluded ones
        return field_name not in self.exclude_fields
    
    def _default_json_serializer(self, obj: Any) -> Any:
        """Default serializer for objects that aren't JSON serializable.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON serializable representation of the object
            
        Raises:
            TypeError: If the object cannot be serialized
        """
        # Handle datetime objects
        if hasattr(obj, 'isoformat'):
            return obj.strftime(self.datetime_format)
        
        # Handle bytes
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='replace')
        
        # Handle custom objects with __dict__
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        
        # Handle sets
        if isinstance(obj, set):
            return list(obj)
        
        # Let JSON module handle the error for unsupported types
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable") 