"""Markdown exporter for Crawl4AI.

This module provides functionality for exporting crawled content
into Markdown format.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Iterable
import re
import html
from datetime import datetime

from crawl4ai.exports.base_exporter import BaseExporter
from crawl4ai.models import Page


class MarkdownExporter(BaseExporter):
    """Exporter for Markdown format.
    
    This class converts crawled content into well-formatted Markdown
    that can be used for documentation, reports, or further processing.
    
    Example:
    ```python
    # Create a Markdown exporter
    exporter = MarkdownExporter(include_metadata=True, heading_level=2)
    
    # Export content to Markdown
    markdown = exporter.export_content(content)
    
    # Save to a file
    exporter.save_to_file(content, "output.md")
    ```
    """
    
    def __init__(
        self,
        include_metadata: bool = True,
        include_url: bool = True,
        heading_level: int = 2,
        max_list_items: Optional[int] = None,
        max_table_rows: Optional[int] = None,
        field_formatter: Optional[Dict[str, Callable[[Any], str]]] = None,
        exclude_fields: Optional[List[str]] = None,
        include_fields: Optional[List[str]] = None,
        template: Optional[str] = None,
        timestamp_format: str = "%Y-%m-%d %H:%M:%S",
        **kwargs
    ):
        """Initialize the Markdown exporter.
        
        Args:
            include_metadata: Whether to include metadata in the output
            include_url: Whether to include the URL in the output
            heading_level: Base heading level (1-6) for section headings
            max_list_items: Maximum number of items to include in lists
            max_table_rows: Maximum number of rows to include in tables
            field_formatter: Custom formatters for specific fields
            exclude_fields: Fields to exclude from the output
            include_fields: Only include these fields (if provided)
            template: Custom template for the output
            timestamp_format: Format for timestamps
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.include_metadata = include_metadata
        self.include_url = include_url
        self.heading_level = min(max(1, heading_level), 6)
        self.max_list_items = max_list_items
        self.max_table_rows = max_table_rows
        self.field_formatter = field_formatter or {}
        self.exclude_fields = set(exclude_fields or [])
        self.include_fields = set(include_fields or [])
        self.template = template
        self.timestamp_format = timestamp_format
    
    def export_content(self, content: Dict[str, Any]) -> str:
        """Export a single content dictionary to Markdown.
        
        Args:
            content: Dictionary containing the content to export
            
        Returns:
            Markdown representation of the content
        """
        if not content:
            return ""
        
        # Start with an empty markdown string
        markdown = []
        
        # If a template is provided, use it
        if self.template:
            return self._apply_template(content, self.template)
        
        # Add title if available
        title = self._get_title(content)
        if title:
            markdown.append(f"{'#' * self.heading_level} {title}\n")
        
        # Process each field
        for field_name, value in content.items():
            # Skip excluded fields or fields not in include_fields if provided
            if self._should_skip_field(field_name):
                continue
            
            # Format the field name as a heading
            field_heading = self._format_field_name(field_name)
            markdown.append(f"{'#' * (self.heading_level + 1)} {field_heading}\n")
            
            # Format the field value
            field_value = self._format_field_value(field_name, value)
            markdown.append(f"{field_value}\n")
        
        # Add metadata if required
        if self.include_metadata:
            markdown.append(self._generate_metadata(content))
        
        return "\n".join(markdown)
    
    def export_page(self, page: Page) -> str:
        """Export a Page object to Markdown.
        
        Args:
            page: Page object to export
            
        Returns:
            Markdown representation of the page
        """
        # Start with an empty markdown string
        markdown = []
        
        # Add title if available
        title = self._get_page_title(page)
        if title:
            markdown.append(f"{'#' * self.heading_level} {title}\n")
        
        # Add URL if available and configured
        if self.include_url and hasattr(page, 'url') and page.url:
            markdown.append(f"URL: [{page.url}]({page.url})\n")
        
        # Add content data if available
        if hasattr(page, 'data') and isinstance(page.data, dict):
            # Process each field in the data
            for field_name, value in page.data.items():
                # Skip excluded fields or fields not in include_fields if provided
                if self._should_skip_field(field_name):
                    continue
                
                # Format the field name as a heading
                field_heading = self._format_field_name(field_name)
                markdown.append(f"{'#' * (self.heading_level + 1)} {field_heading}\n")
                
                # Format the field value
                field_value = self._format_field_value(field_name, value)
                markdown.append(f"{field_value}\n")
        
        # Add page metadata if required
        if self.include_metadata:
            markdown.append(self._generate_page_metadata(page))
        
        return "\n".join(markdown)
    
    def _join_multiple_exports(self, exports: List[str]) -> str:
        """Join multiple Markdown exports with separators.
        
        Args:
            exports: List of Markdown strings
            
        Returns:
            Combined Markdown with separators
        """
        if not exports:
            return ""
        
        # Join with a horizontal rule separator
        return "\n\n---\n\n".join(exports)
    
    def _get_title(self, content: Dict[str, Any]) -> str:
        """Extract a title from the content.
        
        Looks for common title fields like 'title', 'name', 'heading'.
        
        Args:
            content: Content dictionary
            
        Returns:
            Title string or empty string if no title found
        """
        title_fields = ['title', 'name', 'heading', 'subject', 'h1']
        for field in title_fields:
            if field in content and isinstance(content[field], str) and content[field].strip():
                return content[field].strip()
        return ""
    
    def _get_page_title(self, page: Page) -> str:
        """Extract a title from a Page object.
        
        Args:
            page: Page object
            
        Returns:
            Title string or empty string if no title found
        """
        # Try to get title from page.data
        if hasattr(page, 'data') and isinstance(page.data, dict):
            title = self._get_title(page.data)
            if title:
                return title
        
        # Try to get title from page.title attribute
        if hasattr(page, 'title') and page.title:
            return page.title
        
        # Fall back to URL if available
        if hasattr(page, 'url') and page.url:
            return f"Page: {page.url}"
        
        return "Untitled Page"
    
    def _format_field_name(self, name: str) -> str:
        """Format a field name for display in Markdown.
        
        Args:
            name: Field name
            
        Returns:
            Formatted field name
        """
        # Convert snake_case or camelCase to Title Case
        # First, handle camelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        # Then, replace underscores with spaces
        name = name.replace('_', ' ')
        # Finally, title case
        return name.title()
    
    def _format_field_value(self, field_name: str, value: Any) -> str:
        """Format a field value for Markdown.
        
        Handles different types of values appropriately.
        
        Args:
            field_name: Name of the field
            value: Value to format
            
        Returns:
            Formatted value as Markdown
        """
        # Use custom formatter if available
        if field_name in self.field_formatter and callable(self.field_formatter[field_name]):
            return self.field_formatter[field_name](value)
        
        # Handle different types
        if value is None:
            return "*None*"
        
        elif isinstance(value, (int, float, bool)):
            return f"`{value}`"
        
        elif isinstance(value, str):
            # Check if it's a long text that might be better as a quoted block
            if len(value) > 80 or '\n' in value:
                # Ensure each line starts with >
                value = "\n> ".join(value.split('\n'))
                return f"> {value}"
            return value
        
        elif isinstance(value, list):
            return self._format_list(value)
        
        elif isinstance(value, dict):
            return self._format_dict(value)
        
        elif hasattr(value, '__str__'):
            return str(value)
        
        return f"`{repr(value)}`"
    
    def _format_list(self, items: List[Any]) -> str:
        """Format a list as Markdown.
        
        Args:
            items: List to format
            
        Returns:
            Markdown formatted list
        """
        if not items:
            return "*Empty list*"
        
        # Check if we need to limit the number of items
        if self.max_list_items and len(items) > self.max_list_items:
            displayed_items = items[:self.max_list_items]
            remaining = len(items) - self.max_list_items
            truncation_note = f"\n\n*...and {remaining} more item(s)*"
        else:
            displayed_items = items
            truncation_note = ""
        
        # Format each item
        formatted_items = []
        for item in displayed_items:
            if isinstance(item, dict):
                # For dictionaries, try to make a compact representation
                formatted_item = self._format_dict_inline(item)
            elif isinstance(item, list):
                # For nested lists, indent and add sub-bullets
                formatted_item = self._format_nested_list(item)
            else:
                formatted_item = str(item)
            
            formatted_items.append(f"- {formatted_item}")
        
        return "\n".join(formatted_items) + truncation_note
    
    def _format_nested_list(self, items: List[Any]) -> str:
        """Format a nested list for Markdown.
        
        Args:
            items: Nested list to format
            
        Returns:
            Markdown formatted nested list
        """
        if not items:
            return "*Empty list*"
        
        # Format each item with indentation
        formatted_items = []
        for item in items:
            formatted_items.append(f"  - {item}")
        
        return "\n".join(formatted_items)
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format a dictionary as Markdown.
        
        Args:
            data: Dictionary to format
            
        Returns:
            Markdown formatted dictionary
        """
        if not data:
            return "*Empty dictionary*"
        
        # Format each key-value pair
        formatted_items = []
        for key, value in data.items():
            key_str = self._format_field_name(key)
            if isinstance(value, dict):
                # For nested dictionaries, indent
                value_str = self._format_dict(value).replace('\n', '\n  ')
                formatted_items.append(f"**{key_str}**:\n  {value_str}")
            elif isinstance(value, list):
                # For lists, indent
                value_str = self._format_list(value).replace('\n', '\n  ')
                formatted_items.append(f"**{key_str}**:\n  {value_str}")
            else:
                # For simple values
                value_str = str(value)
                formatted_items.append(f"**{key_str}**: {value_str}")
        
        return "\n".join(formatted_items)
    
    def _format_dict_inline(self, data: Dict[str, Any]) -> str:
        """Format a dictionary in a compact inline form.
        
        Args:
            data: Dictionary to format
            
        Returns:
            Compact inline representation
        """
        if not data:
            return "*Empty*"
        
        # Find a good key to use as a summary (like name, title, id)
        summary_keys = ['name', 'title', 'id', 'key']
        for key in summary_keys:
            if key in data:
                return f"{data[key]} *({len(data)} fields)*"
        
        # No good summary key, just show the number of fields
        return f"*Dictionary with {len(data)} fields*"
    
    def _generate_metadata(self, content: Dict[str, Any]) -> str:
        """Generate metadata section for the content.
        
        Args:
            content: Content dictionary
            
        Returns:
            Markdown formatted metadata
        """
        metadata = []
        
        # Add heading
        metadata.append(f"{'#' * (self.heading_level + 1)} Metadata\n")
        
        # Add field count
        metadata.append(f"**Fields**: {len(content)}")
        
        # Add timestamp
        current_time = datetime.now().strftime(self.timestamp_format)
        metadata.append(f"**Exported**: {current_time}")
        
        return "\n".join(metadata)
    
    def _generate_page_metadata(self, page: Page) -> str:
        """Generate metadata section for a Page object.
        
        Args:
            page: Page object
            
        Returns:
            Markdown formatted metadata
        """
        metadata = []
        
        # Add heading
        metadata.append(f"{'#' * (self.heading_level + 1)} Metadata\n")
        
        # Add page info
        if hasattr(page, 'content_type') and page.content_type:
            metadata.append(f"**Content Type**: {page.content_type}")
        
        if hasattr(page, 'status_code') and page.status_code:
            metadata.append(f"**Status Code**: {page.status_code}")
        
        if hasattr(page, 'depth') and page.depth is not None:
            metadata.append(f"**Depth**: {page.depth}")
        
        # Add field count if page has data
        if hasattr(page, 'data') and isinstance(page.data, dict):
            metadata.append(f"**Fields**: {len(page.data)}")
        
        # Add timestamp
        current_time = datetime.now().strftime(self.timestamp_format)
        metadata.append(f"**Exported**: {current_time}")
        
        return "\n".join(metadata)
    
    def _apply_template(self, content: Dict[str, Any], template: str) -> str:
        """Apply a template to the content.
        
        Args:
            content: Content dictionary
            template: Template string with {field_name} placeholders
            
        Returns:
            Formatted string based on the template
        """
        # Create a formatter dictionary with all values as strings
        formatters = {}
        for key, value in content.items():
            if isinstance(value, (dict, list)):
                formatters[key] = self._format_field_value(key, value)
            else:
                formatters[key] = str(value) if value is not None else ""
        
        # Add metadata as formatters
        formatters['export_timestamp'] = datetime.now().strftime(self.timestamp_format)
        
        try:
            # Replace placeholders with values
            return template.format(**formatters)
        except KeyError as e:
            # Handle missing keys
            return f"Error applying template: {e} not found in content"
    
    def _should_skip_field(self, field_name: str) -> bool:
        """Determine if a field should be skipped based on include/exclude rules.
        
        Args:
            field_name: Name of the field
            
        Returns:
            True if the field should be skipped, False otherwise
        """
        # If include_fields is provided, only include those fields
        if self.include_fields:
            return field_name not in self.include_fields
        
        # Otherwise, skip excluded fields
        return field_name in self.exclude_fields 