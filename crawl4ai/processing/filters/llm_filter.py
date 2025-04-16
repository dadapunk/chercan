"""LLM-based content filter for Crawl4AI.

This module provides a content filter implementation that uses Large Language Models
to clean, enhance, and transform extracted content.
"""
import json
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable, Set

from crawl4ai.processing.filters.base_filter import BaseContentFilter
from crawl4ai.config import LLMConfig


class LLMContentFilter(BaseContentFilter):
    """Content filter using Large Language Models.
    
    This filter uses LLMs to process and enhance extracted content in various ways:
    - Removing sensitive or personally identifiable information (PII)
    - Summarizing long text
    - Categorizing content
    - Translating content
    - Fixing formatting issues
    - Enhancing descriptions
    - Standardizing data formats
    
    Example:
    ```python
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    content_filter = LLMContentFilter(
        llm_config=llm_config,
        mode="summarize",
        fields=["description", "content"],
        max_length=150
    )
    
    # Apply the filter
    enhanced_data = content_filter.filter(raw_data)
    ```
    """
    
    # Available filter modes
    FILTER_MODES = {
        "summarize": "Summarize long text content",
        "remove_pii": "Remove personally identifiable information",
        "enhance": "Enhance or clarify content",
        "translate": "Translate content to a specified language",
        "categorize": "Categorize content into predefined categories",
        "standardize": "Standardize data formats",
        "clean": "Clean and fix formatting issues",
        "custom": "Custom processing defined by prompt template"
    }
    
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        mode: str = "clean",
        fields: Optional[List[str]] = None,
        language: str = "english",
        max_length: Optional[int] = None,
        categories: Optional[List[str]] = None,
        prompt_template: Optional[str] = None,
        async_processing: bool = False,
        **kwargs
    ):
        """Initialize the LLM content filter.
        
        Args:
            llm_config: Configuration for the LLM provider
            mode: Filter mode (summarize, remove_pii, enhance, translate, etc.)
            fields: List of field names to apply the filter to (None for all)
            language: Target language for translation
            max_length: Maximum length for summarization
            categories: List of categories for categorization
            prompt_template: Custom prompt template for the 'custom' mode
            async_processing: Whether to process fields asynchronously
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        
        # Set up LLM configuration
        self.llm_config = llm_config or LLMConfig()
        
        # Validate and set mode
        if mode not in self.FILTER_MODES and mode != "custom":
            raise ValueError(f"Invalid mode: {mode}. Available modes: {list(self.FILTER_MODES.keys())}")
        self.mode = mode
        
        # Set other parameters
        self.fields = set(fields) if fields else None
        self.language = language
        self.max_length = max_length
        self.categories = categories
        self.prompt_template = prompt_template
        self.async_processing = async_processing
    
    def filter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply LLM-based filtering to the content.
        
        Args:
            content: The content to filter
            
        Returns:
            The filtered/processed content
        """
        if not content:
            return {}
        
        result = content.copy()
        
        # Determine which fields to process
        fields_to_process = self._get_fields_to_process(content)
        
        if self.async_processing:
            # Process fields asynchronously
            try:
                result = asyncio.run(self._process_fields_async(result, fields_to_process))
            except Exception as e:
                # Fall back to synchronous processing if async fails
                for field in fields_to_process:
                    if field in result:
                        result[field] = self._process_field(result[field], field)
        else:
            # Process fields synchronously
            for field in fields_to_process:
                if field in result:
                    result[field] = self._process_field(result[field], field)
        
        return result
    
    async def _process_fields_async(self, content: Dict[str, Any], fields: Set[str]) -> Dict[str, Any]:
        """Process multiple fields asynchronously.
        
        Args:
            content: The content dictionary
            fields: Set of field names to process
            
        Returns:
            Updated content dictionary
        """
        result = content.copy()
        
        # Create a list to hold the coroutines
        tasks = []
        
        for field in fields:
            if field in result:
                tasks.append(self._process_field_async(result[field], field))
        
        # Run all tasks concurrently and get results
        if tasks:
            processed_values = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update the content with processed values
            for i, field in enumerate(fields):
                if i < len(processed_values) and not isinstance(processed_values[i], Exception):
                    result[field] = processed_values[i]
        
        return result
    
    async def _process_field_async(self, value: Any, field_name: str) -> Any:
        """Process a single field asynchronously using the LLM.
        
        Args:
            value: The field value to process
            field_name: The name of the field
            
        Returns:
            The processed value
        """
        # Handle different value types
        if isinstance(value, str):
            # Process text content with LLM
            prompt = self._build_prompt(value, field_name)
            try:
                result = await self.llm_config.call_llm_async(prompt)
                return result.strip()
            except Exception as e:
                # Return original value if LLM processing fails
                return value
                
        elif isinstance(value, list):
            # Process list items
            processed_items = []
            for item in value:
                processed_item = await self._process_field_async(item, field_name)
                processed_items.append(processed_item)
            return processed_items
            
        elif isinstance(value, dict):
            # Process nested dictionary
            processed_dict = {}
            for key, val in value.items():
                processed_dict[key] = await self._process_field_async(val, f"{field_name}.{key}")
            return processed_dict
            
        # Return other types as is
        return value
    
    def _process_field(self, value: Any, field_name: str) -> Any:
        """Process a single field using the LLM.
        
        Args:
            value: The field value to process
            field_name: The name of the field
            
        Returns:
            The processed value
        """
        # Handle different value types
        if isinstance(value, str):
            # Process text content with LLM
            prompt = self._build_prompt(value, field_name)
            try:
                # Use a synchronous version by running the async method in an event loop
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(self.llm_config.call_llm_async(prompt))
                loop.close()
                return result.strip()
            except Exception as e:
                # Return original value if LLM processing fails
                return value
                
        elif isinstance(value, list):
            # Process list items
            return [self._process_field(item, field_name) for item in value]
            
        elif isinstance(value, dict):
            # Process nested dictionary
            processed_dict = {}
            for key, val in value.items():
                processed_dict[key] = self._process_field(val, f"{field_name}.{key}")
            return processed_dict
            
        # Return other types as is
        return value
    
    def _get_fields_to_process(self, content: Dict[str, Any]) -> Set[str]:
        """Determine which fields to process based on filter configuration.
        
        Args:
            content: The content dictionary
            
        Returns:
            Set of field names to process
        """
        if self.fields is not None:
            # Use specified fields that exist in the content
            return {field for field in self.fields if field in content}
        else:
            # Process all string fields by default
            return {key for key, value in content.items() 
                   if isinstance(value, str) or isinstance(value, list) or isinstance(value, dict)}
    
    def _build_prompt(self, text: str, field_name: str) -> str:
        """Build a prompt for the LLM based on the filter mode.
        
        Args:
            text: The text to process
            field_name: The name of the field
            
        Returns:
            A prompt for the LLM
        """
        if self.mode == "custom" and self.prompt_template:
            # Use the custom prompt template
            return self.prompt_template.format(
                text=text,
                field=field_name,
                max_length=self.max_length or "appropriate",
                language=self.language,
                categories=", ".join(self.categories) if self.categories else "appropriate categories"
            )
        
        # Build a prompt based on the mode
        if self.mode == "summarize":
            max_length = f" in {self.max_length} words or less" if self.max_length else ""
            return f"Summarize the following text{max_length}. Preserve the key information while making it concise: {text}"
            
        elif self.mode == "remove_pii":
            return f"Remove all personally identifiable information (PII) from the following text, replacing it with appropriate placeholders: {text}"
            
        elif self.mode == "enhance":
            return f"Enhance the following {field_name} by improving clarity, fixing grammar, and enriching the description: {text}"
            
        elif self.mode == "translate":
            return f"Translate the following text to {self.language}: {text}"
            
        elif self.mode == "categorize":
            categories_list = ", ".join(self.categories) if self.categories else "appropriate categories"
            return f"Categorize the following content into one of these categories: {categories_list}. Return only the category name: {text}"
            
        elif self.mode == "standardize":
            return f"Standardize the format of the following {field_name} using common data formatting practices: {text}"
            
        else:  # "clean" mode or fallback
            return f"Clean the following text by removing any HTML tags, fixing formatting issues, and ensuring proper punctuation: {text}" 