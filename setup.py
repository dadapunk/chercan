from setuptools import setup, find_packages

setup(
    name="chercan",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "crawl4ai[all]>=0.5.0",
        "pydantic>=2.0.0",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.8",
) 