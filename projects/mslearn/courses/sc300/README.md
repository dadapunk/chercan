# SC-300 Course Extractor

This tool extracts Microsoft Learn SC-300 course content using the crawl4ai library with LLM-based extraction.

## Overview

The SC-300 Course Extractor is designed to extract structured course information from the Microsoft Learn platform, specifically for the SC-300 (Microsoft Identity and Access Administrator) certification course. It extracts:

- Course title and description
- Course difficulty level
- Prerequisites (if any)
- Modules with their titles, descriptions, and durations
- Units within each module with their titles and durations

## Requirements

- Python 3.8+
- crawl4ai library
- OpenAI API key (set as environment variable OPENAI_API_KEY) when using LLM-based extraction

## Usage

To run the extraction:

```bash
# Make sure you're in the sc300 directory
cd projects/mslearn/courses/sc300

# Run with LLM-based extraction (requires OpenAI API key)
python extract.py

# Run with direct HTML extraction (no API key needed)
python extract.py --direct

# Specify a custom output file
python extract.py --output custom_filename.json
```

### Command-line Arguments

- `--direct`: Use direct HTML extraction instead of LLM-based extraction
- `--output FILE`: Specify the output file path (default: sc300_course_data.json)

The script will:

1. Connect to the Microsoft Learn SC-300 course page
2. Use a configured browser to load the page
3. Extract content using either direct HTML extraction or LLM-based extraction
4. Structure the data into a Course object
5. Save the extracted data to the specified output file

## Files

- `extract.py`: Command-line entry point for running the extraction
- `main.py`: Core extraction logic
- `urls.py`: Course URLs and constants
- `__init__.py`: Package initialization
- `sc300_course_data.json`: Output file with the extracted course data

## Extraction Methods

The tool supports two extraction methods:

1. **LLM-based Extraction** (default): Uses OpenAI's language models to intelligently parse the course content. Requires an API key.
2. **Direct HTML Extraction**: Uses regular expressions and HTML parsing to extract content. No API key required but may be less accurate.

## Fallback Mechanism

If extraction fails for any reason, the script provides mock data as a fallback to demonstrate the expected data structure. This can be identified by the `[MOCK]` prefix in the data fields.

## Technical Details

The extraction uses:

- Browser automation for page loading
- LLM-based content extraction using OpenAI
- Fallback direct HTML parsing with regex patterns
- Pydantic models for data validation and serialization

## Example Output

The extracted data is saved in JSON format:

```json
{
  "code": "SC-300",
  "title": "SC-300: Implement an identity management solution",
  "description": "Learn to create and manage your initial Microsoft Entra implementation...",
  "level": "Intermediate",
  "prerequisites": [],
  "modules": [
    {
      "title": "Implement initial configuration of Microsoft Entra ID",
      "description": "Learn to create an initial Microsoft Entra ID configuration...",
      "duration": "50 min",
      "units": [
        {
          "title": "Introduction",
          "duration": "1 min",
          "url": "https://learn.microsoft.com/..."
        }
        // More units...
      ]
    }
    // More modules...
  ]
}
```
