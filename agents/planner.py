"""
Planner Agent - Orchestrates trip planning and extracts user requirements.
"""

import logging
import re
from typing import Dict, Any, Optional

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

from agents.state import AgentState

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Agent responsible for understanding user intent and planning trips."""
    
    def __init__(self, llm: BaseChatModel):
        """Initialize planner agent with LLM."""
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert travel planner for Assam, India.
Your role is to understand the user's travel requirements and extract key information.

Extract the following from the user's query:
1. Destination (specific place in Assam)
2. Duration (number of days)
3. Budget (if mentioned)
4. Traveler type (student, family, solo, couple, group)
5. Interests (wildlife, culture, adventure, food, nature, etc.)
6. Persona (student, family, heritage, corporate, green, solo, religious, spiritual, adventure, luxury)
7. Transport preferences (car, bus, train, mixed, etc.)
8. Stoppage preferences (none, short, medium, long)

Consider the persona when making recommendations:
- Student: Budget-friendly, educational, social
- Family: Kid-friendly, safe, comfortable
- Heritage: Cultural sites, historical places
- Corporate: Efficient, professional, time-conscious
- Green: Sustainable, eco-friendly, low-carbon
- Solo: Flexible, independent, adventurous
- Religious: Spiritual sites, temples, peaceful
- Spiritual: Meditation, yoga, tranquil
- Adventure: Thrilling, outdoor, active
- Luxury: Premium, exclusive, comfortable

If information is missing, make reasonable assumptions based on context and persona.

Respond in a structured format:
DESTINATION: <place>
DURATION: <days>
BUDGET: <amount or "flexible">
TRAVELER_TYPE: <type>
INTERESTS: <comma-separated list>
INTENT: <plan_trip|get_info|calculate_carbon>

Then provide a brief, friendly acknowledgment of their request that reflects their persona."""),
            ("human", "{query}\n\nPersona: {persona}\nTransport: {transport_mode}\nStoppage: {stoppage_duration}")
        ])

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Process user query and extract trip planning details.

        Args:
            state: Current agent state

        Returns:
            Updated state with extracted information
        """
        try:
            user_query = state.get("user_query", "")
            persona = state.get("persona", "solo")
            transport_mode = state.get("transport_mode", "car_petrol")
            stoppage_duration = state.get("stoppage_duration", "none")

            if not user_query:
                logger.warning("Empty user query received")
                return {
                    "error": "No query provided",
                    "should_continue": False
                }

            logger.info(f"Planning trip for query: {user_query[:100]}...")
            logger.info(f"Persona: {persona}, Transport: {transport_mode}, Stoppage: {stoppage_duration}")

            # Invoke LLM to extract information
            chain = self.prompt | self.llm
            response = chain.invoke({
                "query": user_query,
                "persona": persona,
                "transport_mode": transport_mode,
                "stoppage_duration": stoppage_duration
            })

            # Parse response
            response_text = response.content
            
            # Extract structured information
            destination = self._extract_field(response_text, "DESTINATION")
            duration_str = self._extract_field(response_text, "DURATION")
            budget_str = self._extract_field(response_text, "BUDGET")
            traveler_type = self._extract_field(response_text, "TRAVELER_TYPE")
            interests_str = self._extract_field(response_text, "INTERESTS")
            intent = self._extract_field(response_text, "INTENT")
            
            # Parse duration
            duration_days = self._parse_duration(duration_str)
            
            # Parse budget
            budget = self._parse_budget(budget_str)
            
            # Parse interests
            interests = [i.strip() for i in interests_str.split(",")] if interests_str else []
            
            # Extract acknowledgment (text after structured fields)
            acknowledgment = self._extract_acknowledgment(response_text)
            
            logger.info(f"Extracted: destination={destination}, duration={duration_days}, intent={intent}")
            
            return {
                "messages": [AIMessage(content=acknowledgment)],
                "destination": destination or "Assam",
                "duration_days": duration_days or 3,
                "budget": budget,
                "traveler_type": traveler_type or "general",
                "interests": interests,
                "intent": intent or "plan_trip",
                "next_agent": "knowledge",
                "should_continue": True,
            }
            
        except Exception as e:
            logger.error(f"Planner agent error: {e}", exc_info=True)
            return {
                "error": f"Planning failed: {str(e)}",
                "should_continue": False
            }
    
    @staticmethod
    def _extract_field(text: str, field_name: str) -> str:
        """Extract a field value from structured response."""
        pattern = rf"{field_name}:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """Parse duration string to number of days."""
        if not duration_str:
            return 3
        
        # Extract number from string
        match = re.search(r"(\d+)", duration_str)
        if match:
            return int(match.group(1))
        
        return 3
    
    @staticmethod
    def _parse_budget(budget_str: str) -> Optional[float]:
        """Parse budget string to float."""
        if not budget_str or "flexible" in budget_str.lower():
            return None
        
        # Extract number from string
        match = re.search(r"(\d+(?:,\d+)*(?:\.\d+)?)", budget_str.replace(",", ""))
        if match:
            return float(match.group(1))
        
        return None
    
    @staticmethod
    def _extract_acknowledgment(text: str) -> str:
        """Extract acknowledgment text after structured fields."""
        # Find the last structured field
        last_field_match = re.search(r"INTENT:.*?(?:\n|$)", text, re.IGNORECASE)
        
        if last_field_match:
            # Get text after the last field
            acknowledgment = text[last_field_match.end():].strip()
            if acknowledgment:
                return acknowledgment
        
        # Fallback: return a generic message
        return "I'll help you plan your trip to Assam!"
