"""Environment variable configuration for Crawl4AI framework.

This module provides utilities for loading configuration from environment variables
with support for dotenv files and type casting.
"""
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Set, TypeVar, Type, cast, get_type_hints
from dotenv import load_dotenv

from crawl4ai.core.exceptions import ConfigurationError

# Type variable for type casting
T = TypeVar('T')


def load_env_file(env_file: Optional[Union[str, Path]] = None) -> None:
    """Load environment variables from a .env file.
    
    Args:
        env_file: Path to .env file. If None, will look for .env in current directory.
    """
    if env_file:
        env_path = Path(env_file)
        if not env_path.exists():
            raise ConfigurationError(f"Environment file not found: {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        # Default to .env in current directory
        load_dotenv()


def get_env(
    key: str, 
    default: Any = None, 
    required: bool = False, 
    cast_type: Optional[Type[T]] = None
) -> Any:
    """Get environment variable with type casting.
    
    Args:
        key: Environment variable key
        default: Default value if key is not found
        required: Whether the key is required
        cast_type: Type to cast the value to
        
    Returns:
        The environment variable value, cast to the specified type
        
    Raises:
        ConfigurationError: If the key is required but not found or if casting fails
    """
    value = os.environ.get(key)
    
    if value is None:
        if required:
            raise ConfigurationError(f"Required environment variable not found: {key}")
        return default
    
    # If no cast type is specified, return the raw value
    if cast_type is None:
        return value
    
    # Handle special type casting
    try:
        if cast_type is bool:
            return value.lower() in ('true', 'yes', '1', 'y', 'on')
        elif cast_type is int:
            return int(value)
        elif cast_type is float:
            return float(value)
        elif cast_type is list or cast_type is List:
            return json.loads(value) if value.startswith('[') else value.split(',')
        elif cast_type is dict or cast_type is Dict:
            return json.loads(value)
        elif cast_type is set or cast_type is Set:
            return set(json.loads(value) if value.startswith('[') else value.split(','))
        else:
            # Try direct casting for other types
            return cast_type(value)
    except (ValueError, json.JSONDecodeError) as e:
        raise ConfigurationError(f"Failed to cast environment variable {key} to {cast_type.__name__}: {str(e)}")


class EnvConfig:
    """Base class for configuration objects that can be loaded from environment variables.
    
    Example:
        ```python
        class DatabaseConfig(EnvConfig):
            host: str = "localhost"
            port: int = 5432
            debug: bool = False
            
            class Config:
                env_prefix = "DB_"
        ```
        
        This will look for DB_HOST, DB_PORT, and DB_DEBUG in environment variables.
    """
    
    class Config:
        """Configuration options for EnvConfig."""
        env_prefix = ""
    
    @classmethod
    def from_env(cls):
        """Create an instance from environment variables."""
        config_class = cls.Config
        prefix = getattr(config_class, "env_prefix", "")
        
        # Get type hints for the class
        hints = get_type_hints(cls)
        
        # Create args dictionary
        kwargs = {}
        
        # Get default values from class
        for key, value in cls.__dict__.items():
            if not key.startswith('_') and key != 'Config':
                kwargs[key] = value
        
        # Override with environment variables
        for key, expected_type in hints.items():
            if key.startswith('_') or key == 'Config':
                continue
                
            env_key = f"{prefix}{key.upper()}"
            value = get_env(env_key, cast_type=expected_type)
            
            if value is not None:
                kwargs[key] = value
        
        return cls(**kwargs)
    
    def __init__(self, **kwargs):
        """Initialize with provided values."""
        for key, value in kwargs.items():
            setattr(self, key, value) 