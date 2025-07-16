"""
Tool registry and management for the Nijika AI Agent Framework
"""

import asyncio
import logging
import inspect
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import importlib
import json
from datetime import datetime


class ToolType(Enum):
    """Types of tools"""
    UTILITY = "utility"
    API = "api"
    DATABASE = "database"
    FILE = "file"
    COMPUTATION = "computation"
    COMMUNICATION = "communication"
    CUSTOM = "custom"


@dataclass
class ToolParameter:
    """Tool parameter definition"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    validation: Optional[str] = None


@dataclass
class ToolMetadata:
    """Tool metadata"""
    name: str
    description: str
    version: str
    author: str
    tool_type: ToolType
    parameters: List[ToolParameter] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    requires_auth: bool = False
    sandbox_safe: bool = True
    timeout: int = 30


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"nijika.tool.{self.__class__.__name__}")
        self.execution_count = 0
        self.last_executed = None
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata"""
        pass
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        """Execute the tool"""
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate tool parameters"""
        metadata = self.get_metadata()
        
        for param in metadata.parameters:
            if param.required and param.name not in params:
                raise ValueError(f"Required parameter '{param.name}' missing")
            
            if param.name in params:
                value = params[param.name]
                # Basic type validation
                if param.type == "string" and not isinstance(value, str):
                    raise ValueError(f"Parameter '{param.name}' must be a string")
                elif param.type == "integer" and not isinstance(value, int):
                    raise ValueError(f"Parameter '{param.name}' must be an integer")
                elif param.type == "float" and not isinstance(value, (int, float)):
                    raise ValueError(f"Parameter '{param.name}' must be a number")
                elif param.type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Parameter '{param.name}' must be a boolean")
        
        return True
    
    async def pre_execute(self, params: Dict[str, Any], context: Dict[str, Any] = None):
        """Pre-execution hook"""
        self.validate_parameters(params)
    
    async def post_execute(self, result: Any, params: Dict[str, Any], context: Dict[str, Any] = None):
        """Post-execution hook"""
        self.execution_count += 1
        self.last_executed = datetime.now()


# Built-in tools
class EchoTool(BaseTool):
    """Simple echo tool for testing"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="echo",
            description="Echo back the input message",
            version="1.0.0",
            author="Nijika Team",
            tool_type=ToolType.UTILITY,
            parameters=[
                ToolParameter("message", "string", "Message to echo back")
            ],
            tags=["utility", "test"],
            sandbox_safe=True
        )
    
    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        await self.pre_execute(params, context)
        result = {"echo": params["message"]}
        await self.post_execute(result, params, context)
        return result


class HttpRequestTool(BaseTool):
    """HTTP request tool"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="http_request",
            description="Make HTTP requests to external APIs",
            version="1.0.0",
            author="Nijika Team",
            tool_type=ToolType.API,
            parameters=[
                ToolParameter("url", "string", "URL to request"),
                ToolParameter("method", "string", "HTTP method", default="GET"),
                ToolParameter("headers", "object", "HTTP headers", required=False),
                ToolParameter("data", "object", "Request body data", required=False)
            ],
            tags=["http", "api", "request"],
            sandbox_safe=False
        )
    
    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        await self.pre_execute(params, context)
        
        try:
            import aiohttp
            
            url = params["url"]
            method = params.get("method", "GET")
            headers = params.get("headers", {})
            data = params.get("data")
            
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, json=data) as response:
                    result = {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "data": await response.text()
                    }
                    
                    if response.headers.get("content-type", "").startswith("application/json"):
                        try:
                            result["json"] = await response.json()
                        except:
                            pass
            
            await self.post_execute(result, params, context)
            return result
            
        except Exception as e:
            error_result = {"error": str(e)}
            await self.post_execute(error_result, params, context)
            return error_result


class FileReadTool(BaseTool):
    """File reading tool"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file_read",
            description="Read content from a file",
            version="1.0.0",
            author="Nijika Team",
            tool_type=ToolType.FILE,
            parameters=[
                ToolParameter("file_path", "string", "Path to the file to read"),
                ToolParameter("encoding", "string", "File encoding", default="utf-8")
            ],
            tags=["file", "read", "io"],
            sandbox_safe=False
        )
    
    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        await self.pre_execute(params, context)
        
        try:
            file_path = params["file_path"]
            encoding = params.get("encoding", "utf-8")
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            result = {
                "file_path": file_path,
                "content": content,
                "size": len(content)
            }
            
            await self.post_execute(result, params, context)
            return result
            
        except Exception as e:
            error_result = {"error": str(e)}
            await self.post_execute(error_result, params, context)
            return error_result


class CalculatorTool(BaseTool):
    """Simple calculator tool"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="calculator",
            description="Perform basic mathematical calculations",
            version="1.0.0",
            author="Nijika Team",
            tool_type=ToolType.COMPUTATION,
            parameters=[
                ToolParameter("expression", "string", "Mathematical expression to evaluate")
            ],
            tags=["math", "calculation", "utility"],
            sandbox_safe=True
        )
    
    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        await self.pre_execute(params, context)
        
        try:
            expression = params["expression"]
            
            # Basic safety check - only allow basic math operations
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Expression contains invalid characters")
            
            result_value = eval(expression)
            
            result = {
                "expression": expression,
                "result": result_value
            }
            
            await self.post_execute(result, params, context)
            return result
            
        except Exception as e:
            error_result = {"error": str(e)}
            await self.post_execute(error_result, params, context)
            return error_result


class ToolRegistry:
    """
    Tool registry for managing and discovering tools
    """
    
    def __init__(self, tool_names: List[str] = None):
        self.tools: Dict[str, BaseTool] = {}
        self.tool_classes: Dict[str, Type[BaseTool]] = {}
        self.logger = logging.getLogger("nijika.tool.registry")
        
        # Register built-in tools
        self._register_builtin_tools()
        
        # Register specified tools
        if tool_names:
            for tool_name in tool_names:
                try:
                    self.register_tool_by_name(tool_name)
                except Exception as e:
                    self.logger.warning(f"Failed to register tool '{tool_name}': {str(e)}")
    
    def _register_builtin_tools(self):
        """Register built-in tools"""
        builtin_tools = [
            EchoTool,
            HttpRequestTool,
            FileReadTool,
            CalculatorTool
        ]
        
        for tool_class in builtin_tools:
            self.register_tool_class(tool_class)
    
    def register_tool_class(self, tool_class: Type[BaseTool], config: Dict[str, Any] = None):
        """Register a tool class"""
        if not issubclass(tool_class, BaseTool):
            raise ValueError("Tool class must inherit from BaseTool")
        
        tool_instance = tool_class(config)
        metadata = tool_instance.get_metadata()
        
        self.tool_classes[metadata.name] = tool_class
        self.tools[metadata.name] = tool_instance
        
        self.logger.info(f"Registered tool: {metadata.name}")
    
    def register_tool_by_name(self, tool_name: str, config: Dict[str, Any] = None):
        """Register a tool by name (for built-in tools)"""
        if tool_name in self.tools:
            return
        
        # Map common tool names to classes
        tool_mapping = {
            "echo": EchoTool,
            "http_request": HttpRequestTool,
            "file_read": FileReadTool,
            "calculator": CalculatorTool,
            "email": None,  # Would be implemented
            "database": None,  # Would be implemented
            "knowledge_base": None,  # Would be implemented
        }
        
        tool_class = tool_mapping.get(tool_name)
        if tool_class:
            self.register_tool_class(tool_class, config)
        else:
            self.logger.warning(f"Unknown tool: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self.tools.keys())
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool"""
        tool = self.get_tool(tool_name)
        if tool:
            return tool.get_metadata()
        return None
    
    def search_tools(self, query: str = None, tool_type: ToolType = None, 
                    tags: List[str] = None) -> List[ToolMetadata]:
        """Search for tools"""
        results = []
        
        for tool in self.tools.values():
            metadata = tool.get_metadata()
            
            # Filter by type
            if tool_type and metadata.tool_type != tool_type:
                continue
            
            # Filter by tags
            if tags and not any(tag in metadata.tags for tag in tags):
                continue
            
            # Filter by query
            if query:
                query_lower = query.lower()
                if (query_lower not in metadata.name.lower() and 
                    query_lower not in metadata.description.lower()):
                    continue
            
            results.append(metadata)
        
        return results
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any], 
                          context: Dict[str, Any] = None) -> Any:
        """Execute a tool"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        try:
            result = await tool.execute(params, context)
            return result
        except Exception as e:
            self.logger.error(f"Tool execution failed ({tool_name}): {str(e)}")
            raise
    
    def validate_tool_params(self, tool_name: str, params: Dict[str, Any]) -> bool:
        """Validate parameters for a tool"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        return tool.validate_parameters(params)
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get JSON schema for a tool"""
        metadata = self.get_tool_metadata(tool_name)
        if not metadata:
            return None
        
        properties = {}
        required = []
        
        for param in metadata.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            
            if param.default is not None:
                properties[param.name]["default"] = param.default
            
            if param.required:
                required.append(param.name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "description": metadata.description
        }
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            if tool_name in self.tool_classes:
                del self.tool_classes[tool_name]
            self.logger.info(f"Unregistered tool: {tool_name}")
            return True
        return False
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        stats = {
            "total_tools": len(self.tools),
            "tool_types": {},
            "tool_execution_counts": {}
        }
        
        for tool_name, tool in self.tools.items():
            metadata = tool.get_metadata()
            tool_type = metadata.tool_type.value
            
            if tool_type not in stats["tool_types"]:
                stats["tool_types"][tool_type] = 0
            stats["tool_types"][tool_type] += 1
            
            stats["tool_execution_counts"][tool_name] = tool.execution_count
        
        return stats
    
    def discover_tools(self, module_path: str):
        """Discover tools from a module"""
        try:
            module = importlib.import_module(module_path)
            
            for name in dir(module):
                obj = getattr(module, name)
                
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseTool) and 
                    obj != BaseTool):
                    self.register_tool_class(obj)
                    
        except Exception as e:
            self.logger.error(f"Failed to discover tools from {module_path}: {str(e)}")
    
    def export_tools_catalog(self) -> Dict[str, Any]:
        """Export tools catalog as JSON"""
        catalog = {
            "tools": [],
            "total_count": len(self.tools),
            "generated_at": datetime.now().isoformat()
        }
        
        for tool_name, tool in self.tools.items():
            metadata = tool.get_metadata()
            catalog["tools"].append({
                "name": metadata.name,
                "description": metadata.description,
                "version": metadata.version,
                "author": metadata.author,
                "type": metadata.tool_type.value,
                "parameters": [
                    {
                        "name": param.name,
                        "type": param.type,
                        "description": param.description,
                        "required": param.required,
                        "default": param.default
                    }
                    for param in metadata.parameters
                ],
                "tags": metadata.tags,
                "requires_auth": metadata.requires_auth,
                "sandbox_safe": metadata.sandbox_safe,
                "timeout": metadata.timeout
            })
        
        return catalog 