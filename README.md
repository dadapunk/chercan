# Chercan - Crawl4AI Framework

A modular and flexible web scraping and crawling framework based on Crawl4AI v0.5.0, designed to be adaptable for various data collection needs.

## Overview

This project provides a base framework for automated data collection through web scraping and crawling. It's designed to be:

- **Modular**: Easily customize components for specific needs
- **Flexible**: Adapt to different websites and data structures
- **Scalable**: From single-page scraping to large-scale crawling
- **Powerful**: Leveraging Crawl4AI's advanced capabilities

## Key Features

- High-performance asynchronous web crawling
- Multiple crawling strategies (BFS, DFS, Best-First)
- Browser-based (Playwright) and HTTP-only crawlers
- Structured data extraction (CSS, XPath, LLM-based)
- Export to various formats (Markdown, JSON, CSV)
- Docker deployment support
- CLI and API interfaces

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/chercan.git
cd chercan

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run post-installation setup
crawl4ai-setup
crawl4ai-doctor
```

## Quick Start

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.example.com",
        )
        print(result.markdown[:300])  # Show the first 300 characters

if __name__ == "__main__":
    asyncio.run(main())
```

## Project Structure

```
/crawl4ai
  /core          - Base classes and utilities
  /config        - Configuration handling
  /crawlers      - Different crawler implementations
  /strategies    - Crawling strategies
  /processing    - Data extraction and filtering
  /exports       - Export formats
  /api           - API endpoints
  /cli           - Command-line interface
  /utils         - Shared utilities
  /docker        - Docker configurations
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

This project leverages [Crawl4AI](https://docs.crawl4ai.com/) v0.5.0 for web crawling and data extraction.
