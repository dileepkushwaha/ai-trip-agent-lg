"""
Carbon Agent - Calculates carbon footprint and suggests green alternatives.
"""

import logging
from typing import Dict, Any

from langchain_core.messages import AIMessage

from agents.state import AgentState
from services.carbon import CarbonCalculator, TransportMode
from services.carbon.tracker import carbon_tracker

logger = logging.getLogger(__name__)


DISTANCE_ESTIMATES = {
    "guwahati": {"delhi": 1800, "mumbai": 2600, "kolkata": 1000, "bangalore": 2800},
    "kaziranga": {"guwahati": 220, "delhi": 2000, "mumbai": 2800, "kolkata": 1200},
    "shillong": {"guwahati": 100, "delhi": 1900, "mumbai": 2700, "kolkata": 1100},
    "tezpur": {"guwahati": 180, "delhi": 1950, "mumbai": 2750, "kolkata": 1150},
    "majuli": {"guwahati": 300, "delhi": 2100, "mumbai": 2900, "kolkata": 1300},
}


class CarbonAgent:
    """Agent responsible for carbon footprint calculation."""

    def __init__(self, carbon_calculator: CarbonCalculator):
        """Initialize carbon agent with calculator."""
        self.calculator = carbon_calculator

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Calculate carbon footprint and suggest alternatives.

        Args:
            state: Current agent state

        Returns:
            Updated state with carbon calculations
        """
        try:
            destination = state.get("destination", "").lower()
            transport_mode_str = state.get("transport_mode", "car_petrol")

            logger.info(f"Calculating carbon footprint for trip to {destination}")

            distance_km = self._estimate_distance(destination)

            try:
                transport_mode = TransportMode(transport_mode_str)
            except ValueError:
                logger.warning(f"Unknown transport mode: {transport_mode_str}, using car_petrol")
                transport_mode = TransportMode.CAR_PETROL

            result = self.calculator.calculate(
                distance_km=distance_km,
                transport_mode=transport_mode
            )

            alternatives = self.calculator.get_green_alternatives(
                distance_km=distance_km,
                current_mode=transport_mode,
                max_alternatives=3
            )

            carbon_info = {
                "distance_km": result.distance_km,
                "transport_mode": result.transport_mode.value,
                "emissions_kg": round(result.total_emissions_kg, 2),
                "emissions_tonnes": round(result.total_emissions_tonnes, 4),
                "equivalent_trees": round(result.equivalent_trees, 1),
                "emission_factor": result.emission_factor,
            }

            green_alternatives = []
            for mode, alt_result, savings_pct in alternatives:
                green_alternatives.append({
                    "mode": mode.value,
                    "emissions_kg": round(alt_result.total_emissions_kg, 2),
                    "savings_percentage": round(savings_pct, 1),
                    "description": alt_result.description
                })

            carbon_tracker.add_trip(
                carbon_kg=result.total_emissions_kg,
                trip_details={
                    "destination": destination,
                    "distance_km": distance_km,
                    "transport_mode": transport_mode.value
                }
            )

            cumulative_carbon = carbon_tracker.get_total_carbon()

            message = self._format_carbon_message(result, alternatives, cumulative_carbon)

            logger.info(
                f"Carbon calculation complete: {result.total_emissions_kg:.2f} kg CO2e "
                f"for {distance_km} km. Cumulative: {cumulative_carbon:.2f} kg"
            )

            return {
                "distance_km": distance_km,
                "carbon_emissions": carbon_info,
                "green_alternatives": green_alternatives,
                "cumulative_carbon_footprint": cumulative_carbon,
                "messages": [AIMessage(content=message)],
                "next_agent": None,
                "should_continue": False,
            }

        except Exception as e:
            logger.error(f"Carbon agent error: {e}", exc_info=True)
            return {
                "error": f"Carbon calculation failed: {str(e)}",
                "next_agent": None,
                "should_continue": False,
            }

    @staticmethod
    def _estimate_distance(destination: str) -> float:
        """
        Estimate travel distance to destination.

        In production, this should use actual route planning APIs.
        """
        destination = destination.lower()

        for place, distances in DISTANCE_ESTIMATES.items():
            if place in destination:
                return distances.get("guwahati", 200)

        return 200

    @staticmethod
    def _format_carbon_message(result, alternatives, cumulative_carbon: float) -> str:
        """Format carbon information into user-friendly message."""
        message_parts = [
            f"\n🌱 **Carbon Footprint Analysis**",
            f"*Based on **GHG Protocol** and **SBTi** standards*",
            f"",
            f"📍 Distance: {result.distance_km:.0f} km",
            f"🚗 Transport: {result.transport_mode.value.replace('_', ' ').title()}",
            f"💨 Emissions: {result.total_emissions_kg:.2f} kg CO2e",
            f"🌳 Tree equivalent: {result.equivalent_trees:.1f} trees needed to offset for 1 year",
            f"",
            f"📊 **Cumulative Carbon Footprint**: {cumulative_carbon:.2f} kg CO2e",
        ]

        if alternatives:
            message_parts.append("\n♻️ **Greener Alternatives:**")
            for mode, alt_result, savings_pct in alternatives:
                message_parts.append(
                    f"  • {mode.value.replace('_', ' ').title()}: "
                    f"{alt_result.total_emissions_kg:.2f} kg CO2e "
                    f"(Save {savings_pct:.0f}%)"
                )

        message_parts.append(
            "\n💡 Consider using public transport or carpooling to reduce your carbon footprint!"
        )

        return "\n".join(message_parts)
