# Contributing to Nijika AI Agent Framework

Thank you for your interest in contributing to the Nijika AI Agent Framework! This guide will help you get started with contributing to our project.

## 🌟 Ways to Contribute

We welcome contributions in many forms:

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Fix bugs, add features, or improve performance
- **Documentation**: Improve docs, tutorials, or examples
- **Testing**: Write tests or test new features
- **Community Support**: Help other users in discussions

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Basic understanding of async/await in Python

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/nijika.git
   cd nijika
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Verify Setup**
   ```bash
   # Run tests
   pytest
   
   # Run linting
   flake8 nijika/
   black --check nijika/
   
   # Type checking
   mypy nijika/
   ```

### Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number
   ```

2. **Make Changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run full test suite
   pytest
   
   # Run specific tests
   pytest tests/test_agent.py
   
   # Run with coverage
   pytest --cov=nijika
   ```

4. **Commit Changes**
   ```bash
   # Stage changes
   git add .
   
   # Commit with descriptive message
   git commit -m "feat: add new planning strategy"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

## 📝 Code Style Guidelines

### Python Code Style

We follow PEP 8 with some modifications:

- **Line Length**: 88 characters (Black default)
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Required for public APIs

### Code Formatting

We use automated formatting tools:

```bash
# Format code
black nijika/

# Sort imports
isort nijika/

# Lint code
flake8 nijika/

# Type checking
mypy nijika/
```

### Example Code Style

```python
"""
Module docstring describing the purpose.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from nijika.core.base import BaseComponent


class ExampleAgent(BaseComponent):
    """
    Example agent implementation.
    
    Args:
        name: Agent name
        config: Configuration dictionary
        
    Attributes:
        name: Agent name
        config: Agent configuration
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__()
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"nijika.agent.{name}")
    
    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute a query.
        
        Args:
            query: The query to execute
            
        Returns:
            Execution result dictionary
            
        Raises:
            ValueError: If query is empty
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        self.logger.info(f"Executing query: {query}")
        
        # Implementation here
        result = {"status": "success", "result": "processed"}
        
        return result
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test fixtures
└── conftest.py    # Pytest configuration
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, AsyncMock

from nijika import Agent, AgentConfig


class TestAgent:
    """Test suite for Agent class."""
    
    @pytest.fixture
    def agent_config(self):
        """Fixture providing test agent configuration."""
        return AgentConfig(
            name="test_agent",
            providers=[{
                "name": "mock",
                "provider_type": "mock",
                "api_key": "test-key"
            }],
            tools=["echo"]
        )
    
    @pytest.fixture
    async def agent(self, agent_config):
        """Fixture providing configured agent."""
        agent = Agent(agent_config)
        yield agent
        # Cleanup if needed
    
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "test_agent"
        assert agent.id is not None
        assert len(agent.providers) == 1
    
    async def test_execute_simple_query(self, agent):
        """Test executing a simple query."""
        result = await agent.execute("Hello world")
        
        assert result["status"] == "success"
        assert "result" in result
    
    async def test_execute_empty_query_raises_error(self, agent):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await agent.execute("")
    
    @pytest.mark.parametrize("query,expected", [
        ("Hello", "success"),
        ("Calculate 2+2", "success"),
        ("Complex query", "success"),
    ])
    async def test_execute_various_queries(self, agent, query, expected):
        """Test executing various types of queries."""
        result = await agent.execute(query)
        assert result["status"] == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agent.py

# Run with coverage
pytest --cov=nijika --cov-report=html

# Run only fast tests
pytest -m "not slow"

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_agent.py::TestAgent::test_agent_initialization
```

## 📚 Documentation Guidelines

### Documentation Types

1. **API Documentation**: Docstrings in code
2. **User Guides**: Step-by-step tutorials
3. **Reference**: Complete API reference
4. **Examples**: Real-world use cases

### Writing Documentation

```python
def create_agent(config: AgentConfig) -> Agent:
    """
    Create a new agent instance.
    
    This function creates and initializes a new agent with the provided
    configuration. The agent will be ready to execute queries immediately.
    
    Args:
        config: Agent configuration containing providers, tools, and settings
        
    Returns:
        Configured and initialized agent instance
        
    Raises:
        ValueError: If configuration is invalid
        ConfigurationError: If required providers are missing
        
    Example:
        >>> config = AgentConfig(
        ...     name="my_agent",
        ...     providers=[{"name": "openai", "provider_type": ProviderType.OPENAI}]
        ... )
        >>> agent = create_agent(config)
        >>> result = await agent.execute("Hello world")
        
    Note:
        The agent will automatically initialize all configured providers
        and tools during creation.
    """
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Try the latest version
3. Create minimal reproduction case
4. Gather system information

### Bug Report Template

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version:
- Nijika version:
- Operating system:
- Relevant dependencies:

## Minimal Code Example
```python
# Minimal code that reproduces the issue
```

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What other approaches were considered?

## Additional Context
Any other relevant information
```

## 🔍 Code Review Process

### For Contributors

1. **Self-Review**: Review your own code before submitting
2. **Tests**: Ensure all tests pass
3. **Documentation**: Update relevant documentation
4. **Description**: Provide clear PR description

### Review Criteria

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it properly documented?
- **Performance**: Does it meet performance requirements?
- **Security**: Are there any security concerns?

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🏗️ Architecture Guidelines

### Core Principles

1. **Modularity**: Components should be loosely coupled
2. **Extensibility**: Easy to add new providers, tools, etc.
3. **Async-First**: Use async/await throughout
4. **Type Safety**: Use type hints consistently
5. **Error Handling**: Graceful error handling and recovery

### Component Structure

```python
# Base component pattern
class BaseComponent(ABC):
    """Base class for all components."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup component resources."""
        pass
```

### Adding New Providers

```python
# Provider implementation example
class CustomProvider(BaseProvider):
    """Custom AI provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config["api_key"]
        self.model = config.get("model", "default")
    
    async def complete(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a prompt using the custom provider."""
        # Implementation here
        pass
    
    async def validate_config(self) -> bool:
        """Validate provider configuration."""
        return bool(self.api_key)
```

## 🚀 Release Process

### Version Numbering

We use Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

1. **Update Version**: Update version in `__init__.py`
2. **Update Changelog**: Add release notes
3. **Run Tests**: Ensure all tests pass
4. **Update Documentation**: Reflect any changes
5. **Create Tag**: `git tag v1.0.0`
6. **Push Release**: Push tag to trigger CI/CD

## 🤝 Community Guidelines

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community support
- **Discord**: Real-time chat and collaboration
- **Email**: Private or sensitive matters

### Recognition

We recognize contributors in:
- Release notes
- Contributors file
- Documentation acknowledgments
- Community highlights

## 📞 Getting Help

### Documentation
- [API Reference](docs/api/)
- [User Guides](docs/)
- [Examples](examples/)

### Community Support
- [GitHub Discussions](https://github.com/your-org/nijika/discussions)
- [Discord Server](https://discord.gg/nijika)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/nijika)

### Maintainer Contact
- Email: maintainers@nijika.ai
- GitHub: @nijika-maintainers

## 🙏 Thank You

Thank you for contributing to Nijika! Your contributions help make AI agents more accessible and powerful for everyone.

---

*This contributing guide is a living document. Please suggest improvements!* 