#!/usr/bin/env python
"""
SC-300 Course Extraction Script

Command-line utility to extract SC-300 course content.
"""
import os
import sys
import json
import asyncio
import argparse

# Add the project root to path to handle imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from projects.mslearn.courses.sc300.main import extract_sc300_course

async def main():
    """Main entry point function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract SC-300 course content from Microsoft Learn')
    parser.add_argument('--direct', action='store_true', help='Use direct HTML extraction instead of LLM')
    parser.add_argument('--output', default='sc300_course_data.json', help='Output file path')
    args = parser.parse_args()
    
    # Get the API token from environment variable
    api_token = os.getenv("OPENAI_API_KEY")
    if not api_token and not args.direct:
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("You can either set the API key or use --direct for HTML-based extraction")
        sys.exit(1)
    
    print("Starting SC-300 course extraction...")
    course_data = await extract_sc300_course(
        provider="openai", 
        api_token=api_token,
        use_direct_extraction=args.direct
    )
    
    # Pretty print the course data
    try:
        # Try model_dump first (pydantic v2)
        course_dict = course_data.model_dump()
    except AttributeError:
        # Fall back to dict() for pydantic v1
        course_dict = course_data.dict()
    
    print(json.dumps(course_dict, indent=2))
    
    # Save to file
    output_file = args.output
    with open(output_file, "w") as f:
        json.dump(course_dict, f, indent=2)
    
    print(f"Extraction complete. Data saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 