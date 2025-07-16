#!/usr/bin/env python3
"""
Setup script for the Nijika AI Agent Framework
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
    name="nijika",
    version="0.1.0",
    author="Nijika Team",
    author_email="support@nijika.ai",
    description="A dynamic, industry-agnostic AI agent framework for seamless multi-provider integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nijika/nijika",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "isort>=5.10.0",
            "pre-commit>=2.17.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinxcontrib-asyncio>=0.3.0",
            "myst-parser>=0.17.0",
        ],
        "server": [
            "fastapi>=0.68.0",
            "uvicorn[standard]>=0.15.0",
            "gunicorn>=20.1.0",
        ],
        "monitoring": [
            "prometheus-client>=0.14.0",
            "grafana-client>=3.0.0",
            "datadog>=0.44.0",
        ],
        "cloud": [
            "boto3>=1.24.0",
            "google-cloud-storage>=2.5.0",
            "azure-storage-blob>=12.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nijika=nijika.cli:main",
            "nijika-server=nijika.server:main",
            "nijika-config=nijika.config:create_default_config_file",
        ],
    },
    include_package_data=True,
    package_data={
        "nijika": [
            "templates/*.yaml",
            "templates/*.json",
            "static/*",
            "ui/templates/*",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/nijika/nijika/issues",
        "Source": "https://github.com/nijika/nijika",
        "Documentation": "https://docs.nijika.ai",
        "Changelog": "https://github.com/nijika/nijika/blob/main/CHANGELOG.md",
    },
    keywords=[
        "ai",
        "agent",
        "framework",
        "automation",
        "workflow",
        "rag",
        "planning",
        "tools",
        "multi-provider",
        "llm",
        "openai",
        "anthropic",
        "google",
        "enterprise",
        "customer-service",
        "finance",
        "healthcare",
        "e-commerce",
        "education",
    ],
    zip_safe=False,
) 