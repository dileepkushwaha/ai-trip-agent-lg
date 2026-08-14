"""
LangGraph workflow for AI Trip Agent.
Orchestrates multiple agents for trip planning.
"""

import logging
from typing import Literal

from langgraph.graph import StateGraph, END
from langchain_core.language_models.chat_models import BaseChatModel

from agents.state import AgentState
from agents.planner import PlannerAgent
from agents.knowledge import KnowledgeAgent
from agents.itinerary import ItineraryAgent
from agents.carbon import CarbonAgent
from services.rag.vector_store import VectorStoreManager
from services.carbon import CarbonCalculator

logger = logging.getLogger(__name__)


def create_agent_graph(
    llm: BaseChatModel,
    vector_store_manager: VectorStoreManager,
    carbon_calculator: CarbonCalculator
):
    """
    Create the LangGraph workflow for trip planning.
    
    Args:
        llm: Language model instance
        vector_store_manager: Vector store for RAG
        carbon_calculator: Carbon footprint calculator
        
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Creating agent graph...")
    
    # Initialize agents
    planner = PlannerAgent(llm)
    knowledge = KnowledgeAgent(vector_store_manager)
    itinerary_agent = ItineraryAgent(llm)
    carbon = CarbonAgent(carbon_calculator)
    
    # Create workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes (renamed to avoid conflict with state keys)
    workflow.add_node("planner", planner)
    workflow.add_node("knowledge", knowledge)
    workflow.add_node("itinerary_generator", itinerary_agent)
    workflow.add_node("carbon", carbon)
    
    # Define routing logic
    def route_after_planner(state: AgentState) -> Literal["knowledge", END]:
        """Route after planner based on intent and errors."""
        if state.get("error") or not state.get("should_continue", True):
            return END
        
        intent = state.get("intent", "plan_trip")
        if intent in ["plan_trip", "explore", "recommend"]:
            return "knowledge"
        
        return END
    
    def route_after_knowledge(state: AgentState) -> Literal["itinerary_generator", END]:
        """Route after knowledge retrieval."""
        if state.get("error") or not state.get("should_continue", True):
            return END
        
        # Check if we have retrieved documents
        if state.get("retrieved_docs"):
            return "itinerary_generator"
        
        return END
    
    def route_after_itinerary(state: AgentState) -> Literal["carbon", END]:
        """Route after itinerary generation."""
        if state.get("error") or not state.get("should_continue", True):
            return END
        
        # If itinerary was generated, calculate carbon
        if state.get("itinerary"):
            return "carbon"
        
        return END
    
    def route_after_carbon(state: AgentState) -> Literal[END]:
        """Route after carbon calculation (always end)."""
        return END
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "knowledge": "knowledge",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "knowledge",
        route_after_knowledge,
        {
            "itinerary_generator": "itinerary_generator",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "itinerary_generator",
        route_after_itinerary,
        {
            "carbon": "carbon",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "carbon",
        route_after_carbon,
        {
            END: END
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("✅ Agent graph created successfully")
    return app
