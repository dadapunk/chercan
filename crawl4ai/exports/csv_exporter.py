"""CSV exporter for Crawl4AI.

This module provides functionality for exporting crawled content
into CSV format.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Iterable, TextIO
import csv
import io
import os
from datetime import datetime
from collections import defaultdict

from crawl4ai.exports.base_exporter import BaseExporter
from crawl4ai.models import Page


class CSVExporter(BaseExporter):
    """Exporter for CSV format.
    
    This class converts crawled content into CSV format
    that can be easily imported into spreadsheets, databases, or used
    for data analysis.
    
    Example:
    ```python
    # Create a CSV exporter
    exporter = CSVExporter(include_headers=True, delimiter=',')
    
    # Export content to CSV
    csv_content = exporter.export_content(content)
    
    # Save to a file
    exporter.save_to_file(content, "output.csv")
    ```
    """
    
    def __init__(
        self,
        include_headers: bool = True,
        delimiter: str = ',',
        quotechar: str = '"',
        flatten_nested: bool = True,
        flatten_delimiter: str = '_',
        max_flatten_depth: int = 3,
        exclude_fields: Optional[List[str]] = None,
        include_fields: Optional[List[str]] = None,
        field_transformer: Optional[Dict[str, Callable[[Any], str]]] = None,
        include_metadata: bool = False,
        metadata_prefix: str = '_meta_',
        **kwargs
    ):
        """Initialize the CSV exporter.
        
        Args:
            include_headers: Whether to include header row in the output
            delimiter: Character used to separate fields
            quotechar: Character used to quote fields
            flatten_nested: Whether to flatten nested dictionaries
            flatten_delimiter: Character used to join keys in flattened dictionaries
            max_flatten_depth: Maximum depth for flattening nested structures
            exclude_fields: Fields to exclude from the output
            include_fields: Only include these fields (if provided)
            field_transformer: Custom transformers for specific fields
            include_metadata: Whether to include metadata as columns
            metadata_prefix: Prefix for metadata columns
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.include_headers = include_headers
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.flatten_nested = flatten_nested
        self.flatten_delimiter = flatten_delimiter
        self.max_flatten_depth = max_flatten_depth
        self.exclude_fields = set(exclude_fields or [])
        self.include_fields = set(include_fields or [])
        self.field_transformer = field_transformer or {}
        self.include_metadata = include_metadata
        self.metadata_prefix = metadata_prefix
    
    def export_content(self, content: Dict[str, Any]) -> str:
        """Export a single content dictionary to CSV.
        
        Args:
            content: Dictionary containing the content to export
            
        Returns:
            CSV string representation of the content
        """
        if not content:
            return ""
        
        # Flatten the content if needed
        flattened_content = self._flatten_dict(content) if self.flatten_nested else content
        
        # Filter fields based on configuration
        filtered_content = {}
        for field_name, value in flattened_content.items():
            if self._should_include_field(field_name):
                filtered_content[field_name] = value
        
        # Add metadata if configured
        if self.include_metadata:
            metadata = self._generate_metadata(content)
            for key, value in metadata.items():
                filtered_content[f"{self.metadata_prefix}{key}"] = value
        
        # Convert to CSV
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            quoting=csv.QUOTE_MINIMAL
        )
        
        # Add headers if configured
        if self.include_headers:
            writer.writerow(filtered_content.keys())
        
        # Add the row of values
        writer.writerow(self._transform_values(filtered_content))
        
        return output.getvalue()
    
    def export_page(self, page: Page) -> str:
        """Export a Page object to CSV.
        
        Args:
            page: Page object to export
            
        Returns:
            CSV string representation of the page
        """
        # Create a dictionary representation of the page
        page_dict = {"url": getattr(page, "url", "")}
        
        # Add other page attributes
        for attr in ["title", "status_code", "content_type", "depth"]:
            if hasattr(page, attr) and getattr(page, attr) is not None:
                page_dict[attr] = getattr(page, attr)
        
        # Add page data if available
        if hasattr(page, "data") and isinstance(page.data, dict):
            # Either use a prefix for data fields or merge them with page attributes
            for key, value in page.data.items():
                if key not in page_dict:  # Avoid overwriting page attributes
                    page_dict[f"data_{key}"] = value
        
        # Add metadata if configured
        if self.include_metadata:
            metadata = self._generate_page_metadata(page)
            for key, value in metadata.items():
                page_dict[f"{self.metadata_prefix}{key}"] = value
        
        return self.export_content(page_dict)
    
    def export_multiple(self, contents: Iterable[Dict[str, Any]]) -> str:
        """Export multiple content dictionaries to CSV.
        
        Args:
            contents: Iterable of content dictionaries to export
            
        Returns:
            CSV string representation of the contents
        """
        if not contents:
            return ""
        
        # Convert to list to allow multiple passes
        contents_list = list(contents)
        
        # First pass: collect all possible fields and process content
        all_fields = set()
        processed_contents = []
        
        for content in contents_list:
            # Flatten the content if needed
            flattened_content = self._flatten_dict(content) if self.flatten_nested else content
            
            # Filter fields based on configuration
            filtered_content = {}
            for field_name, value in flattened_content.items():
                if self._should_include_field(field_name):
                    filtered_content[field_name] = value
                    all_fields.add(field_name)
            
            # Add metadata if configured
            if self.include_metadata:
                metadata = self._generate_metadata(content)
                for key, value in metadata.items():
                    meta_key = f"{self.metadata_prefix}{key}"
                    filtered_content[meta_key] = value
                    all_fields.add(meta_key)
            
            processed_contents.append(filtered_content)
        
        # Convert to CSV
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            quoting=csv.QUOTE_MINIMAL
        )
        
        # Sort fields for consistent output
        sorted_fields = sorted(all_fields)
        
        # Add headers if configured
        if self.include_headers:
            writer.writerow(sorted_fields)
        
        # Add rows
        for content in processed_contents:
            row = []
            for field in sorted_fields:
                # Use empty string for missing fields
                value = content.get(field, "")
                # Apply transformation if available
                if field in self.field_transformer and callable(self.field_transformer[field]):
                    value = self.field_transformer[field](value)
                elif isinstance(value, (dict, list)):
                    # Convert complex types to string representation
                    value = str(value)
                row.append(value)
            writer.writerow(row)
        
        return output.getvalue()
    
    def export_pages(self, pages: Iterable[Page]) -> str:
        """Export multiple Page objects to CSV.
        
        Args:
            pages: Iterable of Page objects to export
            
        Returns:
            CSV string representation of the pages
        """
        if not pages:
            return ""
        
        # Convert pages to dictionaries
        contents = []
        for page in pages:
            # Create a dictionary representation of the page
            page_dict = {"url": getattr(page, "url", "")}
            
            # Add other page attributes
            for attr in ["title", "status_code", "content_type", "depth"]:
                if hasattr(page, attr) and getattr(page, attr) is not None:
                    page_dict[attr] = getattr(page, attr)
            
            # Add page data if available
            if hasattr(page, "data") and isinstance(page.data, dict):
                # Either use a prefix for data fields or merge them with page attributes
                for key, value in page.data.items():
                    if key not in page_dict:  # Avoid overwriting page attributes
                        page_dict[f"data_{key}"] = value
            
            # Add metadata if configured
            if self.include_metadata:
                metadata = self._generate_page_metadata(page)
                for key, value in metadata.items():
                    page_dict[f"{self.metadata_prefix}{key}"] = value
            
            contents.append(page_dict)
        
        return self.export_multiple(contents)
    
    def _join_multiple_exports(self, exports: List[str]) -> str:
        """Join multiple CSV exports.
        
        Args:
            exports: List of CSV strings
            
        Returns:
            Combined CSV string
        """
        if not exports:
            return ""
        
        # Handle the case where we have multiple CSV outputs to combine
        # We need to keep the header only from the first one
        if not self.include_headers or len(exports) == 1:
            return "".join(exports)
        
        result = []
        for i, export in enumerate(exports):
            if i == 0:
                # Include header from first export
                result.append(export)
            else:
                # Skip header from subsequent exports
                lines = export.splitlines()
                if len(lines) > 1:  # Make sure there's content after the header
                    result.append("\n".join(lines[1:]))
                    if not export.endswith("\n"):
                        result.append("\n")
        
        return "".join(result)
    
    def _flatten_dict(self, d: Dict[str, Any], prefix: str = '', depth: int = 0) -> Dict[str, Any]:
        """Flatten a nested dictionary.
        
        Args:
            d: Dictionary to flatten
            prefix: Prefix for keys
            depth: Current depth level
            
        Returns:
            Flattened dictionary
        """
        if depth >= self.max_flatten_depth:
            return {prefix.rstrip(self.flatten_delimiter): d} if prefix else d
        
        items = []
        for k, v in d.items():
            new_key = f"{prefix}{k}{self.flatten_delimiter}" if prefix else f"{k}{self.flatten_delimiter}"
            
            if isinstance(v, dict) and self.flatten_nested:
                items.extend(self._flatten_dict(v, new_key, depth + 1).items())
            else:
                items.append((new_key.rstrip(self.flatten_delimiter), v))
        
        return dict(items)
    
    def _transform_values(self, content: Dict[str, Any]) -> List[Any]:
        """Transform dictionary values for CSV export.
        
        Args:
            content: Dictionary with field values
            
        Returns:
            List of transformed values
        """
        values = []
        for field, value in content.items():
            # Apply custom transformer if available
            if field in self.field_transformer and callable(self.field_transformer[field]):
                transformed_value = self.field_transformer[field](value)
            elif isinstance(value, (dict, list)):
                # Convert complex types to string representation
                transformed_value = str(value)
            else:
                transformed_value = value
            values.append(transformed_value)
        return values
    
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
    
    def _generate_metadata(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata for the content.
        
        Args:
            content: Content dictionary
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            "fields_count": len(content),
            "export_time": datetime.now().isoformat()
        }
        
        # Add Crawl4AI version if available
        try:
            from crawl4ai import __version__
            metadata["version"] = __version__
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
        metadata = {
            "export_time": datetime.now().isoformat()
        }
        
        # Add page-specific metadata
        if hasattr(page, "depth") and page.depth is not None:
            metadata["depth"] = page.depth
        
        if hasattr(page, "status_code") and page.status_code is not None:
            metadata["status_code"] = page.status_code
        
        if hasattr(page, "content_type") and page.content_type:
            metadata["content_type"] = page.content_type
        
        # Add data fields count if available
        if hasattr(page, "data") and isinstance(page.data, dict):
            metadata["fields_count"] = len(page.data)
        
        # Add Crawl4AI version if available
        try:
            from crawl4ai import __version__
            metadata["version"] = __version__
        except (ImportError, AttributeError):
            pass
        
        return metadata