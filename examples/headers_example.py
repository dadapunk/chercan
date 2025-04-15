#!/usr/bin/env python
"""Example script demonstrating headers and user agent handling."""

import json
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawl4ai.utils import (
    UserAgentManager,
    create_headers,
    COMMON_USER_AGENTS,
    DEFAULT_HEADERS,
)
from crawl4ai.core import CrawlerSession


def create_custom_user_agents_file():
    """Create a sample user agents file for the example."""
    custom_agents = {
        "mobile_android": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "mobile_iphone": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "bot": "MyCustomBot/1.0 (https://example.com/bot)",
    }
    
    with open("custom_user_agents.json", "w") as f:
        json.dump(custom_agents, f, indent=2)
    
    print("Created custom_user_agents.json with 3 user agents")


async def test_user_agent_manager():
    """Test the UserAgentManager functionality."""
    print("\n[1] Testing UserAgentManager...\n")
    
    # Create user agent manager with custom file
    ua_manager = UserAgentManager(
        rotation_strategy="sequential",
        custom_file="custom_user_agents.json",
    )
    
    # Print available user agents
    all_agents = ua_manager.get_all_user_agents()
    print(f"Loaded {len(all_agents)} user agents:")
    for name, agent in list(all_agents.items())[:5]:
        print(f"  {name}: {agent}")
    print("  ... (more user agents)")
    
    # Demonstrate specific agent selection
    print("\nGetting specific user agent:")
    chrome_ua = ua_manager.get_user_agent("chrome_windows")
    print(f"  chrome_windows: {chrome_ua}")
    
    # Demonstrate rotation
    print("\nUser agent rotation (sequential):")
    for i in range(5):
        ua = ua_manager.get_user_agent()
        print(f"  Rotation {i+1}: {ua[:50]}...")


async def test_header_creation():
    """Test the header creation functionality."""
    print("\n[2] Testing header creation...\n")
    
    # Basic headers
    basic_headers = create_headers(user_agent=COMMON_USER_AGENTS["crawl4ai"])
    print("Basic headers:")
    for name, value in basic_headers.items():
        print(f"  {name}: {value}")
    
    # Headers with cookies and referer
    print("\nHeaders with cookies and referer:")
    cookies = {"session_id": "abc123", "preference": "dark_mode"}
    advanced_headers = create_headers(
        user_agent=COMMON_USER_AGENTS["firefox_windows"],
        cookies=cookies,
        referer="https://example.com/previous-page",
        additional_headers={"X-Requested-With": "XMLHttpRequest"},
    )
    
    for name, value in advanced_headers.items():
        print(f"  {name}: {value}")


async def test_with_session():
    """Test headers with CrawlerSession."""
    print("\n[3] Testing headers with CrawlerSession...\n")
    
    # Create user agent manager
    ua_manager = UserAgentManager(rotation_strategy="random")
    
    # Create custom headers
    custom_headers = create_headers(
        user_agent=ua_manager.get_user_agent("chrome_windows"),
        additional_headers={"Accept": "application/json"},
    )
    
    # Create session with custom headers
    async with CrawlerSession(headers=custom_headers) as session:
        print("Making request to httpbin.org to show headers...")
        response = await session.get("https://httpbin.org/headers")
        data = await response.json()
        
        print("\nServer received these headers:")
        for key, value in data["headers"].items():
            print(f"  {key}: {value}")


async def main():
    """Run examples to demonstrate headers and user agent handling."""
    print("Demonstrating headers and user agent handling...")
    
    # Create custom user agents file
    create_custom_user_agents_file()
    
    # Test user agent manager
    await test_user_agent_manager()
    
    # Test header creation
    await test_header_creation()
    
    # Test with session
    await test_with_session()
    
    # Clean up
    Path("custom_user_agents.json").unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(main()) 