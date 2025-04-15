"""Base middleware for Crawl4AI.

This module provides the base middleware class that all middleware components
in the Crawl4AI framework should extend.
"""

from typing import Optional

from crawl4ai.models import Request, Response


class BaseMiddleware:
    """Base middleware class for Crawl4AI.
    
    Middleware components can hook into different stages of the request/response
    lifecycle to modify behavior or add functionality.
    
    To create a middleware, extend this class and override the methods for the
    stages you want to hook into:
    
    - before_request: Called before a request is sent
    - on_response: Called when a response is received
    - after_response: Called after a response has been processed
    - on_error: Called when an error occurs
    
    Example:
    ```python
    class MyMiddleware(BaseMiddleware):
        async def before_request(self, request: Request) -> Request:
            # Modify the request
            request.headers["User-Agent"] = "My Custom User Agent"
            return request
            
        async def on_response(self, response: Response) -> Response:
            # Log the response
            print(f"Received response: {response.status_code}")
            return response
    ```
    """
    
    async def before_request(self, request: Request) -> Request:
        """Called before a request is sent.
        
        Args:
            request: The request to be sent
            
        Returns:
            The modified request
        """
        return request
    
    async def on_response(self, response: Response) -> Response:
        """Called when a response is received.
        
        Args:
            response: The response received
            
        Returns:
            The modified response
        """
        return response
    
    async def after_response(self, response: Response) -> Response:
        """Called after a response has been processed.
        
        Args:
            response: The processed response
            
        Returns:
            The final response
        """
        return response
    
    async def on_error(self, error: Exception, request: Optional[Request] = None) -> None:
        """Called when an error occurs during request/response handling.
        
        Args:
            error: The exception that occurred
            request: The request that caused the error (if available)
        """
        pass 