"""Strategy factory for creating crawling strategies.

This module provides a factory for creating and selecting different crawling strategies.
"""
from typing import Dict, Any, Optional, Type, List, Callable, Union

from .base import CrawlStrategy
from .bfs import BFSCrawlStrategy
from .dfs import DFSCrawlStrategy
from .best_first import BestFirstCrawlStrategy


class StrategyFactory:
    """Factory for creating crawling strategies.
    
    This factory allows for easy creation and selection of different crawling strategies
    based on a strategy name and configuration options.
    """
    
    # Registry of available strategies
    STRATEGIES = {
        'bfs': BFSCrawlStrategy,
        'breadth_first': BFSCrawlStrategy,
        'dfs': DFSCrawlStrategy,
        'depth_first': DFSCrawlStrategy,
        'best_first': BestFirstCrawlStrategy,
        'best': BestFirstCrawlStrategy,
    }
    
    @classmethod
    def create_strategy(
        cls,
        strategy_name: str,
        **kwargs
    ) -> CrawlStrategy:
        """Create a crawling strategy by name.
        
        Args:
            strategy_name: Name of the strategy to create
            **kwargs: Configuration options for the strategy
            
        Returns:
            Initialized crawling strategy
            
        Raises:
            ValueError: If the strategy name is not recognized
        """
        # Convert to lowercase for case-insensitive matching
        strategy_key = strategy_name.lower()
        
        # Check if strategy exists
        if strategy_key not in cls.STRATEGIES:
            valid_strategies = ', '.join(cls.STRATEGIES.keys())
            raise ValueError(
                f"Unknown strategy: '{strategy_name}'. "
                f"Valid strategies are: {valid_strategies}"
            )
        
        # Get the strategy class
        strategy_class = cls.STRATEGIES[strategy_key]
        
        # Create and return the strategy
        return strategy_class(**kwargs)
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[CrawlStrategy]) -> None:
        """Register a new strategy class.
        
        Args:
            name: Name to register the strategy under
            strategy_class: Strategy class to register
            
        Raises:
            TypeError: If the strategy_class is not a subclass of CrawlStrategy
        """
        if not issubclass(strategy_class, CrawlStrategy):
            raise TypeError(
                f"Strategy class must be a subclass of CrawlStrategy, "
                f"got {strategy_class.__name__}"
            )
        
        # Add both lowercase and original name for flexibility
        cls.STRATEGIES[name.lower()] = strategy_class
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get a list of available strategy names.
        
        Returns:
            List of available strategy names
        """
        # Return unique strategy names (we have aliases, so filter duplicates)
        unique_classes = set(cls.STRATEGIES.values())
        return [s.__name__.replace('CrawlStrategy', '') for s in unique_classes]
    
    @classmethod
    def get_strategy_options(cls, strategy_name: str) -> Dict[str, Any]:
        """Get configuration options for a strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Dictionary of option names and default values
            
        Raises:
            ValueError: If the strategy name is not recognized
        """
        # Convert to lowercase for case-insensitive matching
        strategy_key = strategy_name.lower()
        
        # Check if strategy exists
        if strategy_key not in cls.STRATEGIES:
            valid_strategies = ', '.join(cls.STRATEGIES.keys())
            raise ValueError(
                f"Unknown strategy: '{strategy_name}'. "
                f"Valid strategies are: {valid_strategies}"
            )
        
        # Get the strategy class
        strategy_class = cls.STRATEGIES[strategy_key]
        
        # Create an empty instance to get default values
        empty_instance = strategy_class()
        
        # Get public attributes that don't start with underscore
        options = {
            name: value for name, value in vars(empty_instance).items()
            if not name.startswith('_') and name not in {'visited_urls', 'pages_crawled', 'logger'}
        }
        
        return options 