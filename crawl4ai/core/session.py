"""Session management for crawlers.

This module provides session management capabilities for crawlers,
including cookie handling, authentication, and connection pooling.
"""
from typing import Dict, Optional, Any, List, Union
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
import json
from pathlib import Path

from crawl4ai.config import get_logger
from crawl4ai.core.exceptions import RequestError, AuthenticationError


class CrawlerSession:
    """Session management for crawlers.
    
    This class handles cookies, authentication, and connection pooling
    for both AsyncWebCrawler and HTTP-only crawlers.
    """
    
    def __init__(
        self,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        persist_cookies: bool = True,
        cookie_file: Optional[Union[str, Path]] = None,
    ):
        """Initialize a crawler session.
        
        Args:
            cookies: Initial cookies to include in requests
            headers: Default headers to include in requests
            auth: Authentication credentials (username/password or token)
            timeout: Request timeout in seconds
            persist_cookies: Whether to persist cookies between sessions
            cookie_file: File to store cookies (if persist_cookies is True)
        """
        self.cookies = cookies or {}
        self.headers = headers or {}
        self.auth = auth or {}
        self.timeout = timeout or 30
        self.persist_cookies = persist_cookies
        
        # Set up cookie file
        if persist_cookies:
            self.cookie_file = Path(cookie_file) if cookie_file else Path("cookies.json")
            self._load_cookies()
        else:
            self.cookie_file = None
        
        # Set up HTTP session (will be initialized in async context)
        self._http_session = None
        self.logger = get_logger("core.session")
        
        # Session state
        self.is_authenticated = False
        self.last_request_time = None
        self.request_count = 0
    
    async def __aenter__(self):
        """Async context manager entry.
        
        Returns:
            Self instance with initialized session
        """
        # Create HTTP session
        self._http_session = aiohttp.ClientSession(
            cookies=self.cookies,
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
        )
        self.logger.info("Session initialized")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        # Save cookies if needed
        if self.persist_cookies:
            self._save_cookies()
        
        # Close HTTP session
        if self._http_session:
            await self._http_session.close()
            self._http_session = None
        
        self.logger.info(f"Session closed (made {self.request_count} requests)")
    
    def _load_cookies(self) -> None:
        """Load cookies from file if it exists."""
        if not self.cookie_file or not self.cookie_file.exists():
            return
        
        try:
            with open(self.cookie_file, "r") as f:
                stored_cookies = json.load(f)
                
                # Check if cookies are expired
                for name, cookie in list(stored_cookies.items()):
                    if "expires" in cookie:
                        expires = datetime.fromisoformat(cookie["expires"])
                        if expires < datetime.now():
                            del stored_cookies[name]
                            continue
                
                # Update cookies dictionary
                if stored_cookies:
                    self.cookies.update({k: v["value"] for k, v in stored_cookies.items()})
                    self.logger.info(f"Loaded {len(stored_cookies)} cookies from {self.cookie_file}")
        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning(f"Failed to load cookies from {self.cookie_file}: {str(e)}")
    
    def _save_cookies(self) -> None:
        """Save cookies to file."""
        if not self.cookie_file or not self._http_session:
            return
        
        try:
            # Create cookie file directory if it doesn't exist
            self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Format cookies with expiration
            cookie_dict = {}
            for name, morsel in self._http_session.cookie_jar.items():
                cookie_dict[name] = {
                    "value": morsel.value,
                    "domain": morsel.get("domain", ""),
                    "path": morsel.get("path", "/"),
                }
                if morsel.get("expires"):
                    expires = (datetime.now() + timedelta(seconds=morsel["expires"]))
                    cookie_dict[name]["expires"] = expires.isoformat()
            
            # Save to file
            with open(self.cookie_file, "w") as f:
                json.dump(cookie_dict, f, indent=2)
                
            self.logger.info(f"Saved {len(cookie_dict)} cookies to {self.cookie_file}")
        except IOError as e:
            self.logger.warning(f"Failed to save cookies to {self.cookie_file}: {str(e)}")
    
    async def authenticate(
        self,
        url: str,
        auth_type: str = "form",
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> bool:
        """Authenticate with a website.
        
        Args:
            url: Authentication URL
            auth_type: Type of authentication ('form', 'basic', 'token')
            data: Authentication data (username/password or token)
            **kwargs: Additional arguments to pass to request method
            
        Returns:
            True if authentication was successful, False otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if not self._http_session:
            raise AuthenticationError("Session not initialized, use async with context")
        
        # Use provided auth data or fall back to instance auth
        auth_data = data or self.auth
        if not auth_data:
            raise AuthenticationError("No authentication credentials provided")
        
        try:
            self.logger.info(f"Authenticating with {url} using {auth_type} auth")
            
            if auth_type == "form":
                # Form-based authentication (POST request with credentials)
                async with self._http_session.post(url, data=auth_data, **kwargs) as response:
                    if response.status >= 400:
                        raise AuthenticationError(f"Authentication failed: HTTP {response.status}")
                    
                    # Check response for authentication success (could be customized)
                    self.is_authenticated = True
                    self.request_count += 1
                    self.last_request_time = time.time()
                    return True
                    
            elif auth_type == "basic":
                # Basic authentication (Authorization header)
                username = auth_data.get("username", "")
                password = auth_data.get("password", "")
                auth = aiohttp.BasicAuth(username, password)
                
                async with self._http_session.get(url, auth=auth, **kwargs) as response:
                    if response.status >= 400:
                        raise AuthenticationError(f"Authentication failed: HTTP {response.status}")
                    
                    self.is_authenticated = True
                    self.request_count += 1
                    self.last_request_time = time.time()
                    return True
                    
            elif auth_type == "token":
                # Token-based authentication (Authorization header)
                token = auth_data.get("token", "")
                token_type = auth_data.get("token_type", "Bearer")
                
                headers = {"Authorization": f"{token_type} {token}"}
                self._http_session.headers.update(headers)
                
                async with self._http_session.get(url, **kwargs) as response:
                    if response.status >= 400:
                        raise AuthenticationError(f"Authentication failed: HTTP {response.status}")
                    
                    self.is_authenticated = True
                    self.request_count += 1
                    self.last_request_time = time.time()
                    return True
            else:
                raise AuthenticationError(f"Unsupported authentication type: {auth_type}")
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Send a GET request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to session.get()
            
        Returns:
            aiohttp.ClientResponse object
            
        Raises:
            RequestError: If the request fails
        """
        if not self._http_session:
            raise RequestError("Session not initialized, use async with context")
        
        try:
            response = await self._http_session.get(url, **kwargs)
            self.request_count += 1
            self.last_request_time = time.time()
            return response
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.logger.error(f"GET request error: {str(e)}")
            raise RequestError(f"GET request failed: {str(e)}", url=url)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Send a POST request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to session.post()
            
        Returns:
            aiohttp.ClientResponse object
            
        Raises:
            RequestError: If the request fails
        """
        if not self._http_session:
            raise RequestError("Session not initialized, use async with context")
        
        try:
            response = await self._http_session.post(url, **kwargs)
            self.request_count += 1
            self.last_request_time = time.time()
            return response
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.logger.error(f"POST request error: {str(e)}")
            raise RequestError(f"POST request failed: {str(e)}", url=url)
    
    def add_cookie(self, name: str, value: str, **kwargs) -> None:
        """Add a cookie to the session.
        
        Args:
            name: Cookie name
            value: Cookie value
            **kwargs: Additional cookie attributes (domain, path, etc.)
        """
        self.cookies[name] = value
        
        if self._http_session:
            self._http_session.cookie_jar.update_cookies({name: value})
    
    def clear_cookies(self) -> None:
        """Clear all cookies from the session."""
        self.cookies.clear()
        
        if self._http_session:
            self._http_session.cookie_jar.clear()
    
    def update_headers(self, headers: Dict[str, str]) -> None:
        """Update session headers.
        
        Args:
            headers: Headers to update
        """
        self.headers.update(headers)
        
        if self._http_session:
            self._http_session.headers.update(headers)
    
    def get_cookies(self) -> Dict[str, str]:
        """Get current session cookies.
        
        Returns:
            Dictionary of cookies
        """
        if self._http_session:
            return {k: v.value for k, v in self._http_session.cookie_jar.items()}
        return self.cookies.copy() 