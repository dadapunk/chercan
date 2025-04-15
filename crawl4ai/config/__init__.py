"""Configuration handling for Crawl4AI framework.

This package provides utilities for configuring the Crawl4AI framework,
including environment variables, logging, and default settings.
"""

from .env import load_env_file, get_env, EnvConfig
from .logging import setup_logging, get_logger, logger
from .settings import *

# Load environment variables from .env file if it exists
load_env_file()

__all__ = [
    'load_env_file',
    'get_env',
    'EnvConfig',
    'setup_logging',
    'get_logger',
    'logger',
]
