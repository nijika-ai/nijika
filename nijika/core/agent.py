"""
Core Agent implementation for the Nijika AI Agent Framework
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime

from .providers import ProviderManager
from .memory import MemoryManager
from .config import Config
from ..workflows.engine import WorkflowEngine
from ..tools.registry import ToolRegistry
from ..rag.system import RAGSystem
from ..planning.planner import PlanningEngine


class AgentState(Enum):
    """Agent lifecycle states"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Configuration for an agent instance"""
    name: str
    providers: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    workflows: List[str] = field(default_factory=list)
    memory_config: Dict[str, Any] = field(default_factory=dict)
    rag_config: Dict[str, Any] = field(default_factory=dict)
    planning_config: Dict[str, Any] = field(default_factory=dict)
    max_iterations: int = 10
    timeout: int = 300
    logging_level: str = "INFO"


class Agent:
    """
    Main Agent class that orchestrates all framework components
    """
    
    def __init__(self, config: Union[AgentConfig, Dict[str, Any]], **kwargs):
        """
        Initialize an agent instance
        
        Args:
            config: Agent configuration
            **kwargs: Additional configuration options
        """
        if isinstance(config, dict):
            config = AgentConfig(**config)
        elif isinstance(config, AgentConfig):
            pass
        else:
            raise ValueError("Config must be AgentConfig instance or dict")
        
        # Merge kwargs into config
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.config = config
        self.id = str(uuid.uuid4())
        self.state = AgentState.INITIALIZED
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Initialize logging
        self.logger = logging.getLogger(f"nijika.agent.{self.config.name}")
        self.logger.setLevel(getattr(logging, self.config.logging_level))
        
        # Initialize core components
        self.provider_manager = ProviderManager(config.providers)
        self.memory_manager = MemoryManager(config.memory_config)
        self.tool_registry = ToolRegistry(config.tools)
        self.workflow_engine = WorkflowEngine()
        self.rag_system = RAGSystem(config.rag_config) if config.rag_config else None
        self.planning_engine = PlanningEngine(config.planning_config)
        
        # Execution context
        self.execution_history = []
        self.current_execution = None
        
        self.logger.info(f"Agent '{self.config.name}' initialized with ID: {self.id}")
    
    async def execute(self, 
                     query: str, 
                     workflow: Optional[str] = None,
                     context: Optional[Dict[str, Any]] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Execute a query using the agent's capabilities
        
        Args:
            query: The input query/task
            workflow: Optional workflow name to use
            context: Additional context for execution
            **kwargs: Additional execution parameters
            
        Returns:
            Execution result
        """
        execution_id = str(uuid.uuid4())
        self.current_execution = execution_id
        self.state = AgentState.RUNNING
        self.last_activity = datetime.now()
        
        try:
            self.logger.info(f"Starting execution {execution_id} for query: {query[:100]}...")
            
            # Prepare execution context
            exec_context = {
                "agent_id": self.id,
                "execution_id": execution_id,
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "context": context or {},
                **kwargs
            }
            
            # Get relevant context from RAG if available
            if self.rag_system:
                rag_context = await self.rag_system.retrieve(query)
                exec_context["rag_context"] = rag_context
            
            # Create execution plan
            plan = await self.planning_engine.create_plan(query, exec_context)
            exec_context["plan"] = plan
            
            # Execute the plan
            result = await self._execute_plan(plan, exec_context)
            
            # Store in memory
            await self.memory_manager.store_execution(execution_id, exec_context, result)
            
            # Add to execution history
            self.execution_history.append({
                "execution_id": execution_id,
                "query": query,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"Execution {execution_id} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Execution {execution_id} failed: {str(e)}")
            self.state = AgentState.ERROR
            raise
        finally:
            self.current_execution = None
            if self.state != AgentState.ERROR:
                self.state = AgentState.INITIALIZED
    
    async def _execute_plan(self, plan, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a generated plan
        
        Args:
            plan: The execution plan (Plan object)
            context: Execution context
            
        Returns:
            Execution result
        """
        results = []
        
        # Handle both Plan objects and dictionaries for backward compatibility
        if hasattr(plan, 'steps'):
            steps = plan.steps
        else:
            steps = plan.get("steps", [])
        
        for step in steps:
            step_result = await self._execute_step(step, context)
            results.append(step_result)
            
            # Update context with step result
            context["previous_steps"] = results
            
            # Check for early termination conditions
            if step_result.get("terminate", False):
                break
        
        return {
            "status": "success",
            "results": results,
            "final_result": results[-1] if results else None,
            "execution_time": (datetime.now() - datetime.fromisoformat(context["timestamp"])).total_seconds()
        }
    
    async def _execute_step(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step in the plan
        
        Args:
            step: Step definition (PlanStep object or dict)
            context: Execution context
            
        Returns:
            Step result
        """
        # Handle both PlanStep objects and dictionaries for backward compatibility
        if hasattr(step, 'type'):
            step_type = step.type
        else:
            step_type = step.get("type")
        
        if step_type == "tool":
            return await self._execute_tool_step(step, context)
        elif step_type == "llm":
            return await self._execute_llm_step(step, context)
        elif step_type == "workflow":
            return await self._execute_workflow_step(step, context)
        elif step_type == "subtask":
            # Handle subtask type by treating it as a tool step
            return await self._execute_tool_step(step, context)
        else:
            raise ValueError(f"Unknown step type: {step_type}")
    
    async def _execute_tool_step(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool-based step"""
        # Handle both PlanStep objects and dictionaries
        if hasattr(step, 'name'):
            # For PlanStep objects, use the name as the tool name
            tool_name = step.name.lower().replace(" ", "_")
            tool_params = getattr(step, 'inputs', {})
        else:
            # For dictionary format
            tool_name = step.get("tool")
            tool_params = step.get("params", {})
        
        # Try to get the tool, fallback to echo for demo purposes
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            # For demo purposes, use echo tool if specific tool not found
            tool = self.tool_registry.get_tool("echo")
            if tool:
                tool_params = {"message": f"Executed step: {getattr(step, 'description', tool_name)}"}
            else:
                raise ValueError(f"Tool '{tool_name}' not found")
        
        result = await tool.execute(tool_params, context)
        
        return {
            "type": "tool",
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_llm_step(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an LLM-based step"""
        # Handle both PlanStep objects and dictionaries
        if hasattr(step, 'name'):
            # For PlanStep objects, create a prompt from the description
            provider = self.config.providers[0] if self.config.providers else "openai"
            prompt = getattr(step, 'description', f"Execute step: {step.name}")
        else:
            # For dictionary format
            provider = step.get("provider") or self.config.providers[0]
            prompt = step.get("prompt")
        
        # Get provider name if it's a config object
        if isinstance(provider, dict):
            provider_name = provider.get("name", "openai")
        else:
            provider_name = provider
        
        llm = self.provider_manager.get_provider(provider_name)
        if not llm:
            # For demo purposes, return a mock result if provider not available
            return {
                "type": "llm",
                "provider": provider_name,
                "result": {"content": f"Mock LLM response for: {prompt}", "provider": provider_name},
                "timestamp": datetime.now().isoformat()
            }
        
        result = await llm.complete(prompt, context)
        
        return {
            "type": "llm",
            "provider": provider_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_workflow_step(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow-based step"""
        # Handle both PlanStep objects and dictionaries
        if hasattr(step, 'name'):
            # For PlanStep objects, use the name as workflow name
            workflow_name = step.name.lower().replace(" ", "_")
            workflow_params = getattr(step, 'inputs', {})
        else:
            # For dictionary format
            workflow_name = step.get("workflow")
            workflow_params = step.get("params", {})
        
        result = await self.workflow_engine.execute_workflow(workflow_name, workflow_params, context)
        
        return {
            "type": "workflow",
            "workflow": workflow_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "id": self.id,
            "name": self.config.name,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "current_execution": self.current_execution,
            "execution_count": len(self.execution_history),
            "providers": self.config.providers,
            "tools": self.config.tools
        }
    
    async def stop(self):
        """Stop the agent"""
        self.state = AgentState.STOPPED
        self.logger.info(f"Agent '{self.config.name}' stopped")
    
    async def pause(self):
        """Pause the agent"""
        self.state = AgentState.PAUSED
        self.logger.info(f"Agent '{self.config.name}' paused")
    
    async def resume(self):
        """Resume the agent"""
        self.state = AgentState.RUNNING
        self.logger.info(f"Agent '{self.config.name}' resumed")


class AgentManager:
    """
    Manager for multiple agent instances
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.logger = logging.getLogger("nijika.agent_manager")
    
    def create_agent(self, config: Union[AgentConfig, Dict[str, Any]], **kwargs) -> Agent:
        """
        Create a new agent instance
        
        Args:
            config: Agent configuration
            **kwargs: Additional configuration options
            
        Returns:
            Created agent instance
        """
        agent = Agent(config, **kwargs)
        self.agents[agent.id] = agent
        
        self.logger.info(f"Created agent '{agent.config.name}' with ID: {agent.id}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        for agent in self.agents.values():
            if agent.config.name == name:
                return agent
        return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        return [agent.get_status() for agent in self.agents.values()]
    
    async def stop_agent(self, agent_id: str):
        """Stop an agent"""
        agent = self.get_agent(agent_id)
        if agent:
            await agent.stop()
            del self.agents[agent_id]
    
    async def stop_all_agents(self):
        """Stop all agents"""
        for agent_id in list(self.agents.keys()):
            await self.stop_agent(agent_id) 