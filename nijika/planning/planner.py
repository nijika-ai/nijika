"""
Planning and reasoning engine for the Nijika AI Agent Framework
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import re


class PlanningStrategy(Enum):
    """Planning strategies"""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
    PARALLEL = "parallel"
    REACTIVE = "reactive"
    GOAL_ORIENTED = "goal_oriented"


@dataclass
class PlanStep:
    """A single step in a plan"""
    id: str
    type: str  # "tool", "llm", "condition", "subtask"
    name: str
    description: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    priority: int = 1
    estimated_duration: int = 30
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Plan:
    """A complete execution plan"""
    id: str
    goal: str
    strategy: PlanningStrategy
    steps: List[PlanStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    estimated_duration: int = 0
    success_criteria: List[str] = field(default_factory=list)
    fallback_plans: List[str] = field(default_factory=list)


class PlanningEngine:
    """
    Main planning engine for task decomposition and execution planning
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("nijika.planning")
        
        # Configuration
        self.strategy = PlanningStrategy(self.config.get("strategy", "hierarchical"))
        self.max_depth = self.config.get("max_depth", 5)
        self.timeout = self.config.get("timeout", 60)
        self.self_correction = self.config.get("self_correction", True)
        
        # Plan storage
        self.plans: Dict[str, Plan] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
        
        # Initialize built-in templates
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize built-in plan templates"""
        self.templates.update({
            "data_analysis": {
                "goal": "Analyze data and generate insights",
                "steps": [
                    {"type": "tool", "name": "data_loading", "description": "Load data from source"},
                    {"type": "tool", "name": "data_cleaning", "description": "Clean and preprocess data"},
                    {"type": "tool", "name": "data_analysis", "description": "Perform statistical analysis"},
                    {"type": "llm", "name": "insight_generation", "description": "Generate insights from analysis"},
                    {"type": "tool", "name": "report_generation", "description": "Generate final report"}
                ]
            },
            "customer_support": {
                "goal": "Handle customer inquiry",
                "steps": [
                    {"type": "llm", "name": "intent_classification", "description": "Classify customer intent"},
                    {"type": "condition", "name": "route_decision", "description": "Route to appropriate handler"},
                    {"type": "tool", "name": "knowledge_search", "description": "Search knowledge base"},
                    {"type": "llm", "name": "response_generation", "description": "Generate response"},
                    {"type": "tool", "name": "follow_up", "description": "Schedule follow-up if needed"}
                ]
            },
            "content_creation": {
                "goal": "Create content based on requirements",
                "steps": [
                    {"type": "llm", "name": "requirement_analysis", "description": "Analyze content requirements"},
                    {"type": "tool", "name": "research", "description": "Research relevant information"},
                    {"type": "llm", "name": "outline_creation", "description": "Create content outline"},
                    {"type": "llm", "name": "content_generation", "description": "Generate content"},
                    {"type": "tool", "name": "quality_check", "description": "Check content quality"}
                ]
            }
        })
    
    async def create_plan(self, goal: str, context: Dict[str, Any] = None, 
                         strategy: PlanningStrategy = None) -> Plan:
        """Create a plan for achieving a goal"""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        strategy = strategy or self.strategy
        context = context or {}
        
        plan = Plan(
            id=plan_id,
            goal=goal,
            strategy=strategy,
            metadata=context
        )
        
        try:
            # Generate plan steps based on strategy
            if strategy == PlanningStrategy.SEQUENTIAL:
                steps = await self._plan_sequential(goal, context)
            elif strategy == PlanningStrategy.HIERARCHICAL:
                steps = await self._plan_hierarchical(goal, context)
            elif strategy == PlanningStrategy.PARALLEL:
                steps = await self._plan_parallel(goal, context)
            elif strategy == PlanningStrategy.REACTIVE:
                steps = await self._plan_reactive(goal, context)
            elif strategy == PlanningStrategy.GOAL_ORIENTED:
                steps = await self._plan_goal_oriented(goal, context)
            else:
                steps = await self._plan_sequential(goal, context)
            
            plan.steps = steps
            plan.estimated_duration = sum(step.estimated_duration for step in steps)
            plan.success_criteria = self._generate_success_criteria(goal, steps)
            
            # Store plan
            self.plans[plan_id] = plan
            
            self.logger.info(f"Created plan '{plan_id}' with {len(steps)} steps")
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create plan: {str(e)}")
            raise
    
    async def _plan_sequential(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Create a sequential plan"""
        steps = []
        
        # Try to match against templates
        template = self._find_template(goal)
        if template:
            for i, step_config in enumerate(template["steps"]):
                step = PlanStep(
                    id=f"step_{i+1}",
                    type=step_config["type"],
                    name=step_config["name"],
                    description=step_config["description"],
                    dependencies=[f"step_{i}"] if i > 0 else []
                )
                steps.append(step)
        else:
            # Generate steps using LLM-based decomposition
            steps = await self._decompose_task(goal, context)
        
        return steps
    
    async def _plan_hierarchical(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Create a hierarchical plan"""
        steps = []
        
        # Break down goal into high-level tasks
        high_level_tasks = await self._identify_high_level_tasks(goal, context)
        
        for i, task in enumerate(high_level_tasks):
            # Create main step
            main_step = PlanStep(
                id=f"main_{i+1}",
                type="subtask",
                name=task["name"],
                description=task["description"],
                priority=task.get("priority", 1)
            )
            steps.append(main_step)
            
            # Create sub-steps
            sub_steps = await self._decompose_task(task["description"], context)
            for j, sub_step in enumerate(sub_steps):
                sub_step.id = f"sub_{i+1}_{j+1}"
                sub_step.dependencies.append(main_step.id)
                steps.append(sub_step)
        
        return steps
    
    async def _plan_parallel(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Create a parallel plan"""
        steps = []
        
        # Identify independent tasks
        independent_tasks = await self._identify_independent_tasks(goal, context)
        
        for i, task in enumerate(independent_tasks):
            step = PlanStep(
                id=f"parallel_{i+1}",
                type=task["type"],
                name=task["name"],
                description=task["description"],
                dependencies=[]  # No dependencies for parallel execution
            )
            steps.append(step)
        
        # Add a final aggregation step
        final_step = PlanStep(
            id="final_aggregation",
            type="llm",
            name="Aggregate Results",
            description="Aggregate results from parallel tasks",
            dependencies=[step.id for step in steps]
        )
        steps.append(final_step)
        
        return steps
    
    async def _plan_reactive(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Create a reactive plan"""
        steps = []
        
        # Create initial assessment step
        assessment_step = PlanStep(
            id="assessment",
            type="llm",
            name="Assess Situation",
            description="Assess the current situation and determine next actions",
            conditions=[]
        )
        steps.append(assessment_step)
        
        # Create conditional response steps
        response_conditions = await self._identify_response_conditions(goal, context)
        
        for i, condition in enumerate(response_conditions):
            step = PlanStep(
                id=f"response_{i+1}",
                type="condition",
                name=condition["name"],
                description=condition["description"],
                conditions=[condition["condition"]],
                dependencies=["assessment"]
            )
            steps.append(step)
        
        return steps
    
    async def _plan_goal_oriented(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Create a goal-oriented plan"""
        steps = []
        
        # Define success criteria
        success_criteria = await self._analyze_goal_requirements(goal, context)
        
        # Work backwards from goal
        for i, criterion in enumerate(success_criteria):
            step = PlanStep(
                id=f"goal_{i+1}",
                type="tool",
                name=criterion["name"],
                description=criterion["description"],
                outputs={"success_metric": criterion["metric"]}
            )
            steps.append(step)
        
        # Add dependencies based on logical order
        for i in range(1, len(steps)):
            steps[i].dependencies = [steps[i-1].id]
        
        return steps
    
    async def _decompose_task(self, task: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Decompose a task into steps using LLM-based analysis"""
        # This would use an actual LLM for task decomposition
        # For now, return a simple decomposition
        
        common_steps = [
            {"type": "tool", "name": "gather_information", "description": "Gather relevant information"},
            {"type": "llm", "name": "analyze_requirements", "description": "Analyze task requirements"},
            {"type": "tool", "name": "execute_action", "description": "Execute the main action"},
            {"type": "llm", "name": "validate_results", "description": "Validate the results"},
            {"type": "tool", "name": "finalize", "description": "Finalize the task"}
        ]
        
        steps = []
        for i, step_config in enumerate(common_steps):
            step = PlanStep(
                id=f"step_{i+1}",
                type=step_config["type"],
                name=step_config["name"],
                description=step_config["description"],
                dependencies=[f"step_{i}"] if i > 0 else []
            )
            steps.append(step)
        
        return steps
    
    async def _identify_high_level_tasks(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify high-level tasks for hierarchical planning"""
        # This would use LLM analysis
        # For now, return generic high-level tasks
        
        if "analysis" in goal.lower():
            return [
                {"name": "data_preparation", "description": "Prepare data for analysis", "priority": 1},
                {"name": "analysis_execution", "description": "Execute the analysis", "priority": 2},
                {"name": "results_interpretation", "description": "Interpret the results", "priority": 3}
            ]
        elif "support" in goal.lower():
            return [
                {"name": "issue_identification", "description": "Identify the customer issue", "priority": 1},
                {"name": "solution_research", "description": "Research potential solutions", "priority": 2},
                {"name": "response_delivery", "description": "Deliver the response", "priority": 3}
            ]
        else:
            return [
                {"name": "planning", "description": "Plan the task execution", "priority": 1},
                {"name": "execution", "description": "Execute the main task", "priority": 2},
                {"name": "validation", "description": "Validate the results", "priority": 3}
            ]
    
    async def _identify_independent_tasks(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify independent tasks for parallel planning"""
        # This would use sophisticated analysis
        # For now, return some parallel tasks
        
        return [
            {"type": "tool", "name": "data_collection", "description": "Collect required data"},
            {"type": "tool", "name": "environment_setup", "description": "Set up environment"},
            {"type": "tool", "name": "resource_allocation", "description": "Allocate resources"},
            {"type": "llm", "name": "requirement_analysis", "description": "Analyze requirements"}
        ]
    
    async def _identify_response_conditions(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify response conditions for reactive planning"""
        return [
            {
                "name": "success_response",
                "description": "Handle successful completion",
                "condition": "status == 'success'"
            },
            {
                "name": "error_response",
                "description": "Handle error conditions",
                "condition": "status == 'error'"
            },
            {
                "name": "timeout_response",
                "description": "Handle timeout conditions",
                "condition": "status == 'timeout'"
            }
        ]
    
    async def _analyze_goal_requirements(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze goal requirements for goal-oriented planning"""
        return [
            {"name": "requirement_1", "description": "Meet first requirement", "metric": "completion_rate"},
            {"name": "requirement_2", "description": "Meet second requirement", "metric": "accuracy_score"},
            {"name": "requirement_3", "description": "Meet third requirement", "metric": "user_satisfaction"}
        ]
    
    def _find_template(self, goal: str) -> Optional[Dict[str, Any]]:
        """Find a suitable template for the goal"""
        goal_lower = goal.lower()
        
        for template_name, template_config in self.templates.items():
            if template_name.replace("_", " ") in goal_lower:
                return template_config
        
        return None
    
    def _generate_success_criteria(self, goal: str, steps: List[PlanStep]) -> List[str]:
        """Generate success criteria for the plan"""
        criteria = []
        
        # Basic criteria
        criteria.append("All steps completed successfully")
        criteria.append("No critical errors occurred")
        
        # Goal-specific criteria
        if "analysis" in goal.lower():
            criteria.append("Analysis results are accurate and meaningful")
        elif "support" in goal.lower():
            criteria.append("Customer issue resolved satisfactorily")
        elif "create" in goal.lower():
            criteria.append("Created output meets requirements")
        
        return criteria
    
    async def optimize_plan(self, plan_id: str) -> Plan:
        """Optimize an existing plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        # Analyze plan for optimization opportunities
        optimizations = await self._analyze_plan_optimizations(plan)
        
        # Apply optimizations
        for optimization in optimizations:
            await self._apply_optimization(plan, optimization)
        
        # Update estimated duration
        plan.estimated_duration = sum(step.estimated_duration for step in plan.steps)
        
        self.logger.info(f"Optimized plan '{plan_id}' with {len(optimizations)} optimizations")
        return plan
    
    async def _analyze_plan_optimizations(self, plan: Plan) -> List[Dict[str, Any]]:
        """Analyze plan for optimization opportunities"""
        optimizations = []
        
        # Check for parallelizable steps
        for i, step in enumerate(plan.steps):
            if not step.dependencies:
                for j, other_step in enumerate(plan.steps[i+1:], i+1):
                    if not other_step.dependencies:
                        optimizations.append({
                            "type": "parallelize",
                            "steps": [step.id, other_step.id]
                        })
        
        # Check for redundant steps
        step_names = [step.name for step in plan.steps]
        for i, name in enumerate(step_names):
            if step_names.count(name) > 1:
                optimizations.append({
                    "type": "merge_redundant",
                    "step_name": name
                })
        
        return optimizations
    
    async def _apply_optimization(self, plan: Plan, optimization: Dict[str, Any]):
        """Apply an optimization to the plan"""
        if optimization["type"] == "parallelize":
            # Remove dependencies to allow parallel execution
            for step_id in optimization["steps"]:
                step = next((s for s in plan.steps if s.id == step_id), None)
                if step:
                    step.dependencies = []
        
        elif optimization["type"] == "merge_redundant":
            # Merge redundant steps
            step_name = optimization["step_name"]
            redundant_steps = [s for s in plan.steps if s.name == step_name]
            
            if len(redundant_steps) > 1:
                # Keep the first one, remove others
                for step in redundant_steps[1:]:
                    plan.steps.remove(step)
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID"""
        return self.plans.get(plan_id)
    
    def list_plans(self) -> List[str]:
        """List all plan IDs"""
        return list(self.plans.keys())
    
    def remove_plan(self, plan_id: str) -> bool:
        """Remove a plan"""
        if plan_id in self.plans:
            del self.plans[plan_id]
            return True
        return False
    
    def add_template(self, name: str, template: Dict[str, Any]):
        """Add a custom plan template"""
        self.templates[name] = template
        self.logger.info(f"Added plan template: {name}")
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a plan template"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all template names"""
        return list(self.templates.keys())
    
    async def validate_plan(self, plan: Plan) -> Dict[str, Any]:
        """Validate a plan for consistency and feasibility"""
        validation_result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check for circular dependencies
        if self._has_circular_dependencies(plan.steps):
            validation_result["valid"] = False
            validation_result["issues"].append("Circular dependencies detected")
        
        # Check for missing dependencies
        step_ids = {step.id for step in plan.steps}
        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    validation_result["valid"] = False
                    validation_result["issues"].append(f"Missing dependency: {dep}")
        
        # Check for orphaned steps
        referenced_steps = set()
        for step in plan.steps:
            referenced_steps.update(step.dependencies)
        
        for step in plan.steps:
            if step.id not in referenced_steps and step.dependencies:
                validation_result["warnings"].append(f"Potentially orphaned step: {step.id}")
        
        return validation_result
    
    def _has_circular_dependencies(self, steps: List[PlanStep]) -> bool:
        """Check if there are circular dependencies in the plan"""
        # Create adjacency list
        graph = {}
        for step in steps:
            graph[step.id] = step.dependencies
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in graph:
            if step_id not in visited:
                if has_cycle(step_id):
                    return True
        
        return False
    
    def export_plan(self, plan_id: str, format: str = "json") -> str:
        """Export a plan to various formats"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        if format == "json":
            return json.dumps({
                "id": plan.id,
                "goal": plan.goal,
                "strategy": plan.strategy.value,
                "steps": [
                    {
                        "id": step.id,
                        "type": step.type,
                        "name": step.name,
                        "description": step.description,
                        "dependencies": step.dependencies,
                        "estimated_duration": step.estimated_duration
                    }
                    for step in plan.steps
                ],
                "metadata": plan.metadata,
                "created_at": plan.created_at.isoformat(),
                "estimated_duration": plan.estimated_duration
            }, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get planning engine statistics"""
        return {
            "total_plans": len(self.plans),
            "total_templates": len(self.templates),
            "strategies_used": list(set(plan.strategy.value for plan in self.plans.values())),
            "average_steps_per_plan": sum(len(plan.steps) for plan in self.plans.values()) / len(self.plans) if self.plans else 0,
            "average_estimated_duration": sum(plan.estimated_duration for plan in self.plans.values()) / len(self.plans) if self.plans else 0
        } 