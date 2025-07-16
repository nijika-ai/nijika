# Installation Guide

This guide covers all installation methods and system requirements for the Nijika AI Agent Framework.

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB free space
- **Internet**: Required for AI provider API calls

### Recommended Requirements
- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Storage**: 2GB free space
- **Database**: SQLite (included) or PostgreSQL for production

## 🚀 Installation Methods

### Method 1: PyPI Installation (Recommended)

```bash
pip install nijika
```

For development dependencies:
```bash
pip install "nijika[dev]"
```

For all optional dependencies:
```bash
pip install "nijika[all]"
```

### Method 2: Source Installation

```bash
# Clone the repository
git clone https://github.com/your-org/nijika.git
cd nijika

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[all]"
```

### Method 3: Docker Installation

```bash
# Pull the official image
docker pull nijika/nijika:latest

# Run with environment variables
docker run -e OPENAI_API_KEY=your_key nijika/nijika:latest
```

### Method 4: Conda Installation

```bash
# Create a new environment
conda create -n nijika python=3.9
conda activate nijika

# Install nijika
pip install nijika
```

## 🔧 Virtual Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv nijika-env

# Activate (Windows)
nijika-env\Scripts\activate

# Activate (macOS/Linux)
source nijika-env/bin/activate

# Install nijika
pip install nijika
```

### Using conda

```bash
# Create and activate environment
conda create -n nijika python=3.9
conda activate nijika

# Install nijika
pip install nijika
```

### Using pipenv

```bash
# Install pipenv if not already installed
pip install pipenv

# Create Pipfile and install
pipenv install nijika

# Activate environment
pipenv shell
```

## 🔑 API Key Configuration

### Environment Variables

Create a `.env` file in your project directory:

```env
# OpenAI
OPENAI_API_KEY=your_openai_key_here
OPENAI_ORG_ID=your_org_id_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key_here

# Google
GOOGLE_API_KEY=your_google_key_here
GOOGLE_PROJECT_ID=your_project_id_here

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
AZURE_OPENAI_API_VERSION=2023-05-15
```

### System Environment Variables

#### Windows
```cmd
set OPENAI_API_KEY=your_openai_key_here
set ANTHROPIC_API_KEY=your_anthropic_key_here
```

#### macOS/Linux
```bash
export OPENAI_API_KEY=your_openai_key_here
export ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Configuration File

Create a `config.yaml` file:

```yaml
providers:
  - name: openai
    provider_type: openai
    api_key: ${OPENAI_API_KEY}
    model: gpt-3.5-turbo
    
  - name: anthropic
    provider_type: anthropic
    api_key: ${ANTHROPIC_API_KEY}
    model: claude-3-sonnet-20240229

memory:
  backend: sqlite
  db_path: nijika_memory.db
  
rag:
  enabled: true
  chunk_size: 1000
  top_k: 5
```

## 🐳 Docker Setup

### Basic Docker Setup

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install nijika
RUN pip install nijika

# Copy your application
COPY . .

# Set environment variables
ENV OPENAI_API_KEY=""
ENV ANTHROPIC_API_KEY=""

# Run your application
CMD ["python", "your_app.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  nijika-app:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
    
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=nijika
      - POSTGRES_USER=nijika
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## 📦 Optional Dependencies

### Vector Databases
```bash
# For advanced RAG with vector databases
pip install "nijika[vector]"

# Specific vector databases
pip install chromadb  # ChromaDB
pip install pinecone-client  # Pinecone
pip install qdrant-client  # Qdrant
```

### Database Backends
```bash
# PostgreSQL support
pip install "nijika[postgres]"

# MongoDB support
pip install "nijika[mongo]"

# Redis support
pip install "nijika[redis]"
```

### Additional Tools
```bash
# Web scraping tools
pip install "nijika[web]"

# Image processing
pip install "nijika[vision]"

# Audio processing
pip install "nijika[audio]"
```

## ✅ Verification

### Basic Installation Check

```python
import nijika
print(f"Nijika version: {nijika.__version__}")

# Check available components
from nijika import Agent, AgentConfig, ProviderType
print("Core components imported successfully!")
```

### Full System Check

```python
import asyncio
from nijika import Agent, AgentConfig, ProviderType

async def test_installation():
    # Test basic configuration
    config = AgentConfig(
        name="test_agent",
        providers=[
            {
                "name": "openai",
                "provider_type": ProviderType.OPENAI,
                "api_key": "test-key",
                "model": "gpt-3.5-turbo"
            }
        ],
        tools=["echo"]
    )
    
    # Create agent (without executing)
    agent = Agent(config)
    print(f"✅ Agent created: {agent.id}")
    
    # Test memory system
    stats = agent.memory_manager.get_stats()
    print(f"✅ Memory backend: {stats['backend_type']}")
    
    # Test tool registry
    tools = agent.tool_registry.list_tools()
    print(f"✅ Available tools: {tools}")
    
    print("🎉 Installation verified successfully!")

# Run verification
asyncio.run(test_installation())
```

## 🔧 Development Setup

### For Contributors

```bash
# Clone the repository
git clone https://github.com/your-org/nijika.git
cd nijika

# Create development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
flake8 nijika/
black nijika/
```

### Development Dependencies

```bash
# Testing
pip install pytest pytest-asyncio pytest-cov

# Linting and formatting
pip install flake8 black isort

# Documentation
pip install sphinx sphinx-rtd-theme

# Type checking
pip install mypy

# Pre-commit hooks
pip install pre-commit
```

## 🚨 Troubleshooting

### Common Installation Issues

#### Python Version Issues
```bash
# Check Python version
python --version

# Use specific Python version
python3.9 -m pip install nijika
```

#### Permission Errors
```bash
# Use user installation
pip install --user nijika

# Or use sudo (not recommended)
sudo pip install nijika
```

#### SSL Certificate Issues
```bash
# Upgrade certificates
pip install --upgrade certifi

# Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org nijika
```

#### Dependency Conflicts
```bash
# Create clean environment
python -m venv clean-env
source clean-env/bin/activate
pip install nijika
```

### Platform-Specific Issues

#### Windows
- Install Microsoft Visual C++ Build Tools if compilation fails
- Use Windows Subsystem for Linux (WSL) for better compatibility

#### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for system dependencies: `brew install python`

#### Linux
- Install build essentials: `sudo apt-get install build-essential`
- Install Python development headers: `sudo apt-get install python3-dev`

### Memory Issues

#### SQLite Database
```bash
# Check database permissions
ls -la nijika_memory.db

# Reset database
rm nijika_memory.db
```

#### Large Memory Usage
```python
# Configure memory limits
config = AgentConfig(
    memory_config={
        "max_entries": 1000,
        "cleanup_interval": 1800
    }
)
```

## 📞 Getting Help

### Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Community support and questions
- **Documentation**: Comprehensive guides and API reference
- **Discord**: Real-time community chat

### Before Asking for Help
1. Check the [FAQ](faq.md)
2. Search existing GitHub issues
3. Try the troubleshooting steps above
4. Provide system information and error messages

### System Information
```python
import sys
import platform
import nijika

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Nijika: {nijika.__version__}")

# Check dependencies
import pkg_resources
packages = ['openai', 'anthropic', 'aiohttp', 'sqlalchemy']
for package in packages:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f"{package}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"{package}: Not installed")
```

## 🎯 Next Steps

After successful installation:

1. **[Quick Start Guide](quick-start.md)** - Build your first agent
2. **[Configuration Guide](configuration.md)** - Detailed configuration options
3. **[API Reference](api/)** - Complete API documentation
4. **[Tutorials](tutorials/)** - Step-by-step guides
5. **[Examples](examples/)** - Real-world use cases

Happy coding with Nijika! 🚀 