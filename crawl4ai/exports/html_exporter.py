"""HTML exporter for Crawl4AI.

This module provides functionality for exporting crawled content
into HTML format.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Iterable
import os
import html
from datetime import datetime

from crawl4ai.exports.base_exporter import BaseExporter
from crawl4ai.models import Page


class HTMLExporter(BaseExporter):
    """Exporter for HTML format.
    
    This class converts crawled content into well-formatted HTML
    that can be viewed in web browsers, used for documentation, 
    or integrated into web applications.
    
    Example:
    ```python
    # Create an HTML exporter
    exporter = HTMLExporter(include_metadata=True, theme='light')
    
    # Export content to HTML
    html_content = exporter.export_content(content)
    
    # Save to a file
    exporter.save_to_file(content, "output.html")
    ```
    """
    
    def __init__(
        self,
        include_metadata: bool = True,
        include_url: bool = True,
        include_stylesheet: bool = True,
        theme: str = 'light',
        title_template: str = "{title} - Crawl4AI Export",
        max_list_items: Optional[int] = None,
        max_table_rows: Optional[int] = None,
        field_formatter: Optional[Dict[str, Callable[[Any], str]]] = None,
        exclude_fields: Optional[List[str]] = None,
        include_fields: Optional[List[str]] = None,
        custom_head: Optional[str] = None,
        timestamp_format: str = "%Y-%m-%d %H:%M:%S",
        **kwargs
    ):
        """Initialize the HTML exporter.
        
        Args:
            include_metadata: Whether to include metadata in the output
            include_url: Whether to include the URL in the output
            include_stylesheet: Whether to include default CSS styling
            theme: Color theme for styling ('light' or 'dark')
            title_template: Template for the HTML title
            max_list_items: Maximum number of items to include in lists
            max_table_rows: Maximum number of rows to include in tables
            field_formatter: Custom formatters for specific fields
            exclude_fields: Fields to exclude from the output
            include_fields: Only include these fields (if provided)
            custom_head: Custom HTML to include in the <head> section
            timestamp_format: Format for timestamps
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.include_metadata = include_metadata
        self.include_url = include_url
        self.include_stylesheet = include_stylesheet
        self.theme = theme.lower()
        self.title_template = title_template
        self.max_list_items = max_list_items
        self.max_table_rows = max_table_rows
        self.field_formatter = field_formatter or {}
        self.exclude_fields = set(exclude_fields or [])
        self.include_fields = set(include_fields or [])
        self.custom_head = custom_head
        self.timestamp_format = timestamp_format
    
    def export_content(self, content: Dict[str, Any]) -> str:
        """Export a single content dictionary to HTML.
        
        Args:
            content: Dictionary containing the content to export
            
        Returns:
            HTML representation of the content
        """
        if not content:
            return self._generate_html_document("", "Empty Content")
        
        # Extract title for the HTML document
        doc_title = self._get_title(content) or "Crawl4AI Export"
        
        # Start with an empty HTML body
        html_body = []
        
        # Add title if available
        title = self._get_title(content)
        if title:
            html_body.append(f'<h1 class="content-title">{html.escape(title)}</h1>')
        
        # Process each field
        html_body.append('<div class="content-fields">')
        for field_name, value in content.items():
            # Skip excluded fields or fields not in include_fields if provided
            if self._should_skip_field(field_name):
                continue
            
            # Format the field name
            field_heading = self._format_field_name(field_name)
            html_body.append(f'<div class="field-group" data-field="{html.escape(field_name)}">')
            html_body.append(f'<h2 class="field-name">{html.escape(field_heading)}</h2>')
            
            # Format the field value
            field_value = self._format_field_value(field_name, value)
            html_body.append(f'<div class="field-value">{field_value}</div>')
            html_body.append('</div>')
        
        html_body.append('</div>')
        
        # Add metadata if required
        if self.include_metadata:
            html_body.append(self._generate_metadata(content))
        
        # Generate the complete HTML document
        return self._generate_html_document("\n".join(html_body), doc_title)
    
    def export_page(self, page: Page) -> str:
        """Export a Page object to HTML.
        
        Args:
            page: Page object to export
            
        Returns:
            HTML representation of the page
        """
        # Extract title for the HTML document
        doc_title = self._get_page_title(page)
        
        # Start with an empty HTML body
        html_body = []
        
        # Add title if available
        title = self._get_page_title(page)
        if title:
            html_body.append(f'<h1 class="page-title">{html.escape(title)}</h1>')
        
        # Add URL if available and configured
        if self.include_url and hasattr(page, 'url') and page.url:
            html_body.append(f'<div class="page-url"><strong>URL:</strong> <a href="{html.escape(page.url)}" target="_blank">{html.escape(page.url)}</a></div>')
        
        # Add content data if available
        if hasattr(page, 'data') and isinstance(page.data, dict):
            html_body.append('<div class="page-data">')
            # Process each field in the data
            for field_name, value in page.data.items():
                # Skip excluded fields or fields not in include_fields if provided
                if self._should_skip_field(field_name):
                    continue
                
                # Format the field name
                field_heading = self._format_field_name(field_name)
                html_body.append(f'<div class="field-group" data-field="{html.escape(field_name)}">')
                html_body.append(f'<h2 class="field-name">{html.escape(field_heading)}</h2>')
                
                # Format the field value
                field_value = self._format_field_value(field_name, value)
                html_body.append(f'<div class="field-value">{field_value}</div>')
                html_body.append('</div>')
            
            html_body.append('</div>')
        
        # Add page metadata if required
        if self.include_metadata:
            html_body.append(self._generate_page_metadata(page))
        
        # Generate the complete HTML document
        return self._generate_html_document("\n".join(html_body), doc_title)
    
    def _join_multiple_exports(self, exports: List[str]) -> str:
        """Join multiple HTML exports into a single HTML document.
        
        Args:
            exports: List of HTML strings
            
        Returns:
            Combined HTML document
        """
        if not exports:
            return self._generate_html_document("", "Empty Export")
        
        # Extract the body content from each HTML export
        bodies = []
        for export in exports:
            # Simple extraction of body content using string operations
            body_start = export.find("<body>")
            body_end = export.find("</body>")
            if body_start > 0 and body_end > 0:
                body_content = export[body_start + 6:body_end].strip()
                bodies.append(f'<div class="export-item">{body_content}</div>')
                bodies.append('<hr class="export-separator">')
        
        # Remove the last separator
        if bodies and bodies[-1] == '<hr class="export-separator">':
            bodies.pop()
        
        # Combine and create a new HTML document
        return self._generate_html_document("\n".join(bodies), "Multiple Exports - Crawl4AI")
    
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
        """Format a field name for display in HTML.
        
        Args:
            name: Field name
            
        Returns:
            Formatted field name
        """
        # Convert snake_case or camelCase to Title Case
        # Replace underscores with spaces
        name = name.replace('_', ' ')
        # Handle camelCase
        import re
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        # Title case
        return name.title()
    
    def _format_field_value(self, field_name: str, value: Any) -> str:
        """Format a field value for HTML.
        
        Handles different types of values appropriately.
        
        Args:
            field_name: Name of the field
            value: Value to format
            
        Returns:
            Formatted value as HTML
        """
        # Use custom formatter if available
        if field_name in self.field_formatter and callable(self.field_formatter[field_name]):
            return self.field_formatter[field_name](value)
        
        # Handle different types
        if value is None:
            return '<span class="null-value">None</span>'
        
        elif isinstance(value, (int, float, bool)):
            return f'<code class="primitive-value">{html.escape(str(value))}</code>'
        
        elif isinstance(value, str):
            # Check if it's a long text
            if len(value) > 100 or '\n' in value:
                # Format as a pre block for better readability
                return f'<pre class="text-block">{html.escape(value)}</pre>'
            return f'<span class="text-value">{html.escape(value)}</span>'
        
        elif isinstance(value, list):
            return self._format_list(value)
        
        elif isinstance(value, dict):
            return self._format_dict(value)
        
        elif hasattr(value, '__str__'):
            return f'<span class="object-value">{html.escape(str(value))}</span>'
        
        return f'<code class="unknown-value">{html.escape(repr(value))}</code>'
    
    def _format_list(self, items: List[Any]) -> str:
        """Format a list as HTML.
        
        Args:
            items: List to format
            
        Returns:
            HTML formatted list
        """
        if not items:
            return '<span class="empty-list">Empty list</span>'
        
        # Check if we need to limit the number of items
        if self.max_list_items and len(items) > self.max_list_items:
            displayed_items = items[:self.max_list_items]
            remaining = len(items) - self.max_list_items
            truncation_note = f'<div class="truncation-note">...and {remaining} more item(s)</div>'
        else:
            displayed_items = items
            truncation_note = ""
        
        # Format list as HTML unordered list
        html_items = ['<ul class="data-list">']
        for item in displayed_items:
            if isinstance(item, dict):
                # For dictionaries in a list, format them inline
                formatted_item = self._format_dict_inline(item)
            elif isinstance(item, list):
                # For nested lists, format recursively
                formatted_item = self._format_list(item)
            else:
                # For primitive types, just convert to string and escape
                formatted_item = html.escape(str(item))
            
            html_items.append(f'<li class="list-item">{formatted_item}</li>')
        
        html_items.append('</ul>')
        if truncation_note:
            html_items.append(truncation_note)
        
        return "\n".join(html_items)
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format a dictionary as HTML.
        
        Args:
            data: Dictionary to format
            
        Returns:
            HTML formatted dictionary
        """
        if not data:
            return '<span class="empty-dict">Empty dictionary</span>'
        
        # Format as a definition list with key-value pairs
        html_parts = ['<dl class="data-dict">']
        for key, value in data.items():
            key_str = self._format_field_name(key)
            html_parts.append(f'<dt class="dict-key">{html.escape(key_str)}</dt>')
            
            # Format the value based on its type
            if isinstance(value, dict):
                value_str = self._format_dict(value)
            elif isinstance(value, list):
                value_str = self._format_list(value)
            else:
                # Use the generic field value formatter
                value_str = self._format_field_value(key, value)
            
            html_parts.append(f'<dd class="dict-value">{value_str}</dd>')
        
        html_parts.append('</dl>')
        return "\n".join(html_parts)
    
    def _format_dict_inline(self, data: Dict[str, Any]) -> str:
        """Format a dictionary in a compact inline form.
        
        Args:
            data: Dictionary to format
            
        Returns:
            Compact inline HTML representation
        """
        if not data:
            return '<span class="empty-dict-inline">Empty</span>'
        
        # Find a good key to use as a summary (like name, title, id)
        summary_keys = ['name', 'title', 'id', 'key']
        for key in summary_keys:
            if key in data:
                return f'<span class="dict-summary">{html.escape(str(data[key]))} <small>({len(data)} fields)</small></span>'
        
        # No good summary key, just show the number of fields
        return f'<span class="dict-summary">Dictionary with {len(data)} fields</span>'
    
    def _generate_metadata(self, content: Dict[str, Any]) -> str:
        """Generate metadata section for the content.
        
        Args:
            content: Content dictionary
            
        Returns:
            HTML formatted metadata
        """
        metadata = ['<div class="metadata-section">']
        metadata.append('<h2 class="metadata-header">Metadata</h2>')
        
        metadata.append('<dl class="metadata-list">')
        
        # Add field count
        metadata.append('<dt>Fields</dt>')
        metadata.append(f'<dd>{len(content)}</dd>')
        
        # Add timestamp
        current_time = datetime.now().strftime(self.timestamp_format)
        metadata.append('<dt>Exported</dt>')
        metadata.append(f'<dd>{current_time}</dd>')
        
        metadata.append('</dl>')
        metadata.append('</div>')
        
        return "\n".join(metadata)
    
    def _generate_page_metadata(self, page: Page) -> str:
        """Generate metadata section for a Page object.
        
        Args:
            page: Page object
            
        Returns:
            HTML formatted metadata
        """
        metadata = ['<div class="metadata-section">']
        metadata.append('<h2 class="metadata-header">Metadata</h2>')
        
        metadata.append('<dl class="metadata-list">')
        
        # Add page info
        if hasattr(page, 'content_type') and page.content_type:
            metadata.append('<dt>Content Type</dt>')
            metadata.append(f'<dd>{html.escape(page.content_type)}</dd>')
        
        if hasattr(page, 'status_code') and page.status_code:
            metadata.append('<dt>Status Code</dt>')
            metadata.append(f'<dd>{page.status_code}</dd>')
        
        if hasattr(page, 'depth') and page.depth is not None:
            metadata.append('<dt>Depth</dt>')
            metadata.append(f'<dd>{page.depth}</dd>')
        
        # Add field count if page has data
        if hasattr(page, 'data') and isinstance(page.data, dict):
            metadata.append('<dt>Fields</dt>')
            metadata.append(f'<dd>{len(page.data)}</dd>')
        
        # Add timestamp
        current_time = datetime.now().strftime(self.timestamp_format)
        metadata.append('<dt>Exported</dt>')
        metadata.append(f'<dd>{current_time}</dd>')
        
        metadata.append('</dl>')
        metadata.append('</div>')
        
        return "\n".join(metadata)
    
    def _generate_html_document(self, body_content: str, title: str) -> str:
        """Generate a complete HTML document.
        
        Args:
            body_content: HTML content for the body
            title: Title for the document
            
        Returns:
            Complete HTML document as a string
        """
        # Generate the HTML document with proper structure
        html_title = html.escape(self.title_template.format(title=title))
        
        # Start the HTML document
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            f'<meta charset="UTF-8">',
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'<meta name="generator" content="Crawl4AI HTML Exporter">',
            f'<title>{html_title}</title>'
        ]
        
        # Add stylesheet if enabled
        if self.include_stylesheet:
            html_parts.append(self._get_default_stylesheet())
        
        # Add custom head content if provided
        if self.custom_head:
            html_parts.append(self.custom_head)
        
        # Close head and start body
        html_parts.extend([
            '</head>',
            '<body>',
            '<div class="container">',
            body_content,
            '</div>',
            f'<footer class="exporter-footer">Generated by Crawl4AI on {datetime.now().strftime(self.timestamp_format)}</footer>',
            '</body>',
            '</html>'
        ])
        
        return "\n".join(html_parts)
    
    def _get_default_stylesheet(self) -> str:
        """Get the default CSS stylesheet.
        
        Returns:
            HTML style tag with CSS content
        """
        # Choose the theme colors
        if self.theme == 'dark':
            colors = {
                'bg': '#1e1e1e',
                'text': '#e0e0e0',
                'header_bg': '#2d2d2d',
                'border': '#444',
                'highlight': '#0078d7',
                'code_bg': '#333',
                'link': '#4da6ff',
                'separator': '#555'
            }
        else:  # light theme (default)
            colors = {
                'bg': '#ffffff',
                'text': '#333333',
                'header_bg': '#f5f5f5',
                'border': '#ddd',
                'highlight': '#0078d7',
                'code_bg': '#f8f8f8',
                'link': '#0366d6',
                'separator': '#eee'
            }
        
        # Define the CSS
        css = f"""
        <style>
            /* Basic styling */
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: {colors['text']};
                background-color: {colors['bg']};
                margin: 0;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid {colors['border']};
                border-radius: 5px;
                background-color: {colors['bg']};
            }}
            
            /* Typography */
            h1, h2, h3, h4, h5, h6 {{
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                font-weight: 600;
            }}
            
            h1 {{
                font-size: 1.8em;
                border-bottom: 1px solid {colors['border']};
                padding-bottom: 0.3em;
            }}
            
            h2 {{
                font-size: 1.4em;
                margin-top: 1.5em;
            }}
            
            a {{
                color: {colors['link']};
                text-decoration: none;
            }}
            
            a:hover {{
                text-decoration: underline;
            }}
            
            /* Field styling */
            .field-group {{
                margin-bottom: 20px;
                padding: 10px;
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}
            
            .field-name {{
                margin-top: 0;
                color: {colors['highlight']};
            }}
            
            .field-value {{
                margin-top: 10px;
            }}
            
            /* List styling */
            ul.data-list {{
                padding-left: 20px;
            }}
            
            /* Dictionary styling */
            dl.data-dict {{
                margin: 0;
                padding: 0;
            }}
            
            dt.dict-key {{
                font-weight: bold;
                margin-top: 10px;
            }}
            
            dd.dict-value {{
                margin-left: 20px;
            }}
            
            /* Code blocks */
            code, pre {{
                font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                background-color: {colors['code_bg']};
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 90%;
            }}
            
            pre {{
                padding: 10px;
                overflow: auto;
                margin: 10px 0;
                max-height: 400px;
            }}
            
            /* Special values */
            .null-value {{
                font-style: italic;
                color: #888;
            }}
            
            .empty-list, .empty-dict, .empty-dict-inline {{
                font-style: italic;
                color: #888;
            }}
            
            /* Metadata section */
            .metadata-section {{
                margin-top: 30px;
                padding: 15px;
                background-color: {colors['header_bg']};
                border-radius: 4px;
                border: 1px solid {colors['border']};
            }}
            
            .metadata-header {{
                margin-top: 0;
                font-size: 1.2em;
            }}
            
            .metadata-list {{
                display: grid;
                grid-template-columns: 150px auto;
                gap: 5px;
            }}
            
            .metadata-list dt {{
                font-weight: bold;
            }}
            
            .metadata-list dd {{
                margin: 0;
            }}
            
            /* Export separators */
            hr.export-separator {{
                border: none;
                border-top: 1px solid {colors['separator']};
                margin: 30px 0;
            }}
            
            .export-item {{
                margin-bottom: 20px;
            }}
            
            /* Page info */
            .page-url {{
                margin-bottom: 20px;
            }}
            
            /* Truncation note */
            .truncation-note {{
                font-style: italic;
                color: #888;
                margin-top: 5px;
            }}
            
            /* Footer */
            .exporter-footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 10px;
                border-top: 1px solid {colors['border']};
                font-size: 0.9em;
                color: #777;
            }}
        </style>
        """
        
        return css
    
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