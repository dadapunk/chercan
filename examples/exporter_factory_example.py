#!/usr/bin/env python
"""
Example demonstrating the use of ExporterFactory in Crawl4AI

This example shows how to:
1. Create exporters for different formats
2. Export content using file extensions
3. Export to multiple formats at once
4. Register custom exporters
5. Use with crawled content
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, Any

from crawl4ai import (
    HTTPCrawler, 
    CSSExtractor,
    ExporterFactory, 
    ExportFormat, 
    Page,
    BaseExporter
)
from crawl4ai.exports import CustomExporter  # For demonstration of custom exporters

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample content for testing exporters
sample_content = {
    "title": "Example Product",
    "price": "$19.99",
    "description": "This is a sample product description",
    "features": ["Feature 1", "Feature 2", "Feature 3"],
    "in_stock": True,
    "ratings": {
        "average": 4.5,
        "count": 120
    }
}

# Sample pages for testing exporters
sample_page = Page(
    url="https://example.com/product/123",
    status=200,
    content_type="text/html",
    html="<html><body><h1>Example Product</h1></body></html>",
    text="Example Product",
    extracted_data=sample_content
)


async def create_exporters_example():
    """Example showing how to create exporters for different formats."""
    logger.info("Creating exporters for different formats:")
    
    # Create the factory
    factory = ExporterFactory()
    
    # Create exporters for different formats
    json_exporter = factory.create_exporter(ExportFormat.JSON, indent=2)
    csv_exporter = factory.create_exporter(ExportFormat.CSV)
    html_exporter = factory.create_exporter(ExportFormat.HTML, include_metadata=True)
    md_exporter = factory.create_exporter(ExportFormat.MARKDOWN)
    
    logger.info(f"Created JSON exporter: {type(json_exporter).__name__}")
    logger.info(f"Created CSV exporter: {type(csv_exporter).__name__}")
    logger.info(f"Created HTML exporter: {type(html_exporter).__name__}")
    logger.info(f"Created Markdown exporter: {type(md_exporter).__name__}")
    
    # Export sample content with the JSON exporter
    json_content = json_exporter.export_content(sample_content)
    logger.info(f"JSON export sample:\n{json_content[:150]}...")
    
    return factory


async def export_by_extension_example(factory: ExporterFactory):
    """Example showing how to export content using file extensions."""
    logger.info("\nExporting content based on file extensions:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Export to different file formats
        file_paths = {
            "json": os.path.join(temp_dir, "product.json"),
            "csv": os.path.join(temp_dir, "product.csv"),
            "html": os.path.join(temp_dir, "product.html"),
            "md": os.path.join(temp_dir, "product.md")
        }
        
        # Export content by file extension
        for ext, path in file_paths.items():
            factory.export_to_file(sample_content, path)
            with open(path, 'r') as f:
                content = f.read()
                logger.info(f"{ext.upper()} export preview ({path}):\n{content[:100]}...")


class XMLExporter(BaseExporter):
    """Example custom exporter for XML format."""
    
    def export_content(self, content: Dict[str, Any]) -> str:
        """Export content to XML format."""
        xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<root>']
        
        def process_item(item, parent_tag=None):
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, (dict, list)):
                        xml.append(f"<{k}>")
                        process_item(v, k)
                        xml.append(f"</{k}>")
                    else:
                        xml.append(f"<{k}>{v}</{k}>")
            elif isinstance(item, list):
                for v in item:
                    if isinstance(v, (dict, list)):
                        xml.append(f"<item>")
                        process_item(v, "item")
                        xml.append(f"</item>")
                    else:
                        xml.append(f"<item>{v}</item>")
            else:
                xml.append(str(item))
        
        process_item(content)
        xml.append('</root>')
        return "\n".join(xml)


async def register_custom_exporter_example(factory: ExporterFactory):
    """Example showing how to register and use a custom exporter."""
    logger.info("\nRegistering and using a custom exporter:")
    
    # Register a custom XML exporter
    factory.register_exporter("xml", XMLExporter)
    
    # Create an instance of the custom exporter
    xml_exporter = factory.create_exporter_from_extension("xml")
    logger.info(f"Created custom XML exporter: {type(xml_exporter).__name__}")
    
    # Export sample content with the custom XML exporter
    xml_content = xml_exporter.export_content(sample_content)
    logger.info(f"XML export sample:\n{xml_content[:200]}...")
    
    # Export to a file with .xml extension
    with tempfile.TemporaryDirectory() as temp_dir:
        xml_path = os.path.join(temp_dir, "product.xml")
        factory.export_to_file(sample_content, xml_path)
        with open(xml_path, 'r') as f:
            content = f.read()
            logger.info(f"XML file export ({xml_path}):\n{content[:150]}...")


async def multiple_formats_example(factory: ExporterFactory):
    """Example showing how to export content to multiple formats at once."""
    logger.info("\nExporting content to multiple formats:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = os.path.join(temp_dir, "product")
        
        # Export to multiple formats at once
        formats = [ExportFormat.JSON, ExportFormat.CSV, ExportFormat.HTML, ExportFormat.MARKDOWN, "xml"]
        for fmt in formats:
            if isinstance(fmt, ExportFormat):
                file_path = f"{base_path}.{fmt.value.lower()}"
            else:
                file_path = f"{base_path}.{fmt}"
                
            factory.export_to_file(sample_content, file_path)
            logger.info(f"Exported to {file_path}")
        
        # List all created files
        files = os.listdir(temp_dir)
        logger.info(f"Created {len(files)} export files: {', '.join(files)}")


async def crawling_example():
    """Example showing how to use ExporterFactory with crawled content."""
    logger.info("\nUsing ExporterFactory with a crawler:")
    
    # Create a crawler and extractor
    crawler = HTTPCrawler()
    extractor = CSSExtractor({
        "quotes": ".quote .text::text",
        "authors": ".quote .author::text"
    })
    
    # Create an exporter factory
    factory = ExporterFactory()
    
    # Crawl a page
    url = "http://quotes.toscrape.com/"
    page = await crawler.fetch(url)
    
    # Extract data
    data = await extractor.extract(page)
    page.extracted_data = data
    
    logger.info(f"Crawled and extracted data from {url}")
    logger.info(f"Found {len(data.get('quotes', []))} quotes")
    
    # Export to different formats
    with tempfile.TemporaryDirectory() as temp_dir:
        for fmt in [ExportFormat.JSON, ExportFormat.CSV, ExportFormat.HTML]:
            file_path = os.path.join(temp_dir, f"quotes.{fmt.value.lower()}")
            factory.export_to_file(data, file_path)
            logger.info(f"Exported quotes to {file_path}")


async def main():
    """Run all examples."""
    logger.info("=== ExporterFactory Examples ===")
    
    # Example 1: Create exporters for different formats
    factory = await create_exporters_example()
    
    # Example 2: Export content using file extensions
    await export_by_extension_example(factory)
    
    # Example 3: Register and use a custom exporter
    await register_custom_exporter_example(factory)
    
    # Example 4: Export to multiple formats
    await multiple_formats_example(factory)
    
    # Example 5: Use with a crawler
    await crawling_example()
    
    logger.info("=== ExporterFactory Examples Completed ===")


if __name__ == "__main__":
    asyncio.run(main()) 