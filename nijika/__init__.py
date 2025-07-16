"""
Nijika AI Agent Framework

A dynamic, industry-agnostic AI agent framework designed for seamless integration
across multiple AI providers and models.
"""

from .core.agent import Agent, AgentManager
from .core.providers import ProviderManager
from .core.memory import MemoryManager
from .core.config import Config
from .workflows.engine import WorkflowEngine
from .tools.registry import ToolRegistry
from .rag.system import RAGSystem
from .planning.planner import PlanningEngine

__version__ = "0.1.0"
__author__ = "Nijika Team"
__email__ = "support@nijika.ai"

__all__ = [
    "Agent",
    "AgentManager", 
    "ProviderManager",
    "MemoryManager",
    "Config",
    "WorkflowEngine",
    "ToolRegistry",
    "RAGSystem",
    "PlanningEngine",
] 