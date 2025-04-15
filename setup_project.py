#!/usr/bin/env python
import os
import sys
import shutil
import subprocess
import venv
from pathlib import Path
import platform

def create_directory_structure():
    """Create the directory structure for the Crawl4AI project."""
    base_dir = Path("crawl4ai")
    tests_dir = Path("tests")
    examples_dir = Path("examples")
    
    # Main directories
    directories = [
        base_dir,
        base_dir / "core",
        base_dir / "config",
        base_dir / "crawlers",
        base_dir / "strategies",
        base_dir / "processing",
        base_dir / "processing" / "extractors",
        base_dir / "processing" / "filters",
        base_dir / "exports",
        base_dir / "api",
        base_dir / "cli",
        base_dir / "utils",
        base_dir / "docker",
        tests_dir,
        tests_dir / "unit",
        tests_dir / "integration",
        examples_dir,
        examples_dir / "ecommerce",
        examples_dir / "news",
        examples_dir / "social_media",
        examples_dir / "api_extraction",
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        init_file = directory / "__init__.py"
        if not init_file.exists():
            with open(init_file, "w") as f:
                f.write("# Crawl4AI module\n")
    
    print("✅ Project directory structure created successfully.")

def create_virtual_environment():
    """Create a virtual environment for the project."""
    venv_dir = Path("venv")
    
    if venv_dir.exists():
        print("⚠️ Virtual environment already exists.")
        return
    
    print("📦 Creating virtual environment...")
    venv.create(venv_dir, with_pip=True)
    
    # Determine the activation script based on platform
    if platform.system() == "Windows":
        activate_script = venv_dir / "Scripts" / "activate.bat"
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        activate_script = venv_dir / "bin" / "activate"
        pip_path = venv_dir / "bin" / "pip"

    print(f"✅ Virtual environment created at {venv_dir}.")
    print(f"   To activate, run: {activate_script}")
    
    return pip_path

def install_dependencies(pip_path):
    """Install project dependencies."""
    if pip_path is None or not Path(pip_path).exists():
        print("⚠️ Pip not found. Please activate the virtual environment and install dependencies manually.")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("📦 Installing dependencies...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed successfully.")
    return True

def create_sample_files():
    """Create sample configuration and verification files."""
    # Create main __init__.py
    with open(Path("crawl4ai") / "__init__.py", "w") as f:
        f.write('"""Crawl4AI Framework - A modular web crawling and data extraction framework.\n\n')
        f.write('This package provides a flexible, modular framework for web crawling and data extraction.\n')
        f.write('It is built on top of Crawl4AI v0.5.0 and provides a simple interface for common crawling tasks.\n')
        f.write('"""\n\n')
        f.write('__version__ = "0.1.0"\n')
    
    # Create sample config module
    config_dir = Path("crawl4ai") / "config"
    with open(config_dir / "settings.py", "w") as f:
        f.write('"""Global configuration settings for the Crawl4AI framework."""\n\n')
        f.write('from pathlib import Path\n')
        f.write('import os\n\n')
        f.write('# Base directories\n')
        f.write('BASE_DIR = Path(__file__).resolve().parent.parent.parent\n')
        f.write('PACKAGE_DIR = BASE_DIR / "crawl4ai"\n\n')
        f.write('# Default crawler settings\n')
        f.write('DEFAULT_USER_AGENT = "Crawl4AI/0.5.0 (+https://docs.crawl4ai.com/bot)"\n')
        f.write('DEFAULT_TIMEOUT = 30  # seconds\n')
        f.write('DEFAULT_RETRY_COUNT = 3\n')
        f.write('DEFAULT_CRAWL_DELAY = 1.0  # seconds\n\n')
        f.write('# Export settings\n')
        f.write('EXPORT_DIR = BASE_DIR / "exports"\n')
        f.write('DEFAULT_EXPORT_FORMAT = "markdown"\n\n')
        f.write('# Rate limiting\n')
        f.write('DEFAULT_RATE_LIMIT = 60  # requests per minute\n\n')
        f.write('# Logging\n')
        f.write('LOG_DIR = BASE_DIR / "logs"\n')
        f.write('LOG_LEVEL = "INFO"\n')
    
    # Create verification script
    with open("verify_installation.py", "w") as f:
        f.write('#!/usr/bin/env python\n')
        f.write('"""Verification script to test Crawl4AI installation."""\n\n')
        f.write('import asyncio\n')
        f.write('from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig\n\n')
        f.write('async def main():\n')
        f.write('    """Run a simple crawl to verify installation."""\n')
        f.write('    print("Testing Crawl4AI installation...")\n')
        f.write('    async with AsyncWebCrawler() as crawler:\n')
        f.write('        result = await crawler.arun(\n')
        f.write('            url="https://www.example.com",\n')
        f.write('        )\n')
        f.write('        print("Crawl completed successfully!")\n')
        f.write('        print("\\nContent preview (first 300 chars):")\n')
        f.write('        print("-" * 50)\n')
        f.write('        print(result.markdown[:300])\n')
        f.write('        print("-" * 50)\n')
        f.write('        print("\\nCrawl statistics:")\n')
        f.write('        print(f"  Pages crawled: {result.stats.pages_crawled}")\n')
        f.write('        print(f"  Total time: {result.stats.total_time:.2f} seconds")\n\n')
        f.write('if __name__ == "__main__":\n')
        f.write('    asyncio.run(main())\n')
    
    print("✅ Sample configuration and verification files created.")

def main():
    """Main function to set up the project."""
    print("🚀 Setting up Crawl4AI project...")
    
    # Create directory structure
    create_directory_structure()
    
    # Create virtual environment
    pip_path = create_virtual_environment()
    
    # Create sample files
    create_sample_files()
    
    # Print next steps
    print("\n📋 Next Steps:")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("3. Run post-installation setup:")
    print("   crawl4ai-setup")
    print("   crawl4ai-doctor")
    print("4. Verify the installation:")
    print("   python verify_installation.py")

if __name__ == "__main__":
    main() 