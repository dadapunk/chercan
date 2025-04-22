# Microsoft Learn Course Extractors

This directory contains scripts for extracting course content from the Microsoft Learn platform.

## Available Course Extractors

| Course Code | Course Title                              | Directory        |
| ----------- | ----------------------------------------- | ---------------- |
| SC-300      | Implement an identity management solution | [sc300/](sc300/) |

## How to Use

Each course extractor is contained in its own directory. To use a specific extractor:

1. Navigate to the course directory
2. Run the extraction script (usually `extract.py`)
3. Check the output JSON file for the extracted course data

For example, to extract SC-300 course content:

```bash
cd sc300
python extract.py
```

See the README file in each course directory for specific usage instructions.

## Common Requirements

Most course extractors require:

- Python 3.8+
- crawl4ai library
- OpenAI API key (for LLM-based extraction)

## Adding New Course Extractors

To add a new course extractor:

1. Create a new directory with the course code in lowercase (e.g., `sc900/`)
2. Copy the basic structure from an existing course extractor
3. Update the URLs and course-specific constants
4. Test the extraction with both LLM and direct extraction methods
5. Add documentation to the course directory's README file
6. Update this README with the new course information
