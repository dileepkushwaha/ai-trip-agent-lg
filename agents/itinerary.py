"""
Itinerary Agent - Generates detailed trip itineraries.
"""

import logging
import json
from typing import Dict, Any
from datetime import datetime, timedelta

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser

from agents.state import AgentState

logger = logging.getLogger(__name__)


class ItineraryAgent:
    """Agent responsible for generating trip itineraries."""

    def __init__(self, llm: BaseChatModel):
        """Initialize itinerary agent with LLM."""
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert travel itinerary planner for Assam, India.

Create a detailed, day-by-day itinerary based on:
- Destination: {destination}
- Duration: {duration_days} days
- Budget: {budget}
- Traveler type: {traveler_type}
- Interests: {interests}

Use the following local knowledge to make your recommendations accurate and specific:
{local_knowledge}

You MUST respond with a valid JSON object with the following structure:
{{
  "timeline": [
    {{
      "day": 1,
      "date": "2024-01-15",
      "activities": [
        {{
          "time": "09:00 AM",
          "activity": "Visit Kamakhya Temple",
          "location": "Kamakhya Temple, Guwahati",
          "duration": "2 hours",
          "description": "Ancient Hindu temple dedicated to Goddess Kamakhya",
          "image_url": "https://example.com/kamakhya.jpg",
          "cost": 500
        }}
      ]
    }}
  ],
  "budget_breakdown": {{
    "accommodation": 5000,
    "food": 3000,
    "transportation": 2000,
    "activities": 4000,
    "miscellaneous": 1000,
    "total": 15000
  }},
  "summary": "A brief summary of the trip"
}}

Include realistic image URLs (use placeholder URLs like https://images.unsplash.com/photo-XXXXX or https://via.placeholder.com/400x300?text=LocationName).
Ensure all costs are in INR and realistic for Assam tourism.
Create a practical itinerary with specific timings, locations, and activities."""),
            ("human", "Create an itinerary for my trip.")
        ])

        self.json_parser = JsonOutputParser()

    def _generate_timeline_and_budget(self, state: AgentState) -> tuple:
        """Generate structured timeline and budget breakdown."""
        destination = state.get("destination", "Assam")
        duration_days = state.get("duration_days", 3)
        budget = state.get("budget")
        traveler_type = state.get("traveler_type", "general")
        interests = state.get("interests", [])
        local_knowledge = state.get("local_knowledge", "")

        budget_str = f"₹{budget:,.0f}" if budget else "₹15,000"
        interests_str = ", ".join(interests) if interests else "General sightseeing"

        max_knowledge_length = 3000
        if len(local_knowledge) > max_knowledge_length:
            local_knowledge = local_knowledge[:max_knowledge_length] + "..."

        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "destination": destination,
                "duration_days": duration_days,
                "budget": budget_str,
                "traveler_type": traveler_type,
                "interests": interests_str,
                "local_knowledge": local_knowledge or "Use general knowledge about Assam."
            })

            content = response.content
            if isinstance(content, str):
                if content.strip().startswith("```json"):
                    content = content.strip()[7:]
                if content.strip().endswith("```"):
                    content = content.strip()[:-3]
                content = content.strip()

                parsed_data = json.loads(content)
            else:
                parsed_data = content

            timeline = parsed_data.get("timeline", [])
            budget_breakdown = parsed_data.get("budget_breakdown", {})
            summary = parsed_data.get("summary", "")

            return timeline, budget_breakdown, summary

        except Exception as e:
            logger.warning(f"Failed to parse structured response: {e}. Using fallback.")
            return self._generate_fallback_timeline_and_budget(state)

    def _generate_fallback_timeline_and_budget(self, state: AgentState) -> tuple:
        """Generate fallback timeline and budget if LLM parsing fails."""
        duration_days = state.get("duration_days", 3)
        budget = state.get("budget", 15000)
        destination = state.get("destination", "Assam")

        timeline = []
        for day in range(1, duration_days + 1):
            timeline.append({
                "day": day,
                "date": (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
                "activities": [
                    {
                        "time": "09:00 AM",
                        "activity": f"Morning exploration in {destination}",
                        "location": destination,
                        "duration": "3 hours",
                        "description": "Explore local attractions",
                        "image_url": f"https://via.placeholder.com/400x300?text=Day+{day}+Morning",
                        "cost": 1000
                    },
                    {
                        "time": "02:00 PM",
                        "activity": f"Afternoon activities in {destination}",
                        "location": destination,
                        "duration": "3 hours",
                        "description": "Visit cultural sites",
                        "image_url": f"https://via.placeholder.com/400x300?text=Day+{day}+Afternoon",
                        "cost": 1500
                    }
                ]
            })

        budget_breakdown = {
            "accommodation": budget * 0.35,
            "food": budget * 0.25,
            "transportation": budget * 0.20,
            "activities": budget * 0.15,
            "miscellaneous": budget * 0.05,
            "total": budget
        }

        summary = f"A {duration_days}-day trip to {destination} with various activities."

        return timeline, budget_breakdown, summary

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Generate trip itinerary based on requirements and knowledge.

        Args:
            state: Current agent state

        Returns:
            Updated state with generated itinerary
        """
        try:
            destination = state.get("destination", "Assam")
            duration_days = state.get("duration_days", 3)
            budget = state.get("budget")
            traveler_type = state.get("traveler_type", "general")
            interests = state.get("interests", [])

            logger.info(f"Generating itinerary for {duration_days}-day trip to {destination}")

            timeline, budget_breakdown, summary = self._generate_timeline_and_budget(state)

            itinerary_text = f"# {destination} Trip Itinerary\n\n{summary}\n\n"
            itinerary_text += f"**Duration:** {duration_days} days\n"
            itinerary_text += f"**Total Budget:** ₹{budget_breakdown.get('total', budget):,.0f}\n\n"

            for day_info in timeline:
                itinerary_text += f"\n## Day {day_info['day']} - {day_info.get('date', '')}\n"
                for activity in day_info.get('activities', []):
                    itinerary_text += f"\n**{activity['time']}** - {activity['activity']}\n"
                    itinerary_text += f"- Location: {activity['location']}\n"
                    itinerary_text += f"- Duration: {activity['duration']}\n"
                    itinerary_text += f"- Cost: ₹{activity['cost']}\n"
                    itinerary_text += f"- {activity['description']}\n"

            itinerary_text += f"\n## Budget Breakdown\n"
            itinerary_text += f"- Accommodation: ₹{budget_breakdown.get('accommodation', 0):,.0f}\n"
            itinerary_text += f"- Food: ₹{budget_breakdown.get('food', 0):,.0f}\n"
            itinerary_text += f"- Transportation: ₹{budget_breakdown.get('transportation', 0):,.0f}\n"
            itinerary_text += f"- Activities: ₹{budget_breakdown.get('activities', 0):,.0f}\n"
            itinerary_text += f"- Miscellaneous: ₹{budget_breakdown.get('miscellaneous', 0):,.0f}\n"
            itinerary_text += f"- **Total: ₹{budget_breakdown.get('total', 0):,.0f}**\n"

            itinerary = {
                "destination": destination,
                "duration_days": duration_days,
                "budget": budget,
                "traveler_type": traveler_type,
                "interests": interests,
                "full_itinerary": itinerary_text,
                "generated": True
            }

            logger.info("Successfully generated itinerary with timeline and budget")

            return {
                "itinerary": itinerary,
                "timeline": timeline,
                "budget_breakdown": budget_breakdown,
                "messages": [AIMessage(content=itinerary_text)],
                "next_agent": "carbon",
                "should_continue": True,
            }

        except Exception as e:
            logger.error(f"Itinerary agent error: {e}", exc_info=True)
            return {
                "error": f"Failed to generate itinerary: {str(e)}",
                "next_agent": "carbon",
                "should_continue": True,
            }
