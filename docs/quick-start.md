# Quick Start Guide

Get your first Nijika AI Agent up and running in just a few minutes!

## 🚀 Installation

### 1. Install Nijika

```bash
pip install nijika
```

Or install from source:

```bash
git clone https://github.com/your-org/nijika.git
cd nijika
pip install -e .
```

### 2. Set Up API Keys

Create a `.env` file in your project directory:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
AZURE_OPENAI_API_KEY=your_azure_key_here
```

## 🤖 Your First Agent

### Simple Agent Example

```python
import asyncio
from nijika import Agent, AgentConfig, ProviderType

async def main():
    # Configure your agent
    config = AgentConfig(
        name="my_first_agent",
        providers=[
            {
                "name": "openai",
                "provider_type": ProviderType.OPENAI,
                "api_key": "your-openai-api-key",
                "model": "gpt-3.5-turbo"
            }
        ],
        tools=["echo", "calculator"]
    )
    
    # Create the agent
    agent = Agent(config)
    
    # Execute a simple query
    result = await agent.execute("What is 15 * 7 + 3?")
    print(f"Result: {result}")

# Run the agent
asyncio.run(main())
```

### Expected Output

```
INFO:nijika.agent.my_first_agent: Agent 'my_first_agent' initialized
INFO:nijika.agent.my_first_agent: Execution completed successfully
Result: {'status': 'success', 'final_result': {'type': 'tool', 'result': 108}}
```

## 🛠️ Adding More Features

### With RAG System

```python
from nijika import Agent, AgentConfig, RAGSystem

async def main():
    config = AgentConfig(
        name="smart_agent",
        providers=[{"name": "openai", "provider_type": ProviderType.OPENAI}],
        rag_config={"enabled": True, "chunk_size": 1000}
    )
    
    agent = Agent(config)
    
    # Add documents to RAG
    await agent.rag_system.add_document(
        "Nijika is a powerful AI agent framework for building intelligent applications.",
        {"source": "documentation", "type": "overview"}
    )
    
    # Query with RAG context
    result = await agent.execute("What is Nijika?")
    print(f"Answer: {result}")

asyncio.run(main())
```

### With Workflows

```python
from nijika import Agent, AgentConfig, WorkflowEngine

async def main():
    config = AgentConfig(
        name="workflow_agent",
        providers=[{"name": "openai", "provider_type": ProviderType.OPENAI}],
        tools=["echo", "calculator", "http_request"]
    )
    
    agent = Agent(config)
    
    # Create a workflow
    workflow = {
        "name": "data_processing",
        "steps": [
            {"name": "greeting", "type": "echo", "params": {"message": "Starting workflow"}},
            {"name": "calculation", "type": "calculator", "params": {"expression": "10 + 5"}},
            {"name": "completion", "type": "echo", "params": {"message": "Workflow complete"}}
        ]
    }
    
    # Execute workflow
    result = await agent.workflow_engine.execute_workflow("data_processing", workflow)
    print(f"Workflow result: {result}")

asyncio.run(main())
```

## 📊 Built-in Tools

Nijika comes with several built-in tools:

- **echo**: Simple message echoing
- **calculator**: Mathematical calculations
- **http_request**: HTTP API calls
- **file_read**: File system operations

### Using Tools

```python
# Calculator tool
result = await agent.execute("Calculate the square root of 144")

# HTTP request tool
result = await agent.execute("Make a GET request to https://api.github.com/users/octocat")

# File operations
result = await agent.execute("Read the contents of data.txt")
```

## 🧠 Memory System

Agents automatically store conversation history and execution context:

```python
# Get conversation history
history = await agent.memory_manager.get_conversation_history(agent.id, limit=5)

# Get execution history
executions = await agent.memory_manager.get_execution_history(agent.id, limit=5)

# Search knowledge base
knowledge = await agent.memory_manager.search_knowledge("AI agents", agent.id)
```

## 🎯 Planning Engine

The planning engine automatically decomposes complex tasks:

```python
# Complex task - automatically planned and executed
result = await agent.execute(
    "Analyze the latest tech news, summarize key trends, and save to a report file"
)

# View the generated plan
plan = await agent.planning_engine.create_plan(
    "Build a customer support chatbot",
    {"agent_id": agent.id}
)
print(f"Plan steps: {len(plan.steps)}")
```

## 🔧 Configuration Options

### Basic Configuration

```python
config = AgentConfig(
    name="my_agent",
    providers=[...],
    tools=["echo", "calculator"],
    memory_config={
        "backend": "sqlite",
        "db_path": "agent_memory.db"
    },
    rag_config={
        "enabled": True,
        "chunk_size": 1000,
        "top_k": 5
    }
)
```

### Advanced Configuration

```python
config = AgentConfig(
    name="advanced_agent",
    providers=[
        {
            "name": "openai",
            "provider_type": ProviderType.OPENAI,
            "api_key": "your-key",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        }
    ],
    tools=["echo", "calculator", "http_request", "file_read"],
    memory_config={
        "backend": "sqlite",
        "db_path": "advanced_memory.db",
        "max_entries": 10000,
        "cleanup_interval": 3600
    },
    rag_config={
        "enabled": True,
        "chunk_size": 1000,
        "overlap": 200,
        "top_k": 10,
        "similarity_threshold": 0.7
    },
    planning_config={
        "strategy": "hierarchical",
        "max_steps": 20,
        "timeout": 300
    }
)
```

## 🚀 Next Steps

Now that you have your first agent running, explore:

1. **[Configuration Guide](configuration.md)** - Detailed configuration options
2. **[Custom Tools Tutorial](tutorials/custom-tools.md)** - Build your own tools
3. **[Workflow Patterns](tutorials/workflows.md)** - Complex workflow examples
4. **[Industry Examples](examples/)** - Real-world use cases
5. **[API Reference](api/)** - Complete API documentation

## 🆘 Troubleshooting

### Common Issues

**ModuleNotFoundError**: Make sure Nijika is installed:
```bash
pip install nijika
```

**API Key Errors**: Verify your API keys are correct and have sufficient credits.

**Memory Issues**: Check SQLite database permissions and disk space.

**Tool Not Found**: Ensure tools are properly registered in the agent configuration.

### Getting Help

- Check the [FAQ](faq.md)
- Browse [GitHub Issues](https://github.com/your-org/nijika/issues)
- Join the [Community Discussions](https://github.com/your-org/nijika/discussions)

## 📝 Example Projects

Check out these complete example projects:

- [Customer Support Bot](examples/customer-support.md)
- [Data Analysis Agent](examples/data-analysis.md)
- [Content Generation System](examples/content-generation.md)
- [Financial Advisor Bot](examples/financial-advisor.md)

Happy building with Nijika! 🎉 