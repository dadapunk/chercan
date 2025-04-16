"""Filter pipeline for Crawl4AI.

This module provides a mechanism to combine multiple content filters
into a unified filter pipeline for complex content processing.
"""
from typing import Any, Dict, List, Optional, Union, Callable

from crawl4ai.processing.filters.base_filter import BaseContentFilter
from crawl4ai.models import Page


class FilterPipeline(BaseContentFilter):
    """Pipeline for combining multiple content filters.
    
    This class allows creating a filter pipeline by combining multiple
    filters into a sequence. Content flows through each filter in order,
    with each filter processing the output of the previous one.
    
    Example:
    ```python
    # Create individual filters
    basic_filter = BasicContentFilter(remove_empty=True, strip_strings=True)
    pruning_filter = PruningContentFilter(rules=[...])
    llm_filter = LLMContentFilter(mode="enhance", fields=["description"])
    
    # Create a pipeline combining them
    pipeline = FilterPipeline([basic_filter, pruning_filter, llm_filter])
    
    # Apply the pipeline
    result = pipeline.filter(content)
    ```
    """
    
    def __init__(
        self,
        filters: Optional[List[BaseContentFilter]] = None,
        name: Optional[str] = None,
        **kwargs
    ):
        """Initialize the filter pipeline.
        
        Args:
            filters: List of filters to apply in sequence
            name: Optional name for the pipeline
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.filters = filters or []
        self.name = name or "FilterPipeline"
    
    def filter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the filter pipeline to the content.
        
        Content flows through each filter in the pipeline in order,
        with each filter processing the output of the previous one.
        
        Args:
            content: The content to filter
            
        Returns:
            The filtered/processed content
        """
        if not content:
            return {}
        
        if not self.filters:
            return content
        
        # Apply each filter in sequence
        result = content
        for filter_obj in self.filters:
            result = filter_obj.filter(result)
        
        return result
    
    def process_page(self, page: Page) -> Page:
        """Process a full Page object through the filter pipeline.
        
        Args:
            page: The Page object to process
            
        Returns:
            The processed Page object
        """
        if not self.filters:
            return page
        
        # Apply each filter's process_page method in sequence
        result = page
        for filter_obj in self.filters:
            result = filter_obj.process_page(result)
        
        return result
    
    def add_filter(self, filter_obj: BaseContentFilter) -> None:
        """Add a filter to the end of the pipeline.
        
        Args:
            filter_obj: The filter to add
        """
        self.filters.append(filter_obj)
    
    def insert_filter(self, index: int, filter_obj: BaseContentFilter) -> None:
        """Insert a filter at a specific position in the pipeline.
        
        Args:
            index: The position to insert the filter
            filter_obj: The filter to insert
        """
        self.filters.insert(index, filter_obj)
    
    def remove_filter(self, index: int) -> Optional[BaseContentFilter]:
        """Remove a filter from the pipeline.
        
        Args:
            index: The index of the filter to remove
            
        Returns:
            The removed filter, or None if the index is out of range
        """
        if 0 <= index < len(self.filters):
            return self.filters.pop(index)
        return None
    
    def clear(self) -> None:
        """Clear all filters from the pipeline."""
        self.filters = []
    
    def __len__(self) -> int:
        """Get the number of filters in the pipeline.
        
        Returns:
            The number of filters
        """
        return len(self.filters)
    
    def __getitem__(self, index: int) -> BaseContentFilter:
        """Get a filter by index.
        
        Args:
            index: The index of the filter
            
        Returns:
            The filter at the specified index
        """
        return self.filters[index]
    
    @classmethod
    def from_filters(cls, *filters: BaseContentFilter, name: Optional[str] = None) -> 'FilterPipeline':
        """Create a pipeline from a sequence of filters.
        
        Args:
            *filters: Filter objects to include in the pipeline
            name: Optional name for the pipeline
            
        Returns:
            A new FilterPipeline instance
        """
        return cls(filters=list(filters), name=name)
    
    @classmethod
    def create_pipeline(
        cls,
        *filters: BaseContentFilter,
        name: Optional[str] = None
    ) -> 'FilterPipeline':
        """Alternative factory method to create a pipeline.
        
        This is an alias for from_filters for more readable code.
        
        Args:
            *filters: Filter objects to include in the pipeline
            name: Optional name for the pipeline
            
        Returns:
            A new FilterPipeline instance
        """
        return cls.from_filters(*filters, name=name)
    
    def __add__(self, other: Union[BaseContentFilter, 'FilterPipeline']) -> 'FilterPipeline':
        """Combine this pipeline with another filter or pipeline.
        
        This allows using the + operator to combine pipelines.
        
        Args:
            other: Another filter or pipeline to append
            
        Returns:
            A new FilterPipeline combining both
            
        Example:
        ```python
        # Create two pipelines
        pipeline1 = FilterPipeline([filter1, filter2])
        pipeline2 = FilterPipeline([filter3, filter4])
        
        # Combine them
        combined = pipeline1 + pipeline2
        
        # Is equivalent to:
        combined = FilterPipeline([filter1, filter2, filter3, filter4])
        ```
        """
        if isinstance(other, FilterPipeline):
            return FilterPipeline(filters=self.filters + other.filters)
        elif isinstance(other, BaseContentFilter):
            return FilterPipeline(filters=self.filters + [other])
        else:
            raise TypeError(f"Cannot add {type(other)} to FilterPipeline")
    
    def get_filter_by_type(self, filter_type: type) -> Optional[BaseContentFilter]:
        """Get the first filter of a specific type.
        
        Args:
            filter_type: The type of filter to find
            
        Returns:
            The first filter of the specified type, or None if not found
        """
        for filter_obj in self.filters:
            if isinstance(filter_obj, filter_type):
                return filter_obj
        return None
    
    def get_filters_by_type(self, filter_type: type) -> List[BaseContentFilter]:
        """Get all filters of a specific type.
        
        Args:
            filter_type: The type of filter to find
            
        Returns:
            List of filters of the specified type
        """
        return [filter_obj for filter_obj in self.filters if isinstance(filter_obj, filter_type)]
    
    def __str__(self) -> str:
        """Get a string representation of the pipeline.
        
        Returns:
            A string representation
        """
        filter_names = [f.__class__.__name__ for f in self.filters]
        return f"{self.name} ({len(self.filters)} filters): {' -> '.join(filter_names)}" 