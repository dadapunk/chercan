"""Global configuration settings for the Crawl4AI framework."""

from pathlib import Path
import os

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PACKAGE_DIR = BASE_DIR / "crawl4ai"

# Default crawler settings
DEFAULT_USER_AGENT = "Crawl4AI/0.5.0 (+https://docs.crawl4ai.com/bot)"
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_RETRY_COUNT = 3
DEFAULT_CRAWL_DELAY = 1.0  # seconds

# Export settings
EXPORT_DIR = BASE_DIR / "exports"
DEFAULT_EXPORT_FORMAT = "markdown"

# Rate limiting
DEFAULT_RATE_LIMIT = 60  # requests per minute

# Logging
LOG_DIR = BASE_DIR / "logs"
LOG_LEVEL = "INFO"
