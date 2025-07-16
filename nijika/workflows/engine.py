"""
Workflow execution engine for the Nijika AI Agent Framework
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime
import json


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a workflow"""
    id: str
    name: str
    type: str  # "tool", "llm", "condition", "parallel", "sequential"
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    timeout: int = 300
    retry_count: int = 0
    retry_delay: int = 1
    on_success: Optional[str] = None
    on_failure: Optional[str] = None


@dataclass
class StepResult:
    """Result of a step execution"""
    step_id: str
    status: StepStatus
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
    retry_count: int = 0


@dataclass
class WorkflowExecution:
    """Workflow execution context"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    steps: List[WorkflowStep]
    results: Dict[str, StepResult] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    current_step: Optional[str] = None
    error: Optional[str] = None


class WorkflowEngine:
    """
    Workflow execution engine
    """
    
    def __init__(self):
        self.logger = logging.getLogger("nijika.workflow.engine")
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_handlers: Dict[str, Callable] = {}
        
        # Register default step handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default step handlers"""
        self.step_handlers.update({
            "tool": self._handle_tool_step,
            "llm": self._handle_llm_step,
            "condition": self._handle_condition_step,
            "parallel": self._handle_parallel_step,
            "sequential": self._handle_sequential_step,
            "delay": self._handle_delay_step,
            "transform": self._handle_transform_step
        })
    
    def register_workflow(self, workflow_id: str, workflow_config: Dict[str, Any]):
        """Register a workflow definition"""
        self.workflows[workflow_id] = workflow_config
        self.logger.info(f"Registered workflow: {workflow_id}")
    
    def create_workflow(self, steps: List[Dict[str, Any]], workflow_id: str = None) -> str:
        """Create a workflow from step definitions"""
        workflow_id = workflow_id or str(uuid.uuid4())
        
        workflow_steps = []
        for step_config in steps:
            step = WorkflowStep(
                id=step_config.get("id", str(uuid.uuid4())),
                name=step_config.get("name", step_config.get("id", "unnamed")),
                type=step_config.get("type", "tool"),
                config=step_config.get("config", {}),
                dependencies=step_config.get("dependencies", []),
                conditions=step_config.get("conditions", []),
                timeout=step_config.get("timeout", 300),
                retry_count=step_config.get("retry_count", 0),
                retry_delay=step_config.get("retry_delay", 1),
                on_success=step_config.get("on_success"),
                on_failure=step_config.get("on_failure")
            )
            workflow_steps.append(step)
        
        workflow_config = {
            "id": workflow_id,
            "steps": workflow_steps,
            "created_at": datetime.now().isoformat()
        }
        
        self.register_workflow(workflow_id, workflow_config)
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None, 
                             context: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow_config = self.workflows[workflow_id]
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            steps=workflow_config["steps"],
            context={**(context or {}), **(inputs or {})}
        )
        
        self.executions[execution_id] = execution
        
        try:
            execution.status = WorkflowStatus.RUNNING
            await self._execute_workflow_steps(execution)
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.now()
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.end_time = datetime.now()
            self.logger.error(f"Workflow execution failed: {str(e)}")
            raise
        
        return execution
    
    async def _execute_workflow_steps(self, execution: WorkflowExecution):
        """Execute all steps in a workflow"""
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(execution.steps)
        
        # Execute steps in dependency order
        completed_steps = set()
        
        while len(completed_steps) < len(execution.steps):
            # Find steps that can be executed
            ready_steps = []
            for step in execution.steps:
                if (step.id not in completed_steps and 
                    all(dep in completed_steps for dep in step.dependencies)):
                    ready_steps.append(step)
            
            if not ready_steps:
                raise Exception("Circular dependency detected in workflow")
            
            # Execute ready steps
            tasks = []
            for step in ready_steps:
                task = asyncio.create_task(self._execute_step(step, execution))
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                step = ready_steps[i]
                if isinstance(result, Exception):
                    execution.results[step.id] = StepResult(
                        step_id=step.id,
                        status=StepStatus.FAILED,
                        error=str(result)
                    )
                    if step.retry_count > 0:
                        # Retry logic would go here
                        pass
                    else:
                        raise result
                else:
                    execution.results[step.id] = result
                    completed_steps.add(step.id)
    
    def _build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """Build dependency graph from workflow steps"""
        graph = {}
        for step in steps:
            graph[step.id] = step.dependencies
        return graph
    
    async def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Execute a single workflow step"""
        execution.current_step = step.id
        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Executing step: {step.name} ({step.type})")
            
            # Check conditions
            if step.conditions and not await self._check_conditions(step.conditions, execution):
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.SKIPPED,
                    output=None,
                    timestamp=start_time
                )
            
            # Get step handler
            handler = self.step_handlers.get(step.type)
            if not handler:
                raise ValueError(f"Unknown step type: {step.type}")
            
            # Execute step with timeout
            try:
                output = await asyncio.wait_for(
                    handler(step, execution),
                    timeout=step.timeout
                )
            except asyncio.TimeoutError:
                raise Exception(f"Step {step.name} timed out after {step.timeout} seconds")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = StepResult(
                step_id=step.id,
                status=StepStatus.COMPLETED,
                output=output,
                execution_time=execution_time,
                timestamp=start_time
            )
            
            # Update execution context with step output
            execution.context[f"step_{step.id}_output"] = output
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
                timestamp=start_time
            )
    
    async def _check_conditions(self, conditions: List[str], execution: WorkflowExecution) -> bool:
        """Check if step conditions are met"""
        for condition in conditions:
            # Simple condition evaluation - would need more sophisticated parsing
            if not eval(condition, {}, execution.context):
                return False
        return True
    
    # Step handlers
    async def _handle_tool_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Handle tool execution step"""
        tool_name = step.config.get("tool")
        tool_params = step.config.get("params", {})
        
        if not tool_name:
            raise ValueError("Tool name not specified in step config")
        
        # This would integrate with the actual tool registry
        # For now, return a mock result
        return {
            "tool": tool_name,
            "params": tool_params,
            "result": f"Tool {tool_name} executed successfully"
        }
    
    async def _handle_llm_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Handle LLM execution step"""
        prompt = step.config.get("prompt")
        provider = step.config.get("provider", "openai")
        
        if not prompt:
            raise ValueError("Prompt not specified in step config")
        
        # This would integrate with the actual provider manager
        # For now, return a mock result
        return {
            "provider": provider,
            "prompt": prompt,
            "response": f"LLM response for: {prompt[:50]}..."
        }
    
    async def _handle_condition_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Handle conditional step"""
        condition = step.config.get("condition")
        true_action = step.config.get("true_action")
        false_action = step.config.get("false_action")
        
        if not condition:
            raise ValueError("Condition not specified in step config")
        
        # Evaluate condition
        result = eval(condition, {}, execution.context)
        
        return {
            "condition": condition,
            "result": result,
            "action": true_action if result else false_action
        }
    
    async def _handle_parallel_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Handle parallel execution step"""
        parallel_steps = step.config.get("steps", [])
        
        tasks = []
        for parallel_step_config in parallel_steps:
            parallel_step = WorkflowStep(**parallel_step_config)
            task = asyncio.create_task(self._execute_step(parallel_step, execution))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "parallel_results": results,
            "total_steps": len(parallel_steps)
        }
    
    async def _handle_sequential_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Handle sequential execution step"""
        sequential_steps = step.config.get("steps", [])
        results = []
        
        for step_config in sequential_steps:
            sequential_step = WorkflowStep(**step_config)
            result = await self._execute_step(sequential_step, execution)
            results.append(result)
        
        return {
            "sequential_results": results,
            "total_steps": len(sequential_steps)
        }
    
    async def _handle_delay_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Handle delay step"""
        delay_seconds = step.config.get("delay", 1)
        await asyncio.sleep(delay_seconds)
        
        return {
            "delay_seconds": delay_seconds,
            "message": f"Delayed execution by {delay_seconds} seconds"
        }
    
    async def _handle_transform_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Handle data transformation step"""
        transform_type = step.config.get("type", "identity")
        input_data = step.config.get("input", execution.context)
        
        if transform_type == "json":
            return json.dumps(input_data)
        elif transform_type == "filter":
            filter_key = step.config.get("filter_key")
            return {k: v for k, v in input_data.items() if k == filter_key}
        else:
            return input_data
    
    # Management methods
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution by ID"""
        return self.executions.get(execution_id)
    
    def list_workflows(self) -> List[str]:
        """List all registered workflows"""
        return list(self.workflows.keys())
    
    def list_executions(self) -> List[str]:
        """List all workflow executions"""
        return list(self.executions.keys())
    
    def get_workflow_config(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow configuration"""
        return self.workflows.get(workflow_id)
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a workflow execution"""
        execution = self.executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.now()
            return True
        return False
    
    def register_step_handler(self, step_type: str, handler: Callable):
        """Register a custom step handler"""
        self.step_handlers[step_type] = handler
        self.logger.info(f"Registered step handler for type: {step_type}")
    
    def remove_workflow(self, workflow_id: str) -> bool:
        """Remove a workflow definition"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            self.logger.info(f"Removed workflow: {workflow_id}")
            return True
        return False
    
    def cleanup_executions(self, max_age_hours: int = 24):
        """Clean up old workflow executions"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        to_remove = []
        
        for execution_id, execution in self.executions.items():
            if execution.start_time.timestamp() < cutoff_time:
                to_remove.append(execution_id)
        
        for execution_id in to_remove:
            del self.executions[execution_id]
        
        self.logger.info(f"Cleaned up {len(to_remove)} old executions") 