"""Configuration classes for BrowserConfig and CrawlerRunConfig.

This module provides enhanced configuration handling for Crawl4AI's BrowserConfig and CrawlerRunConfig.
"""
from typing import Dict, List, Optional, Any, Union, Type
from pathlib import Path
import json

from crawl4ai import BrowserConfig, CrawlerRunConfig
from crawl4ai.config.env import EnvConfig
from crawl4ai.core.exceptions import ConfigurationError


class BrowserConfiguration(EnvConfig):
    """Configuration class for BrowserConfig with environment variable support.
    
    This enhances Crawl4AI's BrowserConfig with environment variable loading
    and additional configuration options.
    """
    
    # Browser selection
    browser_name: str = "chromium"
    headless: bool = True
    
    # Timeouts and delays
    timeout: int = 30
    wait_until: str = "networkidle"
    slow_mo: int = 0
    
    # Browser behavior
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: Optional[str] = None
    locale: str = "en-US"
    timezone_id: str = "UTC"
    
    # Privacy and security
    ignore_https_errors: bool = False
    java_script_enabled: bool = True
    
    # Additional options
    extra_http_headers: Optional[Dict[str, str]] = None
    
    class Config:
        """Configuration options for BrowserConfiguration."""
        env_prefix = "BROWSER_"
    
    def to_browser_config(self) -> BrowserConfig:
        """Convert to Crawl4AI's BrowserConfig.
        
        Returns:
            BrowserConfig instance configured with current settings
        """
        # Get all configuration params
        config_params = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                config_params[key] = value
        
        # Remove None values
        config_params = {k: v for k, v in config_params.items() if v is not None}
        
        # Create BrowserConfig
        return BrowserConfig(**config_params)
    
    @classmethod
    def from_json(cls, json_file: Union[str, Path]) -> 'BrowserConfiguration':
        """Load configuration from JSON file.
        
        Args:
            json_file: Path to JSON configuration file
            
        Returns:
            BrowserConfiguration instance
            
        Raises:
            ConfigurationError: If file is not found or contains invalid JSON
        """
        try:
            with open(json_file, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Failed to load browser configuration from {json_file}: {str(e)}")
    
    def to_json(self, json_file: Union[str, Path]) -> None:
        """Save configuration to JSON file.
        
        Args:
            json_file: Path to save configuration
            
        Raises:
            ConfigurationError: If file cannot be written
        """
        try:
            # Create dictionary of all configuration values
            config_data = {}
            for key, value in self.__dict__.items():
                if not key.startswith('_'):
                    config_data[key] = value
            
            # Write to file
            with open(json_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            raise ConfigurationError(f"Failed to save browser configuration to {json_file}: {str(e)}")


class CrawlerConfiguration(EnvConfig):
    """Configuration class for CrawlerRunConfig with environment variable support.
    
    This enhances Crawl4AI's CrawlerRunConfig with environment variable loading
    and additional configuration options.
    """
    
    # Basic crawl settings
    follow_links: bool = False
    max_pages: int = 10
    max_depth: int = 1
    
    # Advanced crawl settings
    retry_count: int = 3
    retry_delay: int = 5
    timeout: int = 30
    
    # Content and filtering
    render_javascript: bool = True
    extract_text: bool = True
    extract_metadata: bool = True
    
    # Link handling
    respect_robots_txt: bool = True
    same_domain_only: bool = True
    include_subdomains: bool = True
    link_patterns_to_include: Optional[List[str]] = None
    link_patterns_to_exclude: Optional[List[str]] = None
    
    # Rate limiting
    rate_limit: Optional[int] = None
    
    # Cache settings
    cache_enabled: bool = False
    cache_dir: Optional[str] = None
    
    class Config:
        """Configuration options for CrawlerConfiguration."""
        env_prefix = "CRAWLER_"
    
    def to_crawler_config(self) -> CrawlerRunConfig:
        """Convert to Crawl4AI's CrawlerRunConfig.
        
        Returns:
            CrawlerRunConfig instance configured with current settings
        """
        # Get all configuration params
        config_params = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                config_params[key] = value
        
        # Remove None values
        config_params = {k: v for k, v in config_params.items() if v is not None}
        
        # Create CrawlerRunConfig
        return CrawlerRunConfig(**config_params)
    
    @classmethod
    def from_json(cls, json_file: Union[str, Path]) -> 'CrawlerConfiguration':
        """Load configuration from JSON file.
        
        Args:
            json_file: Path to JSON configuration file
            
        Returns:
            CrawlerConfiguration instance
            
        Raises:
            ConfigurationError: If file is not found or contains invalid JSON
        """
        try:
            with open(json_file, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Failed to load crawler configuration from {json_file}: {str(e)}")
    
    def to_json(self, json_file: Union[str, Path]) -> None:
        """Save configuration to JSON file.
        
        Args:
            json_file: Path to save configuration
            
        Raises:
            ConfigurationError: If file cannot be written
        """
        try:
            # Create dictionary of all configuration values
            config_data = {}
            for key, value in self.__dict__.items():
                if not key.startswith('_'):
                    config_data[key] = value
            
            # Write to file
            with open(json_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            raise ConfigurationError(f"Failed to save crawler configuration to {json_file}: {str(e)}")


def load_browser_config(
    config_file: Optional[Union[str, Path]] = None,
    env_vars: bool = True,
    **kwargs
) -> BrowserConfig:
    """Load browser configuration from file, environment variables, and/or kwargs.
    
    Args:
        config_file: Path to JSON configuration file (optional)
        env_vars: Whether to load from environment variables
        **kwargs: Override configuration parameters
        
    Returns:
        Configured BrowserConfig instance
    """
    # Start with default configuration
    config = BrowserConfiguration()
    
    # Load from file if specified
    if config_file:
        config = BrowserConfiguration.from_json(config_file)
    
    # Load from environment variables if requested
    if env_vars:
        env_config = BrowserConfiguration.from_env()
        
        # Update with environment values
        for key, value in env_config.__dict__.items():
            if not key.startswith('_'):
                setattr(config, key, value)
    
    # Override with kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    # Convert to BrowserConfig
    return config.to_browser_config()


def load_crawler_config(
    config_file: Optional[Union[str, Path]] = None,
    env_vars: bool = True,
    **kwargs
) -> CrawlerRunConfig:
    """Load crawler configuration from file, environment variables, and/or kwargs.
    
    Args:
        config_file: Path to JSON configuration file (optional)
        env_vars: Whether to load from environment variables
        **kwargs: Override configuration parameters
        
    Returns:
        Configured CrawlerRunConfig instance
    """
    # Start with default configuration
    config = CrawlerConfiguration()
    
    # Load from file if specified
    if config_file:
        config = CrawlerConfiguration.from_json(config_file)
    
    # Load from environment variables if requested
    if env_vars:
        env_config = CrawlerConfiguration.from_env()
        
        # Update with environment values
        for key, value in env_config.__dict__.items():
            if not key.startswith('_'):
                setattr(config, key, value)
    
    # Override with kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    # Convert to CrawlerRunConfig
    return config.to_crawler_config() 