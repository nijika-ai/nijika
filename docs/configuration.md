# Configuration Guide

This guide covers all configuration options for the Nijika AI Agent Framework.

## 🔧 Agent Configuration

### Basic Configuration

```python
from nijika import AgentConfig, ProviderType

config = AgentConfig(
    name="my_agent",
    providers=[
        {
            "name": "openai",
            "provider_type": ProviderType.OPENAI,
            "api_key": "your-api-key",
            "model": "gpt-3.5-turbo"
        }
    ],
    tools=["echo", "calculator"]
)
```

### Complete Configuration

```python
config = AgentConfig(
    # Basic settings
    name="advanced_agent",
    description="Advanced AI agent with full configuration",
    
    # Provider configuration
    providers=[
        {
            "name": "openai",
            "provider_type": ProviderType.OPENAI,
            "api_key": "your-openai-key",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 30,
            "retry_attempts": 3
        },
        {
            "name": "anthropic",
            "provider_type": ProviderType.ANTHROPIC,
            "api_key": "your-anthropic-key",
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000
        }
    ],
    
    # Tool configuration
    tools=["echo", "calculator", "http_request", "file_read"],
    
    # Memory configuration
    memory_config={
        "backend": "sqlite",
        "db_path": "agent_memory.db",
        "max_entries": 10000,
        "cleanup_interval": 3600,
        "default_ttl": 86400
    },
    
    # RAG configuration
    rag_config={
        "enabled": True,
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 10,
        "similarity_threshold": 0.7,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    
    # Planning configuration
    planning_config={
        "strategy": "hierarchical",
        "max_steps": 20,
        "timeout": 300,
        "retry_failed_steps": True
    },
    
    # Workflow configuration
    workflow_config={
        "max_parallel_steps": 5,
        "step_timeout": 60,
        "retry_attempts": 2
    }
)
```

## 🌐 Provider Configuration

### OpenAI Provider

```python
openai_config = {
    "name": "openai",
    "provider_type": ProviderType.OPENAI,
    "api_key": "your-api-key",
    "organization": "your-org-id",  # Optional
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "timeout": 30,
    "retry_attempts": 3,
    "base_url": "https://api.openai.com/v1"  # Optional
}
```

### Anthropic Provider

```python
anthropic_config = {
    "name": "anthropic",
    "provider_type": ProviderType.ANTHROPIC,
    "api_key": "your-api-key",
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 4000,
    "temperature": 0.7,
    "timeout": 30,
    "retry_attempts": 3
}
```

### Google Provider

```python
google_config = {
    "name": "google",
    "provider_type": ProviderType.GOOGLE,
    "api_key": "your-api-key",
    "project_id": "your-project-id",
    "model": "gemini-pro",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30
}
```

### Azure OpenAI Provider

```python
azure_config = {
    "name": "azure",
    "provider_type": ProviderType.AZURE,
    "api_key": "your-api-key",
    "endpoint": "https://your-resource.openai.azure.com/",
    "api_version": "2023-05-15",
    "deployment_name": "your-deployment",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

## 🧠 Memory Configuration

### SQLite Backend (Default)

```python
memory_config = {
    "backend": "sqlite",
    "db_path": "agent_memory.db",
    "max_entries": 10000,
    "cleanup_interval": 3600,  # 1 hour
    "default_ttl": 86400,      # 24 hours
    "connection_pool_size": 5
}
```

### PostgreSQL Backend

```python
memory_config = {
    "backend": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "nijika",
    "username": "nijika_user",
    "password": "your-password",
    "max_connections": 20,
    "max_entries": 100000,
    "cleanup_interval": 1800,
    "default_ttl": 86400
}
```

### Redis Backend

```python
memory_config = {
    "backend": "redis",
    "host": "localhost",
    "port": 6379,
    "password": "your-password",
    "db": 0,
    "max_connections": 10,
    "default_ttl": 86400
}
```

## 📄 RAG Configuration

### Basic RAG Setup

```python
rag_config = {
    "enabled": True,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "top_k": 5,
    "similarity_threshold": 0.7
}
```

### Advanced RAG Setup

```python
rag_config = {
    "enabled": True,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "top_k": 10,
    "similarity_threshold": 0.7,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "vector_store": {
        "type": "chroma",
        "persist_directory": "./chroma_db",
        "collection_name": "nijika_documents"
    },
    "text_splitter": {
        "type": "recursive",
        "separators": ["\n\n", "\n", " ", ""]
    },
    "retrieval_strategy": "similarity",
    "rerank_results": True,
    "max_document_size": 10000000  # 10MB
}
```

### Vector Store Options

#### ChromaDB

```python
vector_store_config = {
    "type": "chroma",
    "persist_directory": "./chroma_db",
    "collection_name": "documents",
    "embedding_function": "sentence-transformers"
}
```

#### Pinecone

```python
vector_store_config = {
    "type": "pinecone",
    "api_key": "your-pinecone-key",
    "environment": "us-west1-gcp",
    "index_name": "nijika-index",
    "dimension": 384
}
```

#### Qdrant

```python
vector_store_config = {
    "type": "qdrant",
    "host": "localhost",
    "port": 6333,
    "collection_name": "nijika_vectors",
    "vector_size": 384
}
```

## 🎯 Planning Configuration

### Planning Strategies

```python
# Sequential planning
planning_config = {
    "strategy": "sequential",
    "max_steps": 10,
    "timeout": 300
}

# Hierarchical planning
planning_config = {
    "strategy": "hierarchical",
    "max_steps": 20,
    "max_depth": 3,
    "timeout": 600
}

# Parallel planning
planning_config = {
    "strategy": "parallel",
    "max_parallel_steps": 5,
    "timeout": 300
}

# Reactive planning
planning_config = {
    "strategy": "reactive",
    "reaction_threshold": 0.8,
    "max_reactions": 5
}

# Goal-oriented planning
planning_config = {
    "strategy": "goal_oriented",
    "goal_threshold": 0.9,
    "max_iterations": 10
}
```

## 🔄 Workflow Configuration

### Basic Workflow Setup

```python
workflow_config = {
    "max_parallel_steps": 3,
    "step_timeout": 60,
    "retry_attempts": 2,
    "failure_strategy": "continue"  # or "stop"
}
```

### Advanced Workflow Setup

```python
workflow_config = {
    "max_parallel_steps": 5,
    "step_timeout": 60,
    "retry_attempts": 3,
    "failure_strategy": "continue",
    "execution_mode": "async",
    "checkpoint_enabled": True,
    "checkpoint_interval": 5,
    "recovery_enabled": True,
    "metrics_enabled": True
}
```

## 🔧 Tool Configuration

### Built-in Tools

```python
# Enable specific tools
tools = ["echo", "calculator", "http_request", "file_read"]

# Enable all tools
tools = ["*"]

# Tool-specific configuration
tool_config = {
    "http_request": {
        "timeout": 30,
        "max_retries": 3,
        "allowed_domains": ["api.github.com", "httpbin.org"]
    },
    "file_read": {
        "max_file_size": 1048576,  # 1MB
        "allowed_extensions": [".txt", ".md", ".json", ".csv"]
    }
}
```

### Custom Tool Registration

```python
from nijika.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "A custom tool"
    
    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        return {"result": "success"}

# Register custom tool
config = AgentConfig(
    name="agent",
    providers=[...],
    tools=["echo", CustomTool]
)
```

## 📁 Configuration Files

### YAML Configuration

```yaml
# config.yaml
name: "production_agent"
description: "Production AI agent"

providers:
  - name: "openai"
    provider_type: "openai"
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 2000

  - name: "anthropic"
    provider_type: "anthropic"
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-sonnet-20240229"

tools:
  - "echo"
  - "calculator"
  - "http_request"
  - "file_read"

memory:
  backend: "postgresql"
  host: "localhost"
  port: 5432
  database: "nijika"
  username: "nijika_user"
  password: "${DB_PASSWORD}"

rag:
  enabled: true
  chunk_size: 1000
  top_k: 10
  vector_store:
    type: "chroma"
    persist_directory: "./data/chroma"

planning:
  strategy: "hierarchical"
  max_steps: 20
  timeout: 600

workflow:
  max_parallel_steps: 5
  step_timeout: 60
  retry_attempts: 3
```

### JSON Configuration

```json
{
  "name": "production_agent",
  "providers": [
    {
      "name": "openai",
      "provider_type": "openai",
      "api_key": "${OPENAI_API_KEY}",
      "model": "gpt-4",
      "temperature": 0.7
    }
  ],
  "tools": ["echo", "calculator"],
  "memory": {
    "backend": "sqlite",
    "db_path": "agent_memory.db"
  },
  "rag": {
    "enabled": true,
    "chunk_size": 1000
  }
}
```

### Loading Configuration

```python
from nijika import AgentConfig

# From YAML
config = AgentConfig.from_yaml("config.yaml")

# From JSON
config = AgentConfig.from_json("config.json")

# From environment variables
config = AgentConfig.from_env()

# From dictionary
config_dict = {...}
config = AgentConfig.from_dict(config_dict)
```

## 🌍 Environment Variables

### Standard Environment Variables

```bash
# Core settings
NIJIKA_AGENT_NAME=my_agent
NIJIKA_LOG_LEVEL=INFO

# Provider API keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
AZURE_OPENAI_API_KEY=your_azure_key

# Database settings
NIJIKA_DB_HOST=localhost
NIJIKA_DB_PORT=5432
NIJIKA_DB_NAME=nijika
NIJIKA_DB_USER=nijika_user
NIJIKA_DB_PASSWORD=your_password

# RAG settings
NIJIKA_RAG_ENABLED=true
NIJIKA_RAG_CHUNK_SIZE=1000
NIJIKA_RAG_TOP_K=10

# Planning settings
NIJIKA_PLANNING_STRATEGY=hierarchical
NIJIKA_PLANNING_MAX_STEPS=20
```

## 🔒 Security Configuration

### API Key Management

```python
# Use environment variables
config = AgentConfig(
    providers=[
        {
            "name": "openai",
            "provider_type": ProviderType.OPENAI,
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    ]
)

# Use secrets management
from nijika.security import SecretManager

secret_manager = SecretManager("aws")  # or "azure", "gcp"
api_key = secret_manager.get_secret("openai-api-key")
```

### Access Control

```python
security_config = {
    "authentication": {
        "enabled": True,
        "method": "jwt",
        "secret_key": "your-secret-key"
    },
    "authorization": {
        "enabled": True,
        "roles": ["admin", "user", "readonly"]
    },
    "rate_limiting": {
        "enabled": True,
        "requests_per_minute": 100,
        "burst_size": 10
    }
}
```

## 📊 Monitoring Configuration

### Logging Configuration

```python
logging_config = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": [
        {
            "type": "console",
            "level": "INFO"
        },
        {
            "type": "file",
            "level": "DEBUG",
            "filename": "nijika.log",
            "max_size": "10MB",
            "backup_count": 5
        }
    ]
}
```

### Metrics Configuration

```python
metrics_config = {
    "enabled": True,
    "backend": "prometheus",
    "port": 9090,
    "metrics": [
        "request_count",
        "request_duration",
        "error_rate",
        "memory_usage"
    ]
}
```

## 🔧 Validation and Defaults

### Configuration Validation

```python
from nijika import AgentConfig

try:
    config = AgentConfig(
        name="test_agent",
        providers=[...]
    )
    # Configuration is valid
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Default Values

```python
# Default configuration values
DEFAULT_CONFIG = {
    "memory": {
        "backend": "sqlite",
        "db_path": "nijika_memory.db",
        "max_entries": 10000,
        "cleanup_interval": 3600,
        "default_ttl": 86400
    },
    "rag": {
        "enabled": False,
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 5,
        "similarity_threshold": 0.7
    },
    "planning": {
        "strategy": "sequential",
        "max_steps": 10,
        "timeout": 300
    },
    "workflow": {
        "max_parallel_steps": 3,
        "step_timeout": 60,
        "retry_attempts": 2
    }
}
```

## 🎯 Best Practices

### Configuration Management

1. **Use Environment Variables**: Keep sensitive data in environment variables
2. **Validate Configuration**: Always validate configuration before use
3. **Document Settings**: Document all configuration options
4. **Version Control**: Keep configuration files in version control
5. **Environment Separation**: Use different configs for dev/staging/prod

### Performance Optimization

```python
# Optimized configuration for high-performance scenarios
config = AgentConfig(
    name="high_performance_agent",
    providers=[
        {
            "name": "openai",
            "provider_type": ProviderType.OPENAI,
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-3.5-turbo",  # Faster than GPT-4
            "temperature": 0.3,        # Lower for consistency
            "max_tokens": 1000,        # Limit for speed
            "timeout": 15,             # Shorter timeout
            "retry_attempts": 1        # Fewer retries
        }
    ],
    memory_config={
        "backend": "redis",        # Faster than SQLite
        "cleanup_interval": 300,   # More frequent cleanup
        "max_entries": 5000       # Smaller cache
    },
    rag_config={
        "enabled": True,
        "chunk_size": 500,        # Smaller chunks
        "top_k": 3,              # Fewer results
        "similarity_threshold": 0.8  # Higher threshold
    }
)
```

## 🔍 Troubleshooting

### Common Configuration Issues

1. **Missing API Keys**: Ensure all required API keys are set
2. **Invalid Models**: Check that model names are correct
3. **Database Connection**: Verify database connection settings
4. **Memory Issues**: Adjust memory limits for your system
5. **Timeout Settings**: Increase timeouts for slow operations

### Configuration Debugging

```python
# Debug configuration
config = AgentConfig(...)

# Validate configuration
if config.validate():
    print("Configuration is valid")
else:
    print("Configuration errors:", config.errors)

# Print configuration
print(config.to_dict())

# Check specific settings
print(f"Memory backend: {config.memory_config['backend']}")
print(f"RAG enabled: {config.rag_config.get('enabled', False)}")
```

This configuration guide provides comprehensive coverage of all Nijika configuration options. For more specific use cases, check the [API Reference](api/) and [Examples](examples/) sections. 