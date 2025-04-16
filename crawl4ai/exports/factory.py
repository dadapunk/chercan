"""Exporter factory for Crawl4AI.

This module provides a factory for creating and selecting exporters
based on the file format and export needs.
"""
from typing import Dict, List, Any, Optional, Union, Type, Callable
from enum import Enum
import os
from pathlib import Path

from crawl4ai.exports.base_exporter import BaseExporter
from crawl4ai.exports.markdown_exporter import MarkdownExporter
from crawl4ai.exports.json_exporter import JSONExporter
from crawl4ai.exports.html_exporter import HTMLExporter
from crawl4ai.exports.csv_exporter import CSVExporter
from crawl4ai.models import Page, CrawlResult


class ExportFormat(Enum):
    """Enum for different export formats."""
    
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"
    CSV = "csv"


class ExporterFactory:
    """Factory for creating and selecting exporters.
    
    This class provides methods for creating different types of exporters
    and selecting the appropriate exporter based on the export format.
    
    Example:
    ```python
    # Create a specific exporter
    json_exporter = ExporterFactory.create(ExportFormat.JSON, indent=2)
    
    # Create an exporter based on file extension
    exporter = ExporterFactory.create_for_file("output.csv", delimiter=",")
    
    # Create an exporter with default settings
    exporter = ExporterFactory.get_default_exporter("json")
    
    # Export data with automatic format detection
    ExporterFactory.export_to_file(crawl_result, "data.json")
    ```
    """
    
    _exporter_registry = {
        ExportFormat.MARKDOWN: MarkdownExporter,
        ExportFormat.JSON: JSONExporter,
        ExportFormat.HTML: HTMLExporter,
        ExportFormat.CSV: CSVExporter,
    }
    
    _extension_map = {
        ".md": ExportFormat.MARKDOWN,
        ".markdown": ExportFormat.MARKDOWN,
        ".json": ExportFormat.JSON,
        ".html": ExportFormat.HTML,
        ".htm": ExportFormat.HTML,
        ".csv": ExportFormat.CSV,
    }
    
    @classmethod
    def create(
        cls,
        export_format: Union[ExportFormat, str],
        **kwargs
    ) -> BaseExporter:
        """Create an exporter instance of the specified type.
        
        Args:
            export_format: Type of exporter to create
            **kwargs: Configuration options for the exporter
            
        Returns:
            An instance of the requested exporter type
            
        Raises:
            ValueError: If the export format is invalid or configuration is incorrect
        """
        # Convert string to enum if necessary
        if isinstance(export_format, str):
            try:
                export_format = ExportFormat(export_format.lower())
            except ValueError:
                valid_formats = [f.value for f in ExportFormat]
                raise ValueError(
                    f"Invalid export format: {export_format}. "
                    f"Valid formats are: {', '.join(valid_formats)}"
                )
        
        # Get the exporter class
        if export_format not in cls._exporter_registry:
            valid_formats = [f.value for f in ExportFormat]
            raise ValueError(
                f"Invalid export format: {export_format}. "
                f"Valid formats are: {', '.join(valid_formats)}"
            )
        
        exporter_class = cls._exporter_registry[export_format]
        
        # Create and return the exporter instance
        try:
            return exporter_class(**kwargs)
        except TypeError as e:
            raise ValueError(f"Invalid configuration for {export_format.value} exporter: {str(e)}")
    
    @classmethod
    def create_for_file(cls, file_path: Union[str, Path], **kwargs) -> BaseExporter:
        """Create an exporter based on the file extension.
        
        Args:
            file_path: Path to the output file
            **kwargs: Configuration options for the exporter
            
        Returns:
            An instance of the appropriate exporter type
            
        Raises:
            ValueError: If the file extension is not supported
        """
        file_path = str(file_path)
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() not in cls._extension_map:
            valid_extensions = list(cls._extension_map.keys())
            raise ValueError(
                f"Unsupported file extension: {ext}. "
                f"Supported extensions are: {', '.join(valid_extensions)}"
            )
        
        export_format = cls._extension_map[ext.lower()]
        return cls.create(export_format, **kwargs)
    
    @classmethod
    def get_default_exporter(cls, format_hint: Optional[str] = None) -> BaseExporter:
        """Get a default exporter for general use.
        
        Args:
            format_hint: Optional hint for the desired format
            
        Returns:
            An exporter instance
        """
        if format_hint:
            try:
                return cls.create(format_hint)
            except ValueError:
                # Fall back to JSON if the hint is invalid
                pass
        
        # Default to JSON exporter
        return cls.create(ExportFormat.JSON)
    
    @classmethod
    def register_exporter(
        cls,
        export_format: Union[ExportFormat, str],
        exporter_class: Type[BaseExporter],
        file_extensions: Optional[List[str]] = None
    ) -> None:
        """Register a new exporter type.
        
        Args:
            export_format: Format identifier for the exporter
            exporter_class: Exporter class to register
            file_extensions: Optional list of file extensions to associate with this format
            
        Raises:
            ValueError: If the export format is already registered
        """
        # Convert string to enum if necessary
        if isinstance(export_format, str):
            # Create a new enum value for the format
            export_format = Enum('ExportFormat', {export_format.upper(): export_format.lower()})[export_format.upper()]
        
        if export_format in cls._exporter_registry:
            raise ValueError(f"Export format {export_format.value} is already registered")
        
        cls._exporter_registry[export_format] = exporter_class
        
        # Register file extensions if provided
        if file_extensions:
            for ext in file_extensions:
                if not ext.startswith('.'):
                    ext = f".{ext}"
                cls._extension_map[ext.lower()] = export_format
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get a list of supported export formats.
        
        Returns:
            List of export format names
        """
        return [f.value for f in cls._exporter_registry.keys()]
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get a list of supported file extensions.
        
        Returns:
            List of file extensions
        """
        return list(cls._extension_map.keys())
    
    @classmethod
    def export_to_file(
        cls,
        content: Union[Dict[str, Any], Page, List[Dict[str, Any]], List[Page], CrawlResult],
        file_path: Union[str, Path],
        **kwargs
    ) -> bool:
        """Export content to a file with automatic format detection.
        
        Args:
            content: Content to export
            file_path: Path to the output file
            **kwargs: Additional configuration for the exporter
            
        Returns:
            True if the export was successful, False otherwise
        """
        try:
            exporter = cls.create_for_file(file_path, **kwargs)
            return exporter.save_to_file(content, file_path)
        except Exception as e:
            print(f"Error exporting to file: {str(e)}")
            return False
    
    @classmethod
    def get_recommended_format(cls, content_type: str) -> ExportFormat:
        """Get the recommended export format for a given content type.
        
        Args:
            content_type: Content MIME type
            
        Returns:
            Recommended export format
        """
        content_type = content_type.lower()
        
        if 'json' in content_type:
            return ExportFormat.JSON
        elif 'html' in content_type or 'xml' in content_type:
            return ExportFormat.HTML
        elif 'csv' in content_type or 'text/plain' in content_type:
            return ExportFormat.CSV
        else:
            # Default to Markdown for unknown content types
            return ExportFormat.MARKDOWN 