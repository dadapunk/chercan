"""Performance monitoring middleware for crawlers.

This module provides middleware that can be added to crawlers to record
performance metrics and compare different crawler types.
"""

import time
from typing import Optional

from crawl4ai.middleware import BaseMiddleware
from crawl4ai.models import Request, Response
from crawl4ai.utils.performance_monitor import PerformanceMonitor


class PerformanceMonitorMiddleware(BaseMiddleware):
    """Middleware for monitoring crawler performance metrics.
    
    This middleware records performance metrics for each request and response,
    including response time, processing time, memory usage, and more.
    
    Example usage:
    ```python
    # Create a performance monitor
    monitor = PerformanceMonitor(output_dir="performance_reports")
    
    # Create the middleware
    middleware = PerformanceMonitorMiddleware(
        monitor=monitor,
        crawler_type="http"
    )
    
    # Add to a crawler
    crawler.add_middleware(middleware)
    ```
    """
    
    def __init__(
        self,
        monitor: Optional[PerformanceMonitor] = None,
        crawler_type: str = "unknown",
        auto_generate_report: bool = True,
        report_output_file: Optional[str] = None
    ):
        """Initialize the performance monitoring middleware.
        
        Args:
            monitor: PerformanceMonitor instance to use (creates a new one if None)
            crawler_type: Type of crawler being monitored
            auto_generate_report: Whether to automatically generate a report when done
            report_output_file: File to save the report to (if auto_generate_report is True)
        """
        self.monitor = monitor or PerformanceMonitor()
        self.crawler_type = crawler_type
        self.auto_generate_report = auto_generate_report
        self.report_output_file = report_output_file
        
    async def before_request(self, request: Request) -> Request:
        """Record the start of a request.
        
        Args:
            request: The request being made
            
        Returns:
            The request object (unmodified)
        """
        # Start monitoring if this is the first request
        if not self.monitor.current_metrics:
            self.monitor.start_monitoring(self.crawler_type, request.url)
        
        # Store request start time
        request.metadata["perf_start_time"] = time.time()
        
        return request
    
    async def on_response(self, response: Response) -> Response:
        """Record metrics for a completed request/response.
        
        Args:
            response: The response received
            
        Returns:
            The response object (unmodified)
        """
        # Skip if no monitoring is active
        if not self.monitor.current_metrics:
            return response
        
        # Calculate response time
        start_time = response.request.metadata.get("perf_start_time", time.time())
        response_time = time.time() - start_time
        
        # Set response processing start time
        response.metadata["perf_processing_start"] = time.time()
        
        return response
    
    async def after_response(self, response: Response) -> Response:
        """Record metrics after response processing is complete.
        
        Args:
            response: The processed response
            
        Returns:
            The response object (unmodified)
        """
        # Skip if no monitoring is active
        if not self.monitor.current_metrics:
            return response
        
        # Calculate processing time
        processing_start = response.metadata.get("perf_processing_start", time.time())
        processing_time = time.time() - processing_start
        
        # Calculate response time (if not already done)
        start_time = response.request.metadata.get("perf_start_time", time.time())
        response_time = time.time() - start_time - processing_time
        
        # Get page size
        page_size = len(getattr(response, "content", ""))
        if not page_size and hasattr(response, "text"):
            page_size = len(response.text)
        if not page_size and hasattr(response, "html"):
            page_size = len(response.html)
        if not page_size and hasattr(response, "raw"):
            page_size = len(response.raw)
        
        # Get link count
        link_count = len(getattr(response, "links", []))
        
        # Record metrics
        self.monitor.record_page(
            response_time=response_time,
            processing_time=processing_time,
            page_size=page_size,
            links=link_count
        )
        
        return response
    
    async def on_error(self, error: Exception, request: Optional[Request] = None) -> None:
        """Record errors that occur during crawling.
        
        Args:
            error: The exception that occurred
            request: The request that caused the error (if available)
        """
        # Skip if no monitoring is active
        if not self.monitor.current_metrics:
            return
        
        # Record the error
        self.monitor.record_error(str(error))
    
    def end_monitoring(self) -> None:
        """End monitoring and generate a report if configured to do so."""
        metrics = self.monitor.end_monitoring()
        
        if self.auto_generate_report and metrics:
            self.monitor.generate_report(self.report_output_file) 