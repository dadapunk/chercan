"""Logging configuration for Crawl4AI framework.

This module provides a consistent logging setup for the entire framework.
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union

from .settings import LOG_DIR, LOG_LEVEL


def get_log_level(level_name: str) -> int:
    """Convert log level name to logging module constant.
    
    Args:
        level_name: String representation of log level (e.g., 'INFO', 'DEBUG')
        
    Returns:
        Integer value of the log level
    """
    level_map = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }
    return level_map.get(level_name.upper(), logging.INFO)


def setup_logging(
    name: str = "crawl4ai",
    level: Optional[Union[str, int]] = None,
    log_file: Optional[Union[str, Path]] = None,
    log_to_console: bool = True,
    log_format: Optional[str] = None,
    propagate: bool = False,
) -> logging.Logger:
    """Set up logging for the application.
    
    Args:
        name: Logger name
        level: Log level (e.g., 'INFO', 'DEBUG')
        log_file: Path to log file (if None, will use default based on logger name)
        log_to_console: Whether to log to console
        log_format: Log format string
        propagate: Whether to propagate logs to parent loggers
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Don't duplicate handlers
    if logger.handlers:
        return logger
    
    # Determine log level
    if level is None:
        level = LOG_LEVEL
    if isinstance(level, str):
        level = get_log_level(level)
    
    logger.setLevel(level)
    logger.propagate = propagate
    
    # Define format
    if log_format is None:
        log_format = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    formatter = logging.Formatter(log_format)
    
    # Create console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Create file handler if requested or using default
    if log_file is None:
        # Create log directory if it doesn't exist
        os.makedirs(LOG_DIR, exist_ok=True)
        log_file = LOG_DIR / f"{name}.log"
    
    # Create the file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Create the main logger for the framework
logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.
    
    This will create a child logger of the main crawl4ai logger.
    
    Args:
        name: Logger name (will be prefixed with 'crawl4ai.')
        
    Returns:
        Logger instance
    """
    if not name.startswith("crawl4ai."):
        name = f"crawl4ai.{name}"
    return logging.getLogger(name) 