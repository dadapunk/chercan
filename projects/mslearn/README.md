# Microsoft Learn Content Extractor

A toolkit for extracting and processing Microsoft Learn content using crawl4ai and LLM-based extraction.

## Project Structure

- **courses/**: Course content extractors
  - **sc300/**: SC-300 (Identity and Access Administrator) course extractor
  - _(more courses can be added here)_
- **models.py**: Data models for course content
- ****init**.py**: Package initialization

## Features

- Extract course content from Microsoft Learn
- Support for both LLM-based and direct HTML extraction
- Structured data output in JSON format
- Custom extraction strategies for different course types
- Fallback mechanisms for handling extraction failures

## Usage

See the README in each subdirectory for specific usage instructions:

- [Microsoft Learn Courses](courses/README.md)

## Architecture

The project uses a modular architecture:

1. **Data Models**: Defined using Pydantic for validation and serialization
2. **Extraction Strategies**: Different approaches for content extraction:
   - LLM-based extraction (using OpenAI)
   - Direct HTML extraction
   - Regular expression-based fallback extraction
3. **Web Crawling**: Using crawl4ai for browser automation and page loading
4. **Output Format**: Structured JSON that can be easily processed or displayed

## Requirements

- Python 3.8+
- crawl4ai library
- OpenAI API key (for LLM-based extraction)
- Pydantic for data validation

## License

This project is for educational purposes only.
