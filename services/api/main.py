"""
FastAPI backend for AI Trip Agent.
Provides REST API for trip planning with LangGraph agents.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import get_settings
from config.llm_adapter import LLMAdapter
from services.rag.embeddings import EmbeddingManager
from services.rag.vector_store import VectorStoreManager
from services.carbon import CarbonCalculator
from agents import create_agent_graph
from agents.realtime_agent import agent_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
settings = get_settings()
llm_adapter = None
embedding_manager = None
vector_store_manager = None
carbon_calculator = None
agent_graph = None
# agent_manager is imported as a global singleton

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global llm_adapter, embedding_manager, vector_store_manager, carbon_calculator, agent_graph

    logger.info("Starting AI Trip Agent API...")

    # Configure LangSmith if enabled
    if settings.langsmith_tracing and settings.langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        logger.info(f"LangSmith tracing enabled for project: {settings.langsmith_project}")

    try:
        # Initialize components
        logger.info("Initializing LLM adapter...")
        llm_adapter = LLMAdapter(settings)
        llm = llm_adapter.get_llm()

        logger.info("Initializing embedding manager...")
        embedding_manager = EmbeddingManager(settings)

        logger.info("Initializing vector store...")
        vector_store_manager = VectorStoreManager(settings, embedding_manager)

        logger.info("Initializing carbon calculator...")
        carbon_calculator = CarbonCalculator(settings.carbon_default_emission_factor)

        logger.info("Creating agent graph...")
        agent_graph = create_agent_graph(llm, vector_store_manager, carbon_calculator)

        logger.info("✅ AI Trip Agent API started successfully")

        yield

    except Exception as e:
        logger.error(f"Failed to start API: {e}", exc_info=True)
        raise

    finally:
        logger.info("Shutting down AI Trip Agent API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered travel planning assistant for Assam with carbon footprint tracking",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class TripRequest(BaseModel):
    """Trip planning request with enhanced options."""
    query: str = Field(..., description="User's trip planning query")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    transport_mode: Optional[str] = Field("car_petrol", description="Preferred transport mode (can be 'mixed')")
    persona: Optional[str] = Field("solo", description="Travel persona (student, family, heritage, etc.)")
    stoppage_duration: Optional[str] = Field("none", description="Maximum stoppage duration")
    enable_realtime_agent: bool = Field(False, description="Enable real-time trip monitoring agent")

    # Date and time fields
    travel_date: Optional[str] = Field(None, description="Departure date (YYYY-MM-DD)")
    travel_time: Optional[str] = Field(None, description="Departure time (HH:MM:SS)")
    is_round_trip: bool = Field(False, description="Whether it's a round trip")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD)")
    return_time: Optional[str] = Field(None, description="Return time (HH:MM:SS)")


class TripResponse(BaseModel):
    """Trip planning response with agent info."""
    success: bool
    session_id: str
    destination: Optional[str] = None
    duration_days: Optional[int] = None
    itinerary: Optional[dict] = None
    carbon_emissions: Optional[dict] = None
    green_alternatives: Optional[list] = None
    messages: list[str] = []
    error: Optional[str] = None
    timestamp: str
    agent_id: Optional[str] = None  # Real-time monitoring agent ID


class AgentStatusResponse(BaseModel):
    """Real-time agent status response."""
    agent_id: str
    status: str
    created_at: str
    last_check: str
    updates: list[dict]
    trip_details: dict


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    llm_provider: str
    chroma_connected: bool
    timestamp: str


# API Routes
@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "AI Trip Agent API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check ChromaDB connection
        chroma_connected = False
        try:
            vector_store_manager.get_client().heartbeat()
            chroma_connected = True
        except Exception as e:
            logger.warning(f"ChromaDB health check failed: {e}")
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            llm_provider=settings.llm_provider.value,
            chroma_connected=chroma_connected,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    """
    Plan a trip based on user query with enhanced options.

    This endpoint orchestrates multiple AI agents to:
    1. Understand user requirements
    2. Retrieve relevant local knowledge
    3. Generate detailed itinerary
    4. Calculate carbon footprint
    5. Suggest green alternatives

    Additionally, this endpoint and the application support LangSmith (LangChain) tracing when enabled.
    The application configures tracing during startup using environment variables derived from settings.
    Example of the configuration used elsewhere in this project (kept here for reference):

        # Configure LangSmith if enabled
        if settings.langsmith_tracing and settings.langsmith_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
            # Prefer an explicit endpoint if provided, otherwise use the LangSmith default
            os.environ["LANGCHAIN_ENDPOINT"] = getattr(settings, "langsmith_endpoint", "https://api.smith.langchain.com")
            logger.info(f"LangSmith tracing enabled for project: {settings.langsmith_project}")

        # Also ensure env vars are consistently set
        if settings.langsmith_api_key:
            os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        if settings.langsmith_project:
            os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        if settings.langsmith_tracing:
            os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langsmith_tracing).lower()
    6. Optionally start real-time monitoring agent
    """
    try:
        logger.info(f"Received trip planning request: {request.query[:100]}...")

        # Generate session ID if not provided
        session_id = request.session_id or f"session_{datetime.utcnow().timestamp()}"

        # Prepare initial state with enhanced options
        initial_state = {
            "user_query": request.query,
            "messages": [],
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "transport_mode": request.transport_mode,
            "persona": request.persona,
            "stoppage_duration": request.stoppage_duration,
            "enable_realtime_agent": request.enable_realtime_agent,
            "travel_date": request.travel_date,
            "travel_time": request.travel_time,
            "is_round_trip": request.is_round_trip,
            "return_date": request.return_date,
            "return_time": request.return_time,
            "retrieved_docs": [],
            "interests": [],
            "green_alternatives": [],
            "recommendations": [],
            "should_continue": True,
            "agent_updates": [],
        }

        # Run agent graph
        logger.info("Invoking agent graph...")
        final_state = agent_graph.invoke(initial_state)

        # Extract messages
        messages = []
        for msg in final_state.get("messages", []):
            if hasattr(msg, "content"):
                messages.append(msg.content)

        # Create real-time monitoring agent if requested
        agent_id = None
        if request.enable_realtime_agent:
            trip_details = {
                "destination": final_state.get("destination"),
                "duration_days": final_state.get("duration_days"),
                "transport_mode": request.transport_mode,
                "persona": request.persona,
                "query": request.query
            }
            agent_id = agent_manager.create_agent(trip_details)
            logger.info(f"Created real-time monitoring agent: {agent_id}")

        # Build response
        response = TripResponse(
            success=not bool(final_state.get("error")),
            session_id=session_id,
            destination=final_state.get("destination"),
            duration_days=final_state.get("duration_days"),
            itinerary=final_state.get("itinerary"),
            carbon_emissions=final_state.get("carbon_emissions"),
            green_alternatives=final_state.get("green_alternatives", []),
            messages=messages,
            error=final_state.get("error"),
            timestamp=datetime.utcnow().isoformat(),
            agent_id=agent_id
        )

        logger.info(f"Trip planning completed successfully for session: {session_id}")

        return response

    except Exception as e:
        logger.error(f"Trip planning failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vector-store/stats")
async def get_vector_store_stats():
    """Get vector store statistics."""
    try:
        stats = vector_store_manager.get_collection_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Failed to get vector store stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str):
    """
    Get status of a real-time monitoring agent.

    Returns current status, updates, and trip details.
    """
    try:
        status = agent_manager.get_agent_status(agent_id)

        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])

        return AgentStatusResponse(**status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """
    Stop a real-time monitoring agent.

    The agent will stop monitoring and no longer provide updates.
    """
    try:
        success = agent_manager.stop_agent(agent_id)

        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")

        return {
            "success": True,
            "message": f"Agent {agent_id} stopped successfully",
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/{agent_id}/action")
async def agent_action(agent_id: str, action_request: dict):
    """
    Send an action command to a monitoring agent.

    Supported actions:
    - replan: Replan the trip
    - delayed: Report a delay
    - check_weather: Check current weather
    - check_news: Get latest news
    - security_check: Perform security check
    """
    try:
        action = action_request.get("action")
        details = action_request.get("details")

        if not action:
            raise HTTPException(status_code=400, detail="Action is required")

        agent = agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Handle the action
        result = agent.handle_action(action, details)

        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "success": True,
            "agent_id": agent_id,
            "action": action,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute agent action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """
    List all active monitoring agents.

    Returns a list of all agents with their current status.
    """
    try:
        agents = agent_manager.get_all_agents()
        return {
            "agents": agents,
            "count": len(agents),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/cleanup")
async def cleanup_agents(max_age_hours: int = 24):
    """
    Clean up old monitoring agents.

    Removes agents older than specified hours (default: 24).
    """
    try:
        removed_count = agent_manager.cleanup_old_agents(max_age_hours)
        return {
            "success": True,
            "removed_count": removed_count,
            "message": f"Cleaned up {removed_count} old agents",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to cleanup agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/carbon/stats")
async def get_carbon_stats():
    """
    Get cumulative carbon footprint statistics.

    Returns total carbon emissions, trip count, and recent trips.
    """
    try:
        from services.carbon.tracker import carbon_tracker
        stats = carbon_tracker.get_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get carbon stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/carbon/reset")
async def reset_carbon_tracking():
    """
    Reset cumulative carbon footprint tracking.

    Clears all tracked carbon emissions and trip history.
    """
    try:
        from services.carbon.tracker import carbon_tracker
        carbon_tracker.reset()
        return {
            "success": True,
            "message": "Carbon tracking data has been reset",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to reset carbon tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
