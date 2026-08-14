"""
Real-time trip monitoring agent.
Monitors news, events, weather, and provides real-time updates during trips.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid
from dataclasses import dataclass, field
import threading
import time

logger = logging.getLogger(__name__)


@dataclass
class AgentUpdate:
    """Represents an update from the monitoring agent."""
    timestamp: str
    message: str
    type: str  # info, warning, alert, success
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TripMonitoringAgent:
    """
    Real-time trip monitoring agent.
    
    Monitors various aspects of a trip and provides updates:
    - Weather changes
    - Traffic conditions
    - Local events
    - Travel advisories
    - Alternative routes
    """
    
    agent_id: str
    trip_details: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "active"
    updates: List[AgentUpdate] = field(default_factory=list)
    last_check: datetime = field(default_factory=datetime.now)
    check_interval: int = 300  # 5 minutes
    _stop_flag: bool = False
    _thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the monitoring agent in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning(f"Agent {self.agent_id} is already running")
            return
        
        self._stop_flag = False
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info(f"Started monitoring agent {self.agent_id}")
    
    def stop(self):
        """Stop the monitoring agent."""
        self._stop_flag = True
        self.status = "stopped"
        logger.info(f"Stopped monitoring agent {self.agent_id}")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while not self._stop_flag:
            try:
                self._perform_checks()
                self.last_check = datetime.now()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop for agent {self.agent_id}: {e}")
                self.status = "error"
                self.add_update(
                    message=f"Monitoring error: {str(e)}",
                    update_type="alert"
                )
    
    def _perform_checks(self):
        """Perform all monitoring checks."""
        destination = self.trip_details.get('destination', '')
        
        # Check weather (simulated for now)
        self._check_weather(destination)
        
        # Check traffic (simulated for now)
        self._check_traffic(destination)
        
        # Check local events (simulated for now)
        self._check_events(destination)
        
        # Check travel advisories (simulated for now)
        self._check_advisories(destination)
    
    def _check_weather(self, destination: str):
        """Check weather conditions."""
        # Simulated weather check
        # In production, integrate with weather API
        import random
        
        conditions = ["clear", "cloudy", "rainy", "stormy"]
        condition = random.choice(conditions)
        
        if condition in ["rainy", "stormy"]:
            self.add_update(
                message=f"Weather alert for {destination}: {condition.title()} conditions expected. Consider indoor activities or carry rain gear.",
                update_type="warning",
                data={"condition": condition, "destination": destination}
            )
    
    def _check_traffic(self, destination: str):
        """Check traffic conditions."""
        # Simulated traffic check
        # In production, integrate with traffic API
        import random
        
        if random.random() < 0.2:  # 20% chance of traffic
            self.add_update(
                message=f"Traffic update: Heavy traffic reported on routes to {destination}. Consider alternative routes or adjust timing.",
                update_type="info",
                data={"destination": destination}
            )
    
    def _check_events(self, destination: str):
        """Check local events."""
        # Simulated event check
        # In production, integrate with events API
        import random
        
        events = [
            "Local festival happening this weekend",
            "Cultural exhibition at the museum",
            "Food festival in the city center",
            "Wildlife photography workshop",
            "Traditional dance performance"
        ]
        
        if random.random() < 0.15:  # 15% chance of event
            event = random.choice(events)
            self.add_update(
                message=f"Event alert for {destination}: {event}. This might be of interest!",
                update_type="success",
                data={"event": event, "destination": destination}
            )
    
    def _check_advisories(self, destination: str):
        """Check travel advisories."""
        # Simulated advisory check
        # In production, integrate with travel advisory API
        import random
        
        if random.random() < 0.05:  # 5% chance of advisory
            self.add_update(
                message=f"Travel advisory for {destination}: Road maintenance scheduled. Plan for possible delays.",
                update_type="warning",
                data={"destination": destination}
            )
    
    def add_update(self, message: str, update_type: str, data: Dict[str, Any] = None):
        """Add a new update."""
        update = AgentUpdate(
            timestamp=datetime.now().isoformat(),
            message=message,
            type=update_type,
            data=data or {}
        )
        self.updates.append(update)

        # Keep only last 20 updates
        if len(self.updates) > 20:
            self.updates = self.updates[-20:]

        logger.info(f"Agent {self.agent_id} update: {message}")

    def handle_action(self, action: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Handle user-initiated actions."""
        # Friendly fallback destination name
        destination = self.trip_details.get('destination', 'your destination')

        if action == "replan":
            return self._handle_replan(details)
        elif action == "delayed":
            return self._handle_delay(details)
        elif action == "check_weather":
            return self._handle_weather_check()
        elif action == "check_news":
            return self._handle_news_check()
        elif action == "security_check":
            return self._handle_security_check()
        else:
            self.add_update(
                message=f"⚠️ Received unknown action: {action}",
                update_type="error",
                data={"action": action, "details": details}
            )
            return {"error": f"Unknown action: {action}"}

    def _handle_replan(self, reason: Optional[str]) -> Dict[str, Any]:
        """Handle trip replanning request."""
        destination = self.trip_details.get('destination', 'your destination')

        self.add_update(
            message=f"🔄 Trip replanning initiated for {destination}. Analyzing current conditions and generating alternative routes...",
            update_type="info"
        )

        # Simulate replanning
        import random
        suggestions = [
            "Consider taking the scenic route via NH-37 for better road conditions",
            "Alternative accommodation available at a nearby location with better reviews",
            "Adjust timing to avoid peak traffic hours (9 AM - 11 AM)",
            "Add a stopover at a popular viewpoint along the way"
        ]

        suggestion = random.choice(suggestions)
        self.add_update(
            message=f"✅ Replanning complete! Suggestion: {suggestion}",
            update_type="success",
            data={"suggestion": suggestion}
        )

        return {
            "success": True,
            "message": "Trip replanned successfully",
            "suggestion": suggestion
        }

    def _handle_delay(self, reason: Optional[str]) -> Dict[str, Any]:
        """Handle trip delay notification."""
        reason_text = reason or "unspecified reason"
        destination = self.trip_details.get('destination', 'your destination')

        self.add_update(
            message=f"⏰ Trip delay reported due to {reason_text}. Adjusting schedule...",
            update_type="warning"
        )

        # Simulate schedule adjustment
        import random
        adjustments = [
            "Extended checkout time arranged at current location",
            "Next destination notified of delayed arrival",
            "Alternative activities suggested for the extra time",
            "Dinner reservation rescheduled to accommodate delay"
        ]

        adjustment = random.choice(adjustments)
        self.add_update(
            message=f"✅ Schedule adjusted: {adjustment}",
            update_type="success",
            data={"adjustment": adjustment}
        )

        return {
            "success": True,
            "message": "Schedule adjusted for delay",
            "adjustment": adjustment
        }

    def _handle_weather_check(self) -> Dict[str, Any]:
        """Handle weather check request."""
        destination = self.trip_details.get('destination', 'your destination')

        self.add_update(
            message=f"🌤️ Checking current weather conditions for {destination}...",
            update_type="info"
        )

        # Simulate weather check
        import random
        conditions = [
            ("Clear skies", "Perfect weather for outdoor activities!", "success"),
            ("Partly cloudy", "Good weather with occasional clouds. Carry sunscreen.", "info"),
            ("Light rain expected", "Pack an umbrella. Indoor activities recommended for afternoon.", "warning"),
            ("Heavy rain forecast", "Consider rescheduling outdoor activities. Stay safe!", "alert")
        ]

        condition, advice, update_type = random.choice(conditions)
        self.add_update(
            message=f"🌤️ Weather Update: {condition}. {advice}",
            update_type=update_type,
            data={"condition": condition, "advice": advice}
        )

        return {
            "success": True,
            "condition": condition,
            "advice": advice
        }

    def _handle_news_check(self) -> Dict[str, Any]:
        """Handle news check request."""
        destination = self.trip_details.get('destination', 'your destination')

        self.add_update(
            message=f"📰 Fetching latest news and updates for {destination}...",
            update_type="info"
        )

        # Simulate news check
        import random
        news_items = [
            ("Local festival announced", "A cultural festival is happening this weekend. Great opportunity to experience local culture!", "success"),
            ("Road maintenance scheduled", "NH-37 will have maintenance work from 10 PM to 6 AM. Plan accordingly.", "warning"),
            ("New tourist attraction opened", "A new wildlife viewing platform has opened at the national park.", "success"),
            ("Travel advisory issued", "Increased security checks at major tourist spots. Carry valid ID.", "info")
        ]

        headline, details, update_type = random.choice(news_items)
        self.add_update(
            message=f"📰 News: {headline}. {details}",
            update_type=update_type,
            data={"headline": headline, "details": details}
        )

        return {
            "success": True,
            "headline": headline,
            "details": details
        }

    def _handle_security_check(self) -> Dict[str, Any]:
        """Handle security check request."""
        destination = self.trip_details.get('destination', 'your destination')

        self.add_update(
            message=f"🚨 Performing security check for {destination}...",
            update_type="info"
        )

        # Simulate security check
        import random
        security_status = [
            ("All clear", "No security concerns reported. Safe to proceed with your plans.", "success"),
            ("Minor advisory", "Avoid isolated areas after dark. Stay in well-lit, populated areas.", "info"),
            ("Weather alert", "Storm warning issued. Stay indoors and follow local authorities' guidance.", "warning")
        ]

        status, advice, update_type = random.choice(security_status)
        self.add_update(
            message=f"🚨 Security Status: {status}. {advice}",
            update_type=update_type,
            data={"status": status, "advice": advice}
        )

        return {
            "success": True,
            "status": status,
            "advice": advice
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_check": self.last_check.isoformat(),
            "updates": [
                {
                    "timestamp": u.timestamp,
                    "message": u.message,
                    "type": u.type,
                    "data": u.data
                }
                for u in self.updates[-10:]  # Return last 10 updates
            ],
            "trip_details": self.trip_details
        }


class AgentManager:
    """Manages multiple trip monitoring agents."""
    
    def __init__(self):
        self.agents: Dict[str, TripMonitoringAgent] = {}
        logger.info("AgentManager initialized")
    
    def create_agent(self, trip_details: Dict[str, Any]) -> str:
        """Create a new monitoring agent."""
        agent_id = f"agent_{uuid.uuid4().hex[:12]}"
        
        agent = TripMonitoringAgent(
            agent_id=agent_id,
            trip_details=trip_details
        )
        
        self.agents[agent_id] = agent
        agent.start()
        
        logger.info(f"Created and started agent {agent_id}")
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[TripMonitoringAgent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get agent status."""
        agent = self.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        
        return agent.get_status()
    
    def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.stop()
        return True
    
    def cleanup_old_agents(self, max_age_hours: int = 24):
        """Clean up agents older than specified hours."""
        now = datetime.now()
        to_remove = []
        
        for agent_id, agent in self.agents.items():
            age = now - agent.created_at
            if age > timedelta(hours=max_age_hours):
                agent.stop()
                to_remove.append(agent_id)
        
        for agent_id in to_remove:
            del self.agents[agent_id]
            logger.info(f"Cleaned up old agent {agent_id}")
        
        return len(to_remove)
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get status of all agents."""
        return [agent.get_status() for agent in self.agents.values()]


# Global agent manager instance
agent_manager = AgentManager()
