#!/usr/bin/env python3
"""
Simple example demonstrating the Nijika AI Agent Framework

This example shows how to:
1. Create and configure an agent
2. Set up providers and tools
3. Create a workflow
4. Execute tasks
5. Use RAG system
"""

import asyncio
import logging
from nijika import Agent, WorkflowEngine, RAGSystem, PlanningEngine
from nijika.core.providers import ProviderConfig, ProviderType
from nijika.core.agent import AgentConfig
from nijika.tools.registry import ToolRegistry


async def main():
    """Main example function"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("nijika.example")
    
    logger.info("🚀 Nijika AI Agent Framework - Simple Example")
    logger.info("=" * 50)
    
    # 1. Create an agent configuration
    logger.info("\n1. Creating Agent Configuration...")
    agent_config = AgentConfig(
        name="demo_agent",
        providers=[
            {
                "name": "openai",
                "provider_type": ProviderType.OPENAI,
                "api_key": "sk-svcacct-bClcaltsEV3owFsBOb9qT3BlbkFJ0txPNVMpb1a51l6idnI8",
                "model": "gpt-3.5-turbo"
            }
        ],
        tools=["echo", "calculator", "http_request"],
        memory_config={
            "backend": "sqlite",
            "db_path": "demo_memory.db"
        },
        rag_config={
            "enabled": True,
            "chunk_size": 1000,
            "top_k": 5
        }
    )
    
    # 2. Create the agent
    logger.info("\n2. Creating Agent...")
    agent = Agent(agent_config)
    logger.info(f"   ✓ Agent '{agent.config.name}' created with ID: {agent.id}")
    
    # 3. Add some documents to the RAG system
    logger.info("\n3. Setting up RAG System...")
    if agent.rag_system:
        # Add some sample documents
        await agent.rag_system.add_text(
            "Nijika is a powerful AI agent framework designed for multi-provider integration.",
            metadata={"source": "documentation", "topic": "introduction"}
        )
        
        await agent.rag_system.add_text(
            "The framework supports workflow management, tool integration, and RAG capabilities.",
            metadata={"source": "documentation", "topic": "features"}
        )
        
        await agent.rag_system.add_text(
            "Agents can use multiple AI providers like OpenAI, Anthropic, and Google.",
            metadata={"source": "documentation", "topic": "providers"}
        )
        
        logger.info(f"   ✓ Added {len(agent.rag_system.list_documents())} documents to RAG system")
    
    # 4. Create a simple workflow
    logger.info("\n4. Creating Workflow...")
    workflow_engine = WorkflowEngine()
    
    # Define workflow steps
    workflow_steps = [
        {
            "id": "greeting",
            "name": "Greeting",
            "type": "tool",
            "config": {
                "tool": "echo",
                "params": {"message": "Hello from Nijika!"}
            }
        },
        {
            "id": "calculation",
            "name": "Simple Calculation",
            "type": "tool",
            "config": {
                "tool": "calculator", 
                "params": {"expression": "2 + 2 * 3"}
            },
            "dependencies": ["greeting"]
        },
        {
            "id": "completion",
            "name": "Task Completion",
            "type": "tool",
            "config": {
                "tool": "echo",
                "params": {"message": "Workflow completed successfully!"}
            },
            "dependencies": ["calculation"]
        }
    ]
    
    workflow_id = workflow_engine.create_workflow(workflow_steps, "demo_workflow")
    logger.info(f"   ✓ Created workflow with ID: {workflow_id}")
    
    # 5. Execute some tasks
    logger.info("\n5. Executing Tasks...")
    
    # Simple query
    logger.info("\n   a) Simple Query:")
    try:
        result = await agent.execute("What is the Nijika framework?")
        logger.info(f"      Status: {result.get('status')}")
        logger.info(f"      Steps executed: {len(result.get('results', []))}")
    except Exception as e:
        logger.info(f"      Error: {e}")
    
    # Calculator task
    logger.info("\n   b) Calculator Task:")
    try:
        result = await agent.execute("Calculate the value of 15 * 7 + 3")
        logger.info(f"      Status: {result.get('status')}")
        logger.info(f"      Final result: {result.get('final_result')}")
    except Exception as e:
        logger.info(f"      Error: {e}")
    
    # Workflow execution
    logger.info("\n   c) Workflow Execution:")
    try:
        execution = await workflow_engine.execute_workflow(workflow_id)
        logger.info(f"      Workflow Status: {execution.status.value}")
        logger.info(f"      Steps completed: {len(execution.results)}")
        for step_id, result in execution.results.items():
            logger.info(f"        {step_id}: {result.status.value}")
    except Exception as e:
        logger.info(f"      Error: {e}")
    
    # 6. Test RAG retrieval
    logger.info("\n6. Testing RAG Retrieval...")
    if agent.rag_system:
        try:
            retrieval_result = await agent.rag_system.retrieve("What providers does Nijika support?")
            logger.info(f"   ✓ Retrieved {len(retrieval_result.documents)} documents")
            logger.info(f"   ✓ Retrieval time: {retrieval_result.retrieval_time:.3f}s")
            
            if retrieval_result.documents:
                logger.info(f"   ✓ Top result: {retrieval_result.documents[0].content[:100]}...")
        except Exception as e:
            logger.info(f"   Error: {e}")
    
    # 7. Test planning
    logger.info("\n7. Testing Planning System...")
    try:
        plan = await agent.planning_engine.create_plan(
            "Create a customer support response system",
            {"domain": "e-commerce", "priority": "high"}
        )
        logger.info(f"   ✓ Created plan with {len(plan.steps)} steps")
        logger.info(f"   ✓ Estimated duration: {plan.estimated_duration} seconds")
        logger.info(f"   ✓ Strategy: {plan.strategy.value}")
        
        # Show plan steps
        for i, step in enumerate(plan.steps[:3]):  # Show first 3 steps
            logger.info(f"      Step {i+1}: {step.name} - {step.description}")
        
        if len(plan.steps) > 3:
            logger.info(f"      ... and {len(plan.steps) - 3} more steps")
            
    except Exception as e:
        logger.info(f"   Error: {e}")
    
    # 8. Show agent statistics
    logger.info("\n8. Agent Statistics:")
    status = agent.get_status()
    logger.info(f"   ✓ Agent State: {status['state']}")
    logger.info(f"   ✓ Executions: {status['execution_count']}")
    logger.info(f"   ✓ Providers: {len(status['providers'])}")
    logger.info(f"   ✓ Tools: {len(status['tools'])}")
    
    # Memory statistics
    memory_stats = agent.memory_manager.get_stats()
    logger.info(f"   ✓ Memory Backend: {memory_stats['backend_type']}")
    
    # RAG statistics
    if agent.rag_system:
        rag_stats = agent.rag_system.get_stats()
        logger.info(f"   ✓ RAG Documents: {rag_stats['total_documents']}")
    
    # Planning statistics
    planning_stats = agent.planning_engine.get_stats()
    logger.info(f"   ✓ Plans Created: {planning_stats['total_plans']}")
    
    logger.info("\n" + "=" * 50)
    logger.info("✅ Demo completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Add your actual AI provider API keys")
    logger.info("2. Explore more complex workflows")
    logger.info("3. Add custom tools and integrations")
    logger.info("4. Build industry-specific applications")


if __name__ == "__main__":
    asyncio.run(main()) 