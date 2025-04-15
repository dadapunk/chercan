#!/usr/bin/env python
"""Example script demonstrating session management with CrawlerSession."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.core import CrawlerSession


async def main():
    """Run examples to demonstrate session management."""
    print("Testing CrawlerSession implementation...\n")
    
    # Create custom headers for the session
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    # Create session with custom headers
    async with CrawlerSession(headers=headers, persist_cookies=True) as session:
        # Example 1: Basic GET request
        print("[1] Making a GET request to httpbin.org/headers...")
        response = await session.get("https://httpbin.org/headers")
        data = await response.json()
        print(f"  Status: {response.status}")
        print(f"  Server sees our headers:")
        for key, value in data["headers"].items():
            print(f"    {key}: {value}")
        
        # Example 2: Working with cookies
        print("\n[2] Setting cookies and verifying with httpbin.org/cookies...")
        session.add_cookie("test_cookie", "cookie_value")
        session.add_cookie("another_cookie", "another_value")
        
        response = await session.get("https://httpbin.org/cookies")
        data = await response.json()
        print(f"  Cookies in response: {data['cookies']}")
        
        # Example 3: POST request with form data
        print("\n[3] Sending POST request with form data...")
        form_data = {
            "field1": "value1",
            "field2": "value2",
        }
        response = await session.post("https://httpbin.org/post", data=form_data)
        data = await response.json()
        print(f"  Status: {response.status}")
        print(f"  Form data received by server: {data['form']}")
        
        # Print session statistics
        print("\nSession Statistics:")
        print(f"  Requests made: {session.request_count}")
        print(f"  Current cookies: {session.get_cookies()}")


if __name__ == "__main__":
    asyncio.run(main()) 