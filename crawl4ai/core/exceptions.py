"""Base exception classes for the Crawl4AI framework.

These exception classes provide a consistent way to handle errors throughout the framework.
"""
from typing import Optional, Any, Dict, List


class Crawl4AIError(Exception):
    """Base exception class for all Crawl4AI-related errors."""

    def __init__(self, message: str, *args: Any) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
            *args: Additional arguments to pass to the base Exception class.
        """
        self.message = message
        super().__init__(message, *args)


class ConfigurationError(Crawl4AIError):
    """Exception raised for configuration-related errors."""
    
    pass


class CrawlerError(Crawl4AIError):
    """Exception raised for general crawler errors."""
    
    pass


class RequestError(CrawlerError):
    """Exception raised for HTTP request errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, url: Optional[str] = None) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
            status_code: The HTTP status code, if applicable.
            url: The URL that caused the error.
        """
        self.status_code = status_code
        self.url = url
        super().__init__(message)


class BrowserError(CrawlerError):
    """Exception raised for browser-related errors."""
    
    pass


class StrategyError(Crawl4AIError):
    """Exception raised for crawling strategy errors."""
    
    pass


class ExtractorError(Crawl4AIError):
    """Exception raised for data extraction errors."""
    
    pass


class FilterError(Crawl4AIError):
    """Exception raised for content filtering errors."""
    
    pass


class ExportError(Crawl4AIError):
    """Exception raised for data export errors."""
    
    def __init__(self, message: str, export_format: Optional[str] = None) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
            export_format: The export format that caused the error.
        """
        self.export_format = export_format
        super().__init__(message)


class ResourceLimitError(Crawl4AIError):
    """Exception raised when resource limits are exceeded."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, limit: Optional[Any] = None) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
            resource_type: The type of resource that was limited.
            limit: The limit that was exceeded.
        """
        self.resource_type = resource_type
        self.limit = limit
        super().__init__(message)


class AuthenticationError(Crawl4AIError):
    """Exception raised for authentication-related errors."""
    
    pass 