"""
Configuration management for the Nijika AI Agent Framework
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class ConfigSource(Enum):
    """Configuration source types"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DICT = "dict"
    DEFAULT = "default"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = "nijika.db"
    username: Optional[str] = None
    password: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class SecurityConfig:
    """Security configuration"""
    api_key_encryption: bool = True
    rate_limiting: bool = True
    max_requests_per_minute: int = 100
    allowed_origins: List[str] = field(default_factory=list)
    jwt_secret: Optional[str] = None
    session_timeout: int = 3600  # 1 hour


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    debug: bool = False
    cors_enabled: bool = True
    api_prefix: str = "/api/v1"


class Config:
    """
    Main configuration management class
    """
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger("nijika.config")
        
        # Default configuration
        self._config = self._get_default_config()
        
        # Load configuration from various sources
        if config_path:
            self._load_from_file(config_path)
        elif config_dict:
            self._load_from_dict(config_dict)
        
        # Override with environment variables
        self._load_from_environment()
        
        # Validate configuration
        self._validate()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "framework": {
                "name": "nijika",
                "version": "0.1.0",
                "debug": False,
                "environment": "development"
            },
            "agents": {
                "default_timeout": 300,
                "max_concurrent_executions": 10,
                "auto_cleanup": True,
                "cleanup_interval": 3600
            },
            "providers": {
                "default_provider": "openai",
                "fallback_enabled": True,
                "load_balancing": False,
                "rate_limiting": True,
                "timeout": 30
            },
            "memory": {
                "backend": "sqlite",
                "db_path": "nijika_memory.db",
                "max_entries": 10000,
                "cleanup_interval": 3600,
                "default_ttl": 86400
            },
            "workflows": {
                "engine": "native",
                "max_steps": 50,
                "timeout": 600,
                "parallel_execution": True,
                "save_intermediate_results": True
            },
            "tools": {
                "auto_discovery": True,
                "sandbox_enabled": True,
                "timeout": 30,
                "max_tool_calls": 100
            },
            "rag": {
                "enabled": False,
                "chunk_size": 1000,
                "chunk_overlap": 100,
                "vector_store": "faiss",
                "embedding_model": "text-embedding-ada-002",
                "top_k": 5
            },
            "planning": {
                "strategy": "hierarchical",
                "max_depth": 5,
                "timeout": 60,
                "self_correction": True
            },
            "database": DatabaseConfig(),
            "logging": LoggingConfig(),
            "security": SecurityConfig(),
            "server": ServerConfig()
        }
    
    def _load_from_file(self, config_path: str):
        """Load configuration from file"""
        path = Path(config_path)
        
        if not path.exists():
            self.logger.warning(f"Configuration file not found: {config_path}")
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    file_config = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    file_config = json.load(f)
                else:
                    raise ValueError(f"Unsupported configuration file format: {path.suffix}")
            
            self._merge_config(file_config)
            self.logger.info(f"Configuration loaded from: {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
            raise
    
    def _load_from_dict(self, config_dict: Dict[str, Any]):
        """Load configuration from dictionary"""
        self._merge_config(config_dict)
        self.logger.info("Configuration loaded from dictionary")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            "NIJIKA_DEBUG": ("framework.debug", bool),
            "NIJIKA_ENVIRONMENT": ("framework.environment", str),
            "NIJIKA_DB_PATH": ("memory.db_path", str),
            "NIJIKA_LOG_LEVEL": ("logging.level", str),
            "NIJIKA_SERVER_HOST": ("server.host", str),
            "NIJIKA_SERVER_PORT": ("server.port", int),
            "NIJIKA_API_PREFIX": ("server.api_prefix", str),
            "NIJIKA_CORS_ENABLED": ("server.cors_enabled", bool),
            "NIJIKA_MAX_CONCURRENT_EXECUTIONS": ("agents.max_concurrent_executions", int),
            "NIJIKA_DEFAULT_TIMEOUT": ("agents.default_timeout", int),
            "NIJIKA_RAG_ENABLED": ("rag.enabled", bool),
            "NIJIKA_RAG_CHUNK_SIZE": ("rag.chunk_size", int),
            "NIJIKA_RAG_TOP_K": ("rag.top_k", int),
        }
        
        for env_var, (config_path, value_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Convert value to appropriate type
                    if value_type == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        value = int(value)
                    elif value_type == float:
                        value = float(value)
                    
                    # Set the configuration value
                    self._set_nested_value(config_path, value)
                    self.logger.debug(f"Set {config_path} = {value} from environment")
                    
                except ValueError as e:
                    self.logger.warning(f"Invalid value for {env_var}: {value} - {str(e)}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing configuration"""
        def merge_dicts(base: Dict[str, Any], update: Dict[str, Any]):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value
        
        merge_dicts(self._config, new_config)
    
    def _set_nested_value(self, path: str, value: Any):
        """Set a nested configuration value using dot notation"""
        keys = path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _get_nested_value(self, path: str, default: Any = None):
        """Get a nested configuration value using dot notation"""
        keys = path.split('.')
        current = self._config
        
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        
        return current
    
    def _validate(self):
        """Validate configuration"""
        # Validate required fields
        required_fields = [
            "framework.name",
            "framework.version",
            "memory.backend",
            "logging.level"
        ]
        
        for field in required_fields:
            if self._get_nested_value(field) is None:
                raise ValueError(f"Required configuration field missing: {field}")
        
        # Validate data types and ranges
        if self.get("agents.max_concurrent_executions") <= 0:
            raise ValueError("agents.max_concurrent_executions must be positive")
        
        if self.get("agents.default_timeout") <= 0:
            raise ValueError("agents.default_timeout must be positive")
        
        if self.get("memory.max_entries") <= 0:
            raise ValueError("memory.max_entries must be positive")
        
        # Validate logging level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.get("logging.level") not in valid_log_levels:
            raise ValueError(f"Invalid logging level. Must be one of: {valid_log_levels}")
        
        self.logger.info("Configuration validation passed")
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value by path"""
        return self._get_nested_value(path, default)
    
    def set(self, path: str, value: Any):
        """Set configuration value by path"""
        self._set_nested_value(path, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config.get(section, {})
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration as dataclass"""
        db_config = self.get_section("database")
        return DatabaseConfig(**db_config)
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration as dataclass"""
        logging_config = self.get_section("logging")
        return LoggingConfig(**logging_config)
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration as dataclass"""
        security_config = self.get_section("security")
        return SecurityConfig(**security_config)
    
    def get_server_config(self) -> ServerConfig:
        """Get server configuration as dataclass"""
        server_config = self.get_section("server")
        return ServerConfig(**server_config)
    
    def save_to_file(self, file_path: str, format: str = "yaml"):
        """Save configuration to file"""
        path = Path(file_path)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                if format.lower() == "yaml":
                    yaml.dump(self._config, f, default_flow_style=False, indent=2)
                elif format.lower() == "json":
                    json.dump(self._config, f, indent=2)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Configuration saved to: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {file_path}: {str(e)}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return self._config.copy()
    
    def reload(self):
        """Reload configuration from original source"""
        # This would require storing the original source
        # For now, we'll just note it's not implemented
        raise NotImplementedError("Configuration reload not implemented")
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get("framework.debug", False)
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.get("framework.environment", "development") == "production"
    
    def get_version(self) -> str:
        """Get framework version"""
        return self.get("framework.version", "unknown")
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"Nijika Config (env: {self.get('framework.environment')}, debug: {self.is_debug()})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"Config({self._config})"


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def set_config(config: Config):
    """Set global configuration instance"""
    global _global_config
    _global_config = config


def load_config(config_path: str) -> Config:
    """Load configuration from file and set as global"""
    config = Config(config_path=config_path)
    set_config(config)
    return config


def create_default_config_file(file_path: str = "nijika_config.yaml"):
    """Create a default configuration file"""
    config = Config()
    config.save_to_file(file_path, "yaml")
    return file_path 