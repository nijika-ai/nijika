# Frequently Asked Questions (FAQ)

## 🚀 Getting Started

### Q: What is the Nijika AI Agent Framework?

**A:** Nijika is a comprehensive, industry-agnostic AI agent framework designed for building intelligent applications. It provides multi-provider support, workflow orchestration, memory management, RAG capabilities, and intelligent planning - all in a production-ready package.

### Q: What makes Nijika different from other AI frameworks?

**A:** Nijika stands out with:
- **Multi-provider support** (OpenAI, Anthropic, Google, Azure) with automatic failover
- **Industry-agnostic design** suitable for finance, healthcare, e-commerce, and education
- **Built-in RAG system** for document processing and context retrieval
- **Intelligent planning engine** with multiple strategies
- **Persistent memory management** across sessions
- **Production-ready** with monitoring, security, and scalability features

### Q: Do I need to know Python to use Nijika?

**A:** Yes, Nijika is a Python framework. You'll need basic Python knowledge, especially understanding of async/await patterns. However, the framework is designed to be developer-friendly with comprehensive documentation and examples.

## 🔧 Installation & Setup

### Q: What are the system requirements?

**A:** Minimum requirements:
- Python 3.8+
- 2GB RAM (4GB recommended)
- 500MB disk space
- Internet connection for AI provider APIs

### Q: How do I install Nijika?

**A:** Install via pip:
```bash
pip install nijika
```

For development:
```bash
pip install "nijika[dev]"
```

### Q: I'm getting a "ModuleNotFoundError" when importing Nijika. What should I do?

**A:** This usually means Nijika isn't installed in your current environment. Try:
1. Check if you're in the correct virtual environment
2. Reinstall: `pip install nijika`
3. For development setup: `pip install -e .`

### Q: How do I set up API keys?

**A:** Create a `.env` file in your project directory:
```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

Or set environment variables directly in your system.

## 🤖 Agent Configuration

### Q: How do I create my first agent?

**A:** Here's a minimal example:
```python
import asyncio
from nijika import Agent, AgentConfig, ProviderType

async def main():
    config = AgentConfig(
        name="my_agent",
        providers=[{
            "name": "openai",
            "provider_type": ProviderType.OPENAI,
            "api_key": "your-api-key",
            "model": "gpt-3.5-turbo"
        }],
        tools=["echo", "calculator"]
    )
    
    agent = Agent(config)
    result = await agent.execute("Hello, world!")
    print(result)

asyncio.run(main())
```

### Q: Can I use multiple AI providers simultaneously?

**A:** Yes! Nijika supports multiple providers with automatic load balancing and failover:
```python
config = AgentConfig(
    name="multi_provider_agent",
    providers=[
        {
            "name": "openai",
            "provider_type": ProviderType.OPENAI,
            "api_key": "your-openai-key",
            "model": "gpt-4"
        },
        {
            "name": "anthropic",
            "provider_type": ProviderType.ANTHROPIC,
            "api_key": "your-anthropic-key",
            "model": "claude-3-sonnet-20240229"
        }
    ]
)
```

### Q: How do I configure memory settings?

**A:** Configure memory in your agent config:
```python
config = AgentConfig(
    name="my_agent",
    memory_config={
        "backend": "sqlite",
        "db_path": "agent_memory.db",
        "max_entries": 10000,
        "cleanup_interval": 3600
    }
)
```

## 🛠️ Tools & Capabilities

### Q: What built-in tools are available?

**A:** Nijika includes these built-in tools:
- **echo**: Message echoing and text processing
- **calculator**: Mathematical calculations
- **http_request**: HTTP API calls
- **file_read**: File system operations

### Q: How do I create custom tools?

**A:** Create a custom tool by extending `BaseTool`:
```python
from nijika.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "My custom tool"
    
    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Your implementation here
        return {"result": "success"}

# Register in agent config
config = AgentConfig(
    name="my_agent",
    tools=["echo", CustomTool]
)
```

### Q: How do I restrict tool access for security?

**A:** Configure tool restrictions:
```python
tool_config = {
    "http_request": {
        "allowed_domains": ["api.github.com", "httpbin.org"],
        "timeout": 30
    },
    "file_read": {
        "allowed_extensions": [".txt", ".md", ".json"],
        "max_file_size": 1048576  # 1MB
    }
}
```

## 📄 RAG (Retrieval-Augmented Generation)

### Q: What is RAG and why should I use it?

**A:** RAG (Retrieval-Augmented Generation) allows your agent to access and use information from your documents. It's useful for:
- Building knowledge bases
- Document Q&A systems
- Context-aware responses
- Reducing hallucinations

### Q: How do I set up RAG?

**A:** Enable RAG in your agent configuration:
```python
config = AgentConfig(
    name="rag_agent",
    rag_config={
        "enabled": True,
        "chunk_size": 1000,
        "top_k": 5,
        "similarity_threshold": 0.7
    }
)

# Add documents
await agent.rag_system.add_document(
    "Your document content here",
    {"source": "manual", "type": "documentation"}
)
```

### Q: What document formats are supported?

**A:** Currently supported formats:
- Plain text (.txt)
- Markdown (.md)
- JSON (.json)
- CSV (.csv)
- PDF (with additional dependencies)

### Q: Can I use external vector databases?

**A:** Yes! Nijika supports multiple vector stores:
```python
rag_config = {
    "enabled": True,
    "vector_store": {
        "type": "chroma",  # or "pinecone", "qdrant"
        "persist_directory": "./chroma_db"
    }
}
```

## 🔄 Workflows & Planning

### Q: What's the difference between workflows and planning?

**A:** 
- **Workflows**: Pre-defined sequences of steps for specific tasks
- **Planning**: Dynamic task decomposition based on the query

### Q: How do I create a workflow?

**A:** Define a workflow structure:
```python
workflow = {
    "name": "data_processing",
    "steps": [
        {"name": "validate", "type": "tool", "tool": "validator"},
        {"name": "process", "type": "tool", "tool": "processor"},
        {"name": "save", "type": "tool", "tool": "file_writer"}
    ]
}

result = await agent.workflow_engine.execute_workflow("data_processing", workflow)
```

### Q: What planning strategies are available?

**A:** Nijika supports multiple planning strategies:
- **Sequential**: Step-by-step execution
- **Hierarchical**: Nested task decomposition
- **Parallel**: Concurrent execution
- **Reactive**: Dynamic adaptation
- **Goal-oriented**: Objective-driven planning

## 🧠 Memory Management

### Q: How does memory work in Nijika?

**A:** Nijika maintains different types of memory:
- **Conversation**: Chat history and context
- **Execution**: Task execution results
- **Knowledge**: Learned information
- **Episodic**: Temporal event sequences

### Q: How do I access conversation history?

**A:** Use the memory manager:
```python
# Get recent conversations
history = await agent.memory_manager.get_conversation_history(agent.id, limit=10)

# Get execution history
executions = await agent.memory_manager.get_execution_history(agent.id, limit=5)

# Search knowledge
knowledge = await agent.memory_manager.search_knowledge("AI agents", agent.id)
```

### Q: Can I use external databases for memory?

**A:** Yes! Nijika supports multiple backends:
- SQLite (default)
- PostgreSQL
- MongoDB
- Redis

## 🔐 Security & Production

### Q: How do I secure my API keys?

**A:** Best practices for API key security:
1. Use environment variables
2. Never commit keys to version control
3. Use secret management services (AWS Secrets Manager, Azure Key Vault)
4. Rotate keys regularly

### Q: Is Nijika production-ready?

**A:** Yes! Nijika includes production features:
- Error handling and recovery
- Monitoring and metrics
- Logging and audit trails
- Rate limiting
- Circuit breaker patterns
- Horizontal scaling support

### Q: How do I monitor my agents in production?

**A:** Enable monitoring in your configuration:
```python
config = AgentConfig(
    name="production_agent",
    monitoring_config={
        "enabled": True,
        "metrics_port": 9090,
        "log_level": "INFO"
    }
)
```

## 🚨 Troubleshooting

### Q: My agent is running slowly. How can I optimize performance?

**A:** Performance optimization tips:
1. Use faster models (gpt-3.5-turbo vs gpt-4)
2. Reduce token limits
3. Use Redis for memory backend
4. Optimize RAG chunk sizes
5. Enable caching
6. Use connection pooling

### Q: I'm getting "maximum recursion depth exceeded" errors. What's wrong?

**A:** This usually indicates circular references in your data. The framework includes safeguards, but you can:
1. Check for circular references in your custom tools
2. Limit execution depth in planning config
3. Review your data structures

### Q: API calls are failing. How do I debug?

**A:** Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in agent config
config = AgentConfig(
    name="debug_agent",
    debug=True,
    log_level="DEBUG"
)
```

### Q: How do I handle rate limiting from AI providers?

**A:** Nijika includes built-in rate limiting:
```python
provider_config = {
    "name": "openai",
    "provider_type": ProviderType.OPENAI,
    "rate_limit": {
        "requests_per_minute": 60,
        "tokens_per_minute": 90000
    }
}
```

## 💡 Advanced Usage

### Q: Can I run multiple agents simultaneously?

**A:** Yes! Each agent is independent:
```python
agent1 = Agent(config1)
agent2 = Agent(config2)

# Run concurrently
results = await asyncio.gather(
    agent1.execute("Task 1"),
    agent2.execute("Task 2")
)
```

### Q: How do I implement custom memory backends?

**A:** Extend the `BaseMemoryBackend` class:
```python
from nijika.core.memory import BaseMemoryBackend

class CustomMemoryBackend(BaseMemoryBackend):
    async def store(self, entry: MemoryEntry) -> str:
        # Your implementation
        pass
    
    async def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        # Your implementation
        pass
```

### Q: Can I use Nijika with other frameworks?

**A:** Yes! Nijika is designed to be framework-agnostic:
- FastAPI integration for web APIs
- Streamlit for user interfaces
- Jupyter notebooks for experimentation
- Docker for containerization

### Q: How do I implement custom planning strategies?

**A:** Extend the `BasePlanner` class:
```python
from nijika.planning import BasePlanner

class CustomPlanner(BasePlanner):
    async def plan(self, task: str, context: Dict) -> Plan:
        # Your custom planning logic
        pass
```

## 📊 Monitoring & Analytics

### Q: What metrics does Nijika collect?

**A:** Default metrics include:
- Request count and duration
- Error rates
- Memory usage
- Provider response times
- Tool execution times

### Q: How do I export metrics to Prometheus?

**A:** Configure Prometheus export:
```python
metrics_config = {
    "enabled": True,
    "backend": "prometheus",
    "port": 9090
}
```

### Q: Can I add custom metrics?

**A:** Yes! Use the metrics collector:
```python
from nijika.monitoring import MetricsCollector

metrics = MetricsCollector()
metrics.increment_counter("custom_metric", {"label": "value"})
metrics.record_histogram("response_time", 0.5)
```

## 🌍 Community & Support

### Q: Where can I get help?

**A:** Support channels:
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Community questions and support
- **Documentation**: Comprehensive guides and examples
- **Discord**: Real-time community chat

### Q: How do I contribute to Nijika?

**A:** See our [Contributing Guide](../CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing procedures
- Pull request process

### Q: Is there a roadmap for future features?

**A:** Yes! Check our GitHub project board for:
- Upcoming features
- Current development status
- Community requests
- Release timeline

## 📚 Learning Resources

### Q: Where can I find examples?

**A:** Check these resources:
- [Examples directory](../examples/) - Working code examples
- [Tutorials](tutorials/) - Step-by-step guides
- [Industry examples](examples/) - Real-world use cases
- [API reference](api/) - Complete documentation

### Q: Are there video tutorials?

**A:** We're working on video content! Currently available:
- Documentation walkthroughs
- Architecture deep-dives
- Best practices guides
- Community presentations

### Q: How do I stay updated?

**A:** Follow these channels:
- GitHub releases for version updates
- GitHub discussions for announcements
- Discord for real-time updates
- Blog posts for feature highlights

## 🔄 Migration & Compatibility

### Q: How do I migrate from other frameworks?

**A:** Migration guides available for:
- LangChain → Nijika
- AutoGen → Nijika
- Custom solutions → Nijika

### Q: Is Nijika backward compatible?

**A:** We follow semantic versioning:
- Major versions may have breaking changes
- Minor versions add features (backward compatible)
- Patch versions fix bugs (backward compatible)

### Q: Can I use Nijika with existing code?

**A:** Yes! Nijika is designed to integrate with existing systems:
- Wrap existing functions as tools
- Use existing databases for memory
- Integrate with existing APIs
- Deploy alongside current infrastructure

---

## 🆘 Still Need Help?

If you can't find the answer to your question here:

1. **Search the documentation** - Use the search function
2. **Check GitHub issues** - Someone might have asked the same question
3. **Join the community** - Ask in GitHub Discussions or Discord
4. **Create an issue** - For bugs or feature requests

We're here to help you succeed with Nijika! 🚀 