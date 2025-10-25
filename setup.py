"""
FreeP2W - Free PDF to Word Converter
Setup script for PyPI distribution
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="freep2w",
    version="1.0.0",
    author="zstar",
    author_email="zstar1003@163.com",
    description="Free PDF to Word Converter with formula recognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zstar1003/FreeP2W",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "freep2w=freep2w.cli:main",
        ],
    },
    package_data={
        "freep2w": [
            "weights/*.pt",
            "*.yaml",
        ],
    },
    include_package_data=True,
    keywords="pdf docx converter formula recognition yolo",
    project_urls={
        "Bug Reports": "https://github.com/zstar1003/FreeP2W/issues",
        "Source": "https://github.com/zstar1003/FreeP2W",
    },
)
