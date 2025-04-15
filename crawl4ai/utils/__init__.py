"""Utility modules for Crawl4AI framework.

This package provides various utility functions for the framework.
"""

from .headers import (
    UserAgentManager,
    create_headers,
    COMMON_USER_AGENTS,
    DEFAULT_HEADERS,
)

__all__ = [
    'UserAgentManager',
    'create_headers',
    'COMMON_USER_AGENTS',
    'DEFAULT_HEADERS',
]
