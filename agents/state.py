from typing import Annotated, List, Optional, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Shared state for all agents in the trip planning workflow.

    This state is passed between agents and updated as the workflow progresses.
    """

    # Conversation messages
    messages: Annotated[List[BaseMessage], add_messages]

    # User query and intent
    user_query: str
    intent: Optional[str]  # e.g., "plan_trip", "get_weather", "calculate_carbon"

    # Trip planning details
    destination: Optional[str]
    duration_days: Optional[int]
    budget: Optional[float]
    traveler_type: Optional[str]  # e.g., "student", "family", "solo", "couple"
    interests: List[str]  # e.g., ["wildlife", "culture", "adventure"]

    # Enhanced user preferences
    persona: Optional[str]  # student, family, heritage, corporate, green, solo, religious, spiritual, adventure, luxury
    stoppage_duration: Optional[str]  # none, 3_hours, 6_hours, 12_hours_plus

    # Travel date and time
    travel_date: Optional[str]  # Departure date
    travel_time: Optional[str]  # Departure time
    is_round_trip: bool  # Whether it's a round trip
    return_date: Optional[str]  # Return date (if round trip)
    return_time: Optional[str]  # Return time (if round trip)

    # Retrieved knowledge
    retrieved_docs: List[Dict[str, Any]]
    local_knowledge: Optional[str]

    # Weather information
    weather_info: Optional[Dict[str, Any]]

    # Transportation and carbon
    transport_mode: Optional[str]  # Can be "mixed" for best combination
    distance_km: Optional[float]
    carbon_emissions: Optional[Dict[str, Any]]
    green_alternatives: List[Dict[str, Any]]

    # Generated itinerary
    itinerary: Optional[Dict[str, Any]]
    timeline: List[Dict[str, Any]]  # Timeline with time slots, activities, and images
    budget_breakdown: Optional[Dict[str, Any]]  # Detailed budget breakdown
    final_response: Optional[str]

    # Session management
    session_id: Optional[str]
    cumulative_carbon_footprint: Optional[float]  # Total carbon footprint across all trips

    # Real-time agent management
    enable_realtime_agent: bool
    agent_id: Optional[str]
    agent_status: Optional[str]
    agent_updates: List[Dict[str, Any]]
