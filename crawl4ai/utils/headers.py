"""Utility module for handling request headers and user agents.

This module provides functionality for configuring request headers
and managing user agents for crawlers.
"""
import random
from typing import Dict, List, Optional, Union, Any
import json
from pathlib import Path
import pkg_resources

from crawl4ai.config import get_logger

# Common user agents
COMMON_USER_AGENTS = {
    "chrome_windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "chrome_mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "chrome_linux": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "firefox_windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "firefox_mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "firefox_linux": "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "crawl4ai": "Crawl4AI/0.5.0 (+https://docs.crawl4ai.com/bot)",
}

# Default headers
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}


class UserAgentManager:
    """Manages user agents for crawlers.
    
    This class provides functionality for selecting and rotating user agents.
    """
    
    def __init__(
        self,
        user_agents: Optional[Union[List[str], Dict[str, str]]] = None,
        rotation_strategy: str = "random",
        custom_file: Optional[Union[str, Path]] = None,
    ):
        """Initialize the user agent manager.
        
        Args:
            user_agents: List or dictionary of user agents
            rotation_strategy: Strategy for rotating user agents ('random', 'sequential')
            custom_file: Path to JSON file containing custom user agents
        """
        self.logger = get_logger("utils.headers")
        
        # Initialize user agents
        self.user_agents = {}
        
        # Add common user agents
        self.user_agents.update(COMMON_USER_AGENTS)
        
        # Add custom user agents from file
        if custom_file:
            self._load_from_file(custom_file)
        
        # Add provided user agents
        if user_agents:
            if isinstance(user_agents, list):
                for i, ua in enumerate(user_agents):
                    self.user_agents[f"custom_{i}"] = ua
            elif isinstance(user_agents, dict):
                self.user_agents.update(user_agents)
        
        # Set rotation strategy
        self.rotation_strategy = rotation_strategy
        self._current_index = 0
        
        self.logger.info(f"Initialized user agent manager with {len(self.user_agents)} user agents")
    
    def _load_from_file(self, file_path: Union[str, Path]) -> None:
        """Load user agents from a JSON file.
        
        Args:
            file_path: Path to JSON file
        """
        try:
            with open(file_path, "r") as f:
                custom_agents = json.load(f)
            
            if isinstance(custom_agents, list):
                for i, ua in enumerate(custom_agents):
                    self.user_agents[f"file_{i}"] = ua
            elif isinstance(custom_agents, dict):
                self.user_agents.update(custom_agents)
                
            self.logger.info(f"Loaded user agents from {file_path}")
        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning(f"Failed to load user agents from {file_path}: {str(e)}")
    
    def get_user_agent(self, name: Optional[str] = None) -> str:
        """Get a user agent by name or according to rotation strategy.
        
        Args:
            name: Name of the user agent to retrieve
            
        Returns:
            User agent string
            
        Raises:
            KeyError: If the specified user agent name is not found
        """
        if name:
            if name in self.user_agents:
                return self.user_agents[name]
            else:
                self.logger.warning(f"User agent '{name}' not found, using default")
                return self.user_agents.get("crawl4ai", list(self.user_agents.values())[0])
        
        # Use rotation strategy if no name specified
        if self.rotation_strategy == "random":
            return random.choice(list(self.user_agents.values()))
        else:  # sequential
            user_agent_values = list(self.user_agents.values())
            ua = user_agent_values[self._current_index]
            self._current_index = (self._current_index + 1) % len(user_agent_values)
            return ua
    
    def get_all_user_agents(self) -> Dict[str, str]:
        """Get all available user agents.
        
        Returns:
            Dictionary of user agent names and values
        """
        return self.user_agents.copy()
    
    def add_user_agent(self, name: str, user_agent: str) -> None:
        """Add a new user agent.
        
        Args:
            name: Name to identify the user agent
            user_agent: User agent string
        """
        self.user_agents[name] = user_agent


def create_headers(
    user_agent: Optional[str] = None,
    additional_headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    referer: Optional[str] = None,
) -> Dict[str, str]:
    """Create headers for HTTP requests.
    
    Args:
        user_agent: User agent string
        additional_headers: Additional headers to include
        cookies: Cookies to include in the Cookie header
        referer: Referer URL
        
    Returns:
        Dictionary of HTTP headers
    """
    # Start with default headers
    headers = DEFAULT_HEADERS.copy()
    
    # Add user agent if provided
    if user_agent:
        headers["User-Agent"] = user_agent
    
    # Add referer if provided
    if referer:
        headers["Referer"] = referer
    
    # Add cookies if provided
    if cookies:
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        headers["Cookie"] = cookie_str
    
    # Add additional headers
    if additional_headers:
        headers.update(additional_headers)
    
    return headers 