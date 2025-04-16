"""LLM-based extractor for Crawl4AI.

This module provides an extractor that uses Large Language Models to extract
structured data from content based on provided extraction schemas or prompts.
"""
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
import json
import asyncio

from crawl4ai.models import Page
from crawl4ai.extractors.base_extractor import BaseExtractor
from crawl4ai.config import LLMConfig


T = TypeVar('T')


class LLMExtractor(BaseExtractor):
    """Extract data from content using Large Language Models.
    
    This extractor leverages LLMs to extract structured data from text or HTML content
    based on provided extraction schemas or natural language prompts.
    
    Example:
    ```python
    extractor = LLMExtractor(
        schema={
            "title": "string",
            "price": "number",
            "features": "array:string",
            "available": "boolean"
        },
        extraction_prompt="Extract product details from the website."
    )
    
    data = extractor.extract(html_content)
    # {
    #   "title": "Product Name",
    #   "price": 99.99,
    #   "features": ["Feature 1", "Feature 2", "Feature 3"],
    #   "available": true
    # }
    ```
    """
    
    def __init__(
        self,
        schema: Dict[str, Any] = None,
        extraction_prompt: str = "Extract structured data from the content.",
        llm_config: Optional[LLMConfig] = None,
        content_type: str = "auto",
        extract_html: bool = True,
        extract_text: bool = True
    ):
        """Initialize the LLM extractor.
        
        Args:
            schema: Dictionary defining the expected extraction schema
            extraction_prompt: Prompt to guide the LLM extraction process
            llm_config: Configuration for the LLM provider
            content_type: Type of content to extract from ('html', 'text', or 'auto')
            extract_html: Whether to extract from HTML content
            extract_text: Whether to extract from text content
        """
        self.schema = schema or {}
        self.extraction_prompt = extraction_prompt
        self.llm_config = llm_config or LLMConfig()
        self.content_type = content_type
        self.extract_html = extract_html
        self.extract_text = extract_text
    
    async def extract_async(self, content: Union[str, Page]) -> Dict[str, Any]:
        """Extract data from content using an LLM asynchronously.
        
        Args:
            content: Content to extract data from, either a string or a Page object
            
        Returns:
            A dictionary containing the extracted data
        """
        # Get content string from content object
        content_str = self._get_content_string(content)
        if not content_str:
            return {}
        
        # Generate the extraction prompt
        prompt = self._generate_extraction_prompt(content_str)
        
        try:
            # Call LLM with the prompt
            llm_response = await self.llm_config.call_llm_async(prompt)
            
            # Parse the LLM response
            extracted_data = self._parse_llm_response(llm_response)
            
            return extracted_data
        except Exception as e:
            # Log the error and return empty dict
            print(f"Error during LLM extraction: {e}")
            return {}
    
    def extract(self, content: Union[str, Page]) -> Dict[str, Any]:
        """Extract data from content using an LLM.
        
        Args:
            content: Content to extract data from, either a string or a Page object
            
        Returns:
            A dictionary containing the extracted data
        """
        # Run the async extraction in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If there is no event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.extract_async(content))
    
    async def extract_all_async(self, contents: List[Union[str, Page]]) -> List[Dict[str, Any]]:
        """Extract data from multiple contents asynchronously.
        
        Args:
            contents: List of content strings or Page objects
            
        Returns:
            A list of dictionaries containing the extracted data
        """
        tasks = [self.extract_async(content) for content in contents]
        return await asyncio.gather(*tasks)
    
    def extract_all(self, contents: List[Union[str, Page]]) -> List[Dict[str, Any]]:
        """Extract data from multiple contents.
        
        Args:
            contents: List of content strings or Page objects
            
        Returns:
            A list of dictionaries containing the extracted data
        """
        # Run the async extraction in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If there is no event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.extract_all_async(contents))
    
    def _get_content_string(self, content: Union[str, Page]) -> str:
        """Extract content string from input.
        
        Args:
            content: Content to extract from, either a string or a Page object
            
        Returns:
            A string representation of the content
        """
        # If content is already a string, return it
        if isinstance(content, str):
            return content
        
        # If it's a Page object, extract content based on settings
        html_content = None
        text_content = None
        
        if hasattr(content, 'html') and self.extract_html:
            html_content = getattr(content, 'html')
        
        if hasattr(content, 'text') and self.extract_text:
            text_content = getattr(content, 'text')
        elif hasattr(content, 'content') and self.extract_text:
            text_content = getattr(content, 'content')
        
        # Determine which content to use based on content_type
        if self.content_type == 'html' and html_content:
            return html_content
        elif self.content_type == 'text' and text_content:
            return text_content
        elif self.content_type == 'auto':
            # Prefer HTML if available and extraction is enabled
            if html_content and self.extract_html:
                return html_content
            # Otherwise use text content
            elif text_content and self.extract_text:
                return text_content
        
        # If no content could be extracted, return empty string
        return ""
    
    def _generate_extraction_prompt(self, content: str) -> str:
        """Generate a prompt for the LLM extraction.
        
        Args:
            content: Content to extract data from
            
        Returns:
            A formatted prompt for the LLM
        """
        schema_str = json.dumps(self.schema, indent=2)
        
        prompt = f"""
{self.extraction_prompt}

Extract the following structured data from the content:
{schema_str}

The data should be returned as a valid JSON object matching the schema.
If a field cannot be extracted, use null or an appropriate default value.

CONTENT:
{content}

EXTRACTED DATA (JSON):
"""
        return prompt.strip()
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data.
        
        Args:
            response: Response from the LLM
            
        Returns:
            A dictionary containing the extracted data
        """
        # Try to find and parse JSON in the response
        try:
            # Look for JSON blocks in markdown format
            if "```json" in response and "```" in response.split("```json", 1)[1]:
                json_str = response.split("```json", 1)[1].split("```", 1)[0].strip()
                return json.loads(json_str)
            
            # Look for JSON blocks without language specification
            elif "```" in response and "```" in response.split("```", 1)[1]:
                json_str = response.split("```", 1)[1].split("```", 1)[0].strip()
                return json.loads(json_str)
            
            # Try to parse the entire response as JSON
            else:
                return json.loads(response.strip())
                
        except (json.JSONDecodeError, IndexError):
            # If JSON parsing fails, try to find a dictionary-like structure
            if "{" in response and "}" in response:
                # Extract text between first { and last }
                dict_str = response[response.find("{"):response.rfind("}")+1]
                try:
                    return json.loads(dict_str)
                except json.JSONDecodeError:
                    return {}
            
            # If no valid JSON or dictionary format found, return empty dict
            return {}
    
    def update_schema(self, schema: Dict[str, Any]) -> None:
        """Update the extraction schema.
        
        Args:
            schema: New schema dictionary
        """
        self.schema = schema
    
    def update_prompt(self, prompt: str) -> None:
        """Update the extraction prompt.
        
        Args:
            prompt: New extraction prompt
        """
        self.extraction_prompt = prompt
    
    def update_llm_config(self, llm_config: LLMConfig) -> None:
        """Update the LLM configuration.
        
        Args:
            llm_config: New LLM configuration
        """
        self.llm_config = llm_config
    
    def to_json(self) -> str:
        """Convert the extractor configuration to JSON.
        
        Returns:
            JSON string representation of the extractor configuration
        """
        config = {
            "schema": self.schema,
            "extraction_prompt": self.extraction_prompt,
            "content_type": self.content_type,
            "extract_html": self.extract_html,
            "extract_text": self.extract_text,
            "llm_config": self.llm_config.to_dict() if hasattr(self.llm_config, "to_dict") else None
        }
        
        return json.dumps(config, indent=2)
    
    @classmethod
    def from_json(cls, json_config: str) -> 'LLMExtractor':
        """Create an extractor from a JSON configuration.
        
        Args:
            json_config: JSON string with extractor configuration
            
        Returns:
            A new LLMExtractor instance
        """
        config = json.loads(json_config)
        
        # Create LLMConfig from config dict if available
        llm_config = None
        if config.get("llm_config"):
            llm_config = LLMConfig.from_dict(config["llm_config"])
        
        return cls(
            schema=config.get("schema", {}),
            extraction_prompt=config.get("extraction_prompt", "Extract structured data from the content."),
            llm_config=llm_config,
            content_type=config.get("content_type", "auto"),
            extract_html=config.get("extract_html", True),
            extract_text=config.get("extract_text", True)
        ) 