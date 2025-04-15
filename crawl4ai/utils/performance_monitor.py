"""Performance monitoring utilities for crawler types.

This module provides tools for monitoring and comparing the performance
of different crawler types across various metrics.
"""

import time
import psutil
import logging
import statistics
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path


@dataclass
class PerformanceMetrics:
    """Performance metrics for a crawler run."""
    
    # Basic metrics
    crawler_type: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    url: str = ""
    success: bool = True
    error_message: Optional[str] = None
    
    # Page metrics
    pages_crawled: int = 0
    links_found: int = 0
    page_size_bytes: List[int] = field(default_factory=list)
    
    # Time metrics
    response_times: List[float] = field(default_factory=list)
    processing_times: List[float] = field(default_factory=list)
    
    # Memory metrics
    memory_samples: List[float] = field(default_factory=list)
    peak_memory_mb: float = 0.0
    
    # CPU metrics
    cpu_samples: List[float] = field(default_factory=list)
    
    def add_page_metrics(
        self, 
        response_time: float, 
        processing_time: float,
        page_size: int,
        memory_usage: float,
        cpu_usage: float
    ) -> None:
        """Add metrics for a single page crawl.
        
        Args:
            response_time: Time to receive the response in seconds
            processing_time: Time to process the page in seconds
            page_size: Size of the page content in bytes
            memory_usage: Memory usage in MB at time of crawl
            cpu_usage: CPU usage percentage at time of crawl
        """
        self.pages_crawled += 1
        self.response_times.append(response_time)
        self.processing_times.append(processing_time)
        self.page_size_bytes.append(page_size)
        self.memory_samples.append(memory_usage)
        self.cpu_samples.append(cpu_usage)
        
        # Update peak memory
        if memory_usage > self.peak_memory_mb:
            self.peak_memory_mb = memory_usage
    
    def finish(self) -> None:
        """Mark the crawl as finished and calculate final metrics."""
        self.end_time = time.time()
    
    def set_error(self, error_message: str) -> None:
        """Mark the crawl as failed with an error message.
        
        Args:
            error_message: Description of the error
        """
        self.success = False
        self.error_message = error_message
        self.finish()
    
    def add_links(self, link_count: int) -> None:
        """Add number of links found.
        
        Args:
            link_count: Number of links found
        """
        self.links_found += link_count
    
    @property
    def duration(self) -> float:
        """Get the total duration of the crawl in seconds."""
        if self.end_time is None:
            # If not finished, calculate based on current time
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    @property
    def avg_response_time(self) -> Optional[float]:
        """Get the average response time in seconds."""
        if not self.response_times:
            return None
        return statistics.mean(self.response_times)
    
    @property
    def avg_processing_time(self) -> Optional[float]:
        """Get the average processing time in seconds."""
        if not self.processing_times:
            return None
        return statistics.mean(self.processing_times)
    
    @property
    def avg_memory_usage(self) -> Optional[float]:
        """Get the average memory usage in MB."""
        if not self.memory_samples:
            return None
        return statistics.mean(self.memory_samples)
    
    @property
    def avg_cpu_usage(self) -> Optional[float]:
        """Get the average CPU usage percentage."""
        if not self.cpu_samples:
            return None
        return statistics.mean(self.cpu_samples)
    
    @property
    def throughput(self) -> float:
        """Get the throughput in pages per second."""
        if self.duration == 0 or self.pages_crawled == 0:
            return 0.0
        return self.pages_crawled / self.duration
    
    @property
    def avg_page_size(self) -> Optional[float]:
        """Get the average page size in bytes."""
        if not self.page_size_bytes:
            return None
        return statistics.mean(self.page_size_bytes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to a dictionary for serialization."""
        return {
            "crawler_type": self.crawler_type,
            "url": self.url,
            "success": self.success,
            "error_message": self.error_message,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "pages_crawled": self.pages_crawled,
            "links_found": self.links_found,
            "avg_response_time": self.avg_response_time,
            "avg_processing_time": self.avg_processing_time,
            "avg_memory_usage": self.avg_memory_usage,
            "peak_memory_mb": self.peak_memory_mb,
            "avg_cpu_usage": self.avg_cpu_usage,
            "throughput": self.throughput,
            "avg_page_size": self.avg_page_size,
        }


class PerformanceMonitor:
    """Monitor and compare performance of different crawler types."""
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """Initialize the performance monitor.
        
        Args:
            output_dir: Directory to save performance reports
        """
        self.metrics_history: List[PerformanceMetrics] = []
        self.current_metrics: Optional[PerformanceMetrics] = None
        self.logger = logging.getLogger("crawl4ai.utils.performance_monitor")
        
        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.output_dir = None
    
    def start_monitoring(self, crawler_type: str, url: str) -> PerformanceMetrics:
        """Start monitoring a crawl.
        
        Args:
            crawler_type: Type of crawler being used
            url: URL being crawled
            
        Returns:
            PerformanceMetrics object for the crawl
        """
        self.current_metrics = PerformanceMetrics(crawler_type=crawler_type)
        self.current_metrics.url = url
        self.logger.info(f"Started monitoring {crawler_type} crawler for {url}")
        return self.current_metrics
    
    def end_monitoring(self) -> Optional[PerformanceMetrics]:
        """End monitoring the current crawl.
        
        Returns:
            Final metrics for the crawl
        """
        if self.current_metrics:
            self.current_metrics.finish()
            self.metrics_history.append(self.current_metrics)
            self.logger.info(
                f"Ended monitoring {self.current_metrics.crawler_type} crawler "
                f"for {self.current_metrics.url} "
                f"({self.current_metrics.pages_crawled} pages, "
                f"{self.current_metrics.duration:.2f}s)"
            )
            metrics = self.current_metrics
            self.current_metrics = None
            
            # Save metrics to file if output directory is set
            if self.output_dir:
                self._save_metrics(metrics)
                
            return metrics
        return None
    
    def record_page(
        self,
        response_time: float,
        processing_time: float,
        page_size: int,
        links: int
    ) -> None:
        """Record metrics for a page crawl.
        
        Args:
            response_time: Time to receive the response in seconds
            processing_time: Time to process the page in seconds
            page_size: Size of the page content in bytes
            links: Number of links found on the page
        """
        if not self.current_metrics:
            self.logger.warning("Tried to record page metrics but no crawl is being monitored")
            return
            
        # Get current memory and CPU usage
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
        cpu_usage = process.cpu_percent()
        
        # Add metrics
        self.current_metrics.add_page_metrics(
            response_time=response_time,
            processing_time=processing_time,
            page_size=page_size,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage
        )
        
        # Add links
        self.current_metrics.add_links(links)
    
    def record_error(self, error_message: str) -> None:
        """Record an error in the current crawl.
        
        Args:
            error_message: Description of the error
        """
        if not self.current_metrics:
            self.logger.warning("Tried to record error but no crawl is being monitored")
            return
            
        self.current_metrics.set_error(error_message)
        self.metrics_history.append(self.current_metrics)
        self.current_metrics = None
    
    def get_crawler_comparison(self, url: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Compare performance of different crawler types.
        
        Args:
            url: Optional URL to filter metrics by
            
        Returns:
            Dictionary mapping crawler types to their average metrics
        """
        # Filter metrics by URL if specified
        filtered_metrics = self.metrics_history
        if url:
            filtered_metrics = [m for m in filtered_metrics if m.url == url]
            
        # Group metrics by crawler type
        metrics_by_type: Dict[str, List[PerformanceMetrics]] = {}
        for metrics in filtered_metrics:
            if metrics.crawler_type not in metrics_by_type:
                metrics_by_type[metrics.crawler_type] = []
            metrics_by_type[metrics.crawler_type].append(metrics)
        
        # Calculate average metrics for each crawler type
        comparison = {}
        for crawler_type, metrics_list in metrics_by_type.items():
            successful_metrics = [m for m in metrics_list if m.success]
            if not successful_metrics:
                continue
                
            # Calculate averages
            avg_metrics = {
                "count": len(successful_metrics),
                "avg_duration": statistics.mean([m.duration for m in successful_metrics]),
                "avg_throughput": statistics.mean([m.throughput for m in successful_metrics]),
                "avg_memory_usage": statistics.mean([m.avg_memory_usage or 0 for m in successful_metrics]),
                "avg_response_time": statistics.mean([m.avg_response_time or 0 for m in successful_metrics]),
                "success_rate": len(successful_metrics) / len(metrics_list),
            }
            
            comparison[crawler_type] = avg_metrics
            
        return comparison
    
    def _save_metrics(self, metrics: PerformanceMetrics) -> None:
        """Save metrics to a JSON file.
        
        Args:
            metrics: Metrics to save
        """
        if not self.output_dir:
            return
            
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crawler_type = metrics.crawler_type
        url_safe = metrics.url.replace("://", "_").replace("/", "_").replace("?", "_")[:50]
        filename = f"{timestamp}_{crawler_type}_{url_safe}.json"
        filepath = self.output_dir / filename
        
        # Save metrics to file
        with open(filepath, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)
            
        self.logger.info(f"Saved metrics to {filepath}")
    
    def generate_report(self, output_file: Optional[Union[str, Path]] = None) -> str:
        """Generate a performance report for all recorded metrics.
        
        Args:
            output_file: Optional file to save the report
            
        Returns:
            Report as a string
        """
        if not self.metrics_history:
            return "No metrics recorded"
            
        # Get crawler type comparison
        comparison = self.get_crawler_comparison()
        
        # Build report
        report = ["# Crawler Performance Report", ""]
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total metrics recorded: {len(self.metrics_history)}")
        report.append("")
        
        # Add comparison table
        report.append("## Crawler Type Comparison")
        report.append("")
        report.append("| Crawler Type | Count | Success Rate | Avg Duration | Avg Throughput | Avg Memory Usage | Avg Response Time |")
        report.append("| ------------ | ----- | ------------ | ------------ | -------------- | ---------------- | ----------------- |")
        
        for crawler_type, metrics in comparison.items():
            report.append(
                f"| {crawler_type} | "
                f"{metrics['count']} | "
                f"{metrics['success_rate']:.2%} | "
                f"{metrics['avg_duration']:.2f}s | "
                f"{metrics['avg_throughput']:.2f} pages/s | "
                f"{metrics['avg_memory_usage']:.2f} MB | "
                f"{metrics['avg_response_time']:.4f}s |"
            )
        
        # Add individual metrics
        report.append("")
        report.append("## Individual Crawl Metrics")
        report.append("")
        
        for i, metrics in enumerate(self.metrics_history[-10:]):  # Last 10 metrics
            report.append(f"### Crawl {i+1}: {metrics.crawler_type} - {metrics.url}")
            report.append("")
            report.append(f"- **Success:** {'Yes' if metrics.success else 'No'}")
            if not metrics.success and metrics.error_message:
                report.append(f"- **Error:** {metrics.error_message}")
            report.append(f"- **Duration:** {metrics.duration:.2f}s")
            report.append(f"- **Pages Crawled:** {metrics.pages_crawled}")
            report.append(f"- **Throughput:** {metrics.throughput:.2f} pages/s")
            if metrics.avg_response_time:
                report.append(f"- **Avg Response Time:** {metrics.avg_response_time:.4f}s")
            if metrics.avg_memory_usage:
                report.append(f"- **Avg Memory Usage:** {metrics.avg_memory_usage:.2f} MB")
            report.append("")
        
        # Save report to file if specified
        report_str = "\n".join(report)
        if output_file:
            with open(output_file, "w") as f:
                f.write(report_str)
                
        return report_str 