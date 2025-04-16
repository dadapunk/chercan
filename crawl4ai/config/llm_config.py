"""LLM configuration for Crawl4AI.

This module provides configuration for Large Language Model providers
that can be used with extractors and content filters.
"""

import os
import json
from typing import Dict, Any, Optional, List, Union, Callable


class LLMConfig:
    """Configuration for Large Language Model providers.
    
    This class contains settings for interacting with various LLM providers
    like OpenAI, Google, Anthropic, or custom providers.
    
    Example:
    ```python
    # OpenAI configuration
    config = LLMConfig(
        provider="openai",
        model="gpt-4",
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=0.1
    )
    
    # Using the config
    response = await config.call_llm_async("Extract the title from this HTML.")
    ```
    """
    
    SUPPORTED_PROVIDERS = ["openai", "anthropic", "google", "azure", "custom"]
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 60.0,
        extra_params: Optional[Dict[str, Any]] = None,
        custom_llm_callable: Optional[Callable] = None
    ):
        """Initialize the LLM configuration.
        
        Args:
            provider: LLM provider name (openai, anthropic, google, azure, custom)
            model: Model name or version
            api_key: API key for the LLM provider
            api_base: Base URL for the API (for custom endpoints)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            timeout: API call timeout in seconds
            extra_params: Additional parameters for the specific provider
            custom_llm_callable: Custom function for calling an LLM provider
        """
        if provider.lower() not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: {self.SUPPORTED_PROVIDERS}")
        
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key or self._get_default_api_key(provider)
        self.api_base = api_base
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.extra_params = extra_params or {}
        self.custom_llm_callable = custom_llm_callable
        
        # Import required libraries based on provider
        self._import_provider_libs()
    
    def _get_default_api_key(self, provider: str) -> Optional[str]:
        """Get default API key from environment variables.
        
        Args:
            provider: LLM provider name
            
        Returns:
            API key from environment variables, or None if not found
        """
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "azure": "AZURE_OPENAI_API_KEY",
        }
        
        if provider.lower() in env_var_map:
            return os.environ.get(env_var_map[provider.lower()])
        
        return None
    
    def _import_provider_libs(self) -> None:
        """Import required libraries based on provider.
        
        This method imports the necessary libraries lazily to avoid unnecessary dependencies.
        """
        # We'll import libraries only when needed to avoid unnecessary dependencies
        pass
    
    async def call_llm_async(self, prompt: str) -> str:
        """Call the LLM asynchronously with the given prompt.
        
        Args:
            prompt: Text prompt to send to the LLM
            
        Returns:
            Text response from the LLM
        """
        if self.provider == "custom" and self.custom_llm_callable:
            # Call custom LLM function if provided
            if callable(self.custom_llm_callable):
                return await self.custom_llm_callable(prompt, self)
            else:
                raise ValueError("Custom LLM callable is not a valid callable function")
        
        # Call the appropriate provider
        if self.provider == "openai":
            return await self._call_openai_async(prompt)
        elif self.provider == "anthropic":
            return await self._call_anthropic_async(prompt)
        elif self.provider == "google":
            return await self._call_google_async(prompt)
        elif self.provider == "azure":
            return await self._call_azure_openai_async(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _call_openai_async(self, prompt: str) -> str:
        """Call OpenAI API asynchronously.
        
        Args:
            prompt: Text prompt to send to OpenAI
            
        Returns:
            Text response from OpenAI
        """
        try:
            # Import OpenAI library
            import openai
            from openai import AsyncOpenAI
            
            # Configure client
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base if self.api_base else openai.base_url,
                timeout=self.timeout
            )
            
            # Build request parameters
            params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
            }
            
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            
            # Add any extra parameters
            params.update(self.extra_params)
            
            # Call the API
            response = await client.chat.completions.create(**params)
            
            # Extract and return the content
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("OpenAI Python package is not installed. Install with 'pip install openai'.")
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    async def _call_anthropic_async(self, prompt: str) -> str:
        """Call Anthropic API asynchronously.
        
        Args:
            prompt: Text prompt to send to Anthropic
            
        Returns:
            Text response from Anthropic
        """
        try:
            # Import Anthropic library
            import anthropic
            
            # Configure client
            client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.api_base if self.api_base else None,
                timeout=self.timeout
            )
            
            # Build request parameters
            params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
            }
            
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            
            # Add any extra parameters
            params.update(self.extra_params)
            
            # Call the API
            response = await client.messages.create(**params)
            
            # Extract and return the content
            return response.content[0].text
        except ImportError:
            raise ImportError("Anthropic Python package is not installed. Install with 'pip install anthropic'.")
        except Exception as e:
            raise Exception(f"Error calling Anthropic API: {str(e)}")
    
    async def _call_google_async(self, prompt: str) -> str:
        """Call Google API asynchronously.
        
        Args:
            prompt: Text prompt to send to Google
            
        Returns:
            Text response from Google
        """
        try:
            # Import Google library
            import google.generativeai as genai
            
            # Configure API key
            genai.configure(api_key=self.api_key)
            
            # Build request parameters
            params = {
                "model": self.model,
                "temperature": self.temperature,
            }
            
            if self.max_tokens:
                params["max_output_tokens"] = self.max_tokens
            
            # Add any extra parameters
            params.update(self.extra_params)
            
            # Initialize the model
            model = genai.GenerativeModel(**params)
            
            # Call the API
            response = await model.generate_content_async(prompt)
            
            # Extract and return the content
            return response.text
        except ImportError:
            raise ImportError("Google GenerativeAI package is not installed. Install with 'pip install google-generativeai'.")
        except Exception as e:
            raise Exception(f"Error calling Google API: {str(e)}")
    
    async def _call_azure_openai_async(self, prompt: str) -> str:
        """Call Azure OpenAI API asynchronously.
        
        Args:
            prompt: Text prompt to send to Azure OpenAI
            
        Returns:
            Text response from Azure OpenAI
        """
        try:
            # Import OpenAI library
            from openai import AsyncAzureOpenAI
            
            # Configure client
            client = AsyncAzureOpenAI(
                api_key=self.api_key,
                api_version=self.extra_params.get("api_version", "2023-05-15"),
                azure_endpoint=self.api_base,
                timeout=self.timeout
            )
            
            # Build request parameters
            params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
            }
            
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            
            # Add any extra parameters (excluding api_version which is used for client init)
            extra_params = self.extra_params.copy()
            if "api_version" in extra_params:
                del extra_params["api_version"]
            params.update(extra_params)
            
            # Call the API
            response = await client.chat.completions.create(**params)
            
            # Extract and return the content
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("OpenAI Python package is not installed. Install with 'pip install openai'.")
        except Exception as e:
            raise Exception(f"Error calling Azure OpenAI API: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        config_dict = {
            "provider": self.provider,
            "model": self.model,
            "api_key": None,  # Don't include API key for security
            "api_base": self.api_base,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "extra_params": self.extra_params
        }
        
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'LLMConfig':
        """Create a configuration from a dictionary.
        
        Args:
            config_dict: Dictionary representation of the configuration
            
        Returns:
            A new LLMConfig instance
        """
        # We don't pass the API key from the dict for security,
        # it will be retrieved from environment variables
        return cls(
            provider=config_dict.get("provider", "openai"),
            model=config_dict.get("model", "gpt-3.5-turbo"),
            api_key=None,  # Use environment variables
            api_base=config_dict.get("api_base"),
            temperature=config_dict.get("temperature", 0.7),
            max_tokens=config_dict.get("max_tokens"),
            timeout=config_dict.get("timeout", 60.0),
            extra_params=config_dict.get("extra_params", {})
        )
    
    @classmethod
    def from_json(cls, json_string: str) -> 'LLMConfig':
        """Create a configuration from a JSON string.
        
        Args:
            json_string: JSON string representation of the configuration
            
        Returns:
            A new LLMConfig instance
        """
        config_dict = json.loads(json_string)
        return cls.from_dict(config_dict)
    
    def to_json(self) -> str:
        """Convert the configuration to a JSON string.
        
        Returns:
            JSON string representation of the configuration
        """
        return json.dumps(self.to_dict(), indent=2) 