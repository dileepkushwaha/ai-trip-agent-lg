"""
Streamlit UI for AI Trip Agent - Enhanced Version
Interactive chat interface with real-time trip monitoring
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
import time
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import centralized theme
from styles.theme import THEMES, get_theme_css

# Page configuration
st.set_page_config(
    page_title="AI Trip Agent - Assam",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8001"

# Initialize session state for theme
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    """Toggle between light and dark theme."""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Get current theme and apply CSS
current_theme = THEMES[st.session_state.theme]
st.markdown(get_theme_css(current_theme, page_type="main"), unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def plan_trip(
    query: str,
    transport_mode: str,
    persona: str,
    stoppage_duration: str,
    enable_realtime_agent: bool,
    travel_date: Optional[str] = None,
    travel_time: Optional[str] = None,
    is_round_trip: bool = False,
    return_date: Optional[str] = None,
    return_time: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Call the trip planning API with enhanced options."""
    try:
        payload = {
            "query": query,
            "transport_mode": transport_mode,
            "persona": persona,
            "stoppage_duration": stoppage_duration,
            "enable_realtime_agent": enable_realtime_agent,
            "session_id": session_id
        }

        # Add date/time if provided
        if travel_date:
            payload["travel_date"] = str(travel_date)
        if travel_time:
            payload["travel_time"] = str(travel_time)

        # Add round trip info
        payload["is_round_trip"] = is_round_trip
        if is_round_trip:
            if return_date:
                payload["return_date"] = str(return_date)
            if return_time:
                payload["return_time"] = str(return_time)

        response = requests.post(
            f"{API_BASE_URL}/plan-trip",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None


def get_agent_status(agent_id: str) -> Dict[str, Any]:
    """Get real-time agent status."""
    try:
        response = requests.get(f"{API_BASE_URL}/agent/{agent_id}/status", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def stop_agent(agent_id: str) -> bool:
    """Stop a running real-time agent."""
    try:
        response = requests.post(f"{API_BASE_URL}/agent/{agent_id}/stop", timeout=5)
        response.raise_for_status()
        return True
    except Exception:
        return False


def display_carbon_info(carbon_data: Dict[str, Any], alternatives: list):
    """Display carbon footprint information."""
    st.markdown("### 🌱 Carbon Footprint Analysis")
    st.markdown("*Calculated based on **GHG Protocol** and **SBTi** standards*")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Distance",
            f"{carbon_data.get('distance_km', 0):.0f} km"
        )

    with col2:
        st.metric(
            "CO2 Emissions",
            f"{carbon_data.get('emissions_kg', 0):.2f} kg"
        )

    with col3:
        st.metric(
            "Tree Equivalent",
            f"{carbon_data.get('equivalent_trees', 0):.1f} trees"
        )

    if alternatives:
        st.markdown("#### ♻️ Greener Alternatives")
        for alt in alternatives:
            savings = alt.get('savings_percentage', 0)
            mode = alt.get('mode', '').replace('_', ' ').title()
            emissions = alt.get('emissions_kg', 0)

            st.markdown(f"""
            <div class="carbon-box">
                <strong>{mode}</strong><br>
                Emissions: {emissions:.2f} kg CO2e<br>
                <span style="font-weight: bold;">💚 Save {savings:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)


def display_itinerary(itinerary: Dict[str, Any]):
    """Display trip itinerary."""
    st.markdown("### 📅 Your Trip Itinerary")

    destination = itinerary.get('destination', 'N/A')
    duration = itinerary.get('duration_days', 0)
    traveler_type = itinerary.get('traveler_type', 'N/A').title()
    interests = ', '.join(itinerary.get('interests', []))

    st.markdown(f"""
    <div class="itinerary-box">
        <strong>Destination:</strong> {destination}<br>
        <strong>Duration:</strong> {duration} days<br>
        <strong>Traveler Type:</strong> {traveler_type}<br>
        <strong>Interests:</strong> {interests}
    </div>
    """, unsafe_allow_html=True)

    full_itinerary = itinerary.get('full_itinerary', '')
    if full_itinerary:
        st.markdown(f'<div style="padding: 1rem; background-color: {current_theme["bg_secondary"]}; border-radius: 0.5rem; margin-top: 1rem;">{full_itinerary}</div>', unsafe_allow_html=True)


def display_agent_status(agent_id: str, status_data: Dict[str, Any]):
    """Display real-time agent status with action buttons."""
    st.markdown("### 🤖 Real-Time Trip Agent")

    status = status_data.get('status', 'unknown')
    last_check = status_data.get('last_check', 'N/A')
    updates = status_data.get('updates', [])

    status_emoji = {
        'active': '🟢',
        'monitoring': '🔵',
        'alert': '🟡',
        'stopped': '⚫',
        'error': '🔴'
    }.get(status, '⚪')

    st.markdown(f"""
    <div class="agent-status-box">
        <strong>Agent ID:</strong> {agent_id}<br>
        <strong>Status:</strong> {status_emoji} {status.upper()}<br>
        <strong>Last Check:</strong> {last_check}<br>
        <strong>Active Updates:</strong> {len(updates)}
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    st.markdown("#### 🎯 Quick Actions")
    st.markdown('<div class="action-button-container">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Replan Trip", key=f"replan_{agent_id}", use_container_width=True):
            with st.spinner("Replanning trip..."):
                result = send_agent_action(agent_id, "replan")
                if not result.get('error'):
                    st.success("✅ Trip replanning initiated!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error')}")

        if st.button("🌤️ Check Weather", key=f"weather_{agent_id}", use_container_width=True):
            with st.spinner("Checking weather..."):
                result = send_agent_action(agent_id, "check_weather")
                if not result.get('error'):
                    st.success("✅ Weather check initiated!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error')}")

    with col2:
        if st.button("⏰ Delayed (Personal)", key=f"delayed_{agent_id}", use_container_width=True):
            with st.spinner("Adjusting schedule..."):
                result = send_agent_action(agent_id, "delayed", "personal_reason")
                if not result.get('error'):
                    st.success("✅ Schedule adjusted!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error')}")

        if st.button("📰 Check News", key=f"news_{agent_id}", use_container_width=True):
            with st.spinner("Fetching news..."):
                result = send_agent_action(agent_id, "check_news")
                if not result.get('error'):
                    st.success("✅ News check initiated!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error')}")

    with col3:
        if st.button("🚨 Security Check", key=f"security_{agent_id}", use_container_width=True):
            with st.spinner("Checking security..."):
                result = send_agent_action(agent_id, "security_check")
                if not result.get('error'):
                    st.success("✅ Security check initiated!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error')}")

        if st.button("✅ Trip Finished", key=f"finish_{agent_id}", use_container_width=True, type="primary"):
            if stop_agent(agent_id):
                st.success("🎉 Trip completed! Agent stopped.")
                if agent_id in st.session_state.active_agents:
                    del st.session_state.active_agents[agent_id]
                st.rerun()
            else:
                st.error("❌ Failed to stop agent")

    st.markdown('</div>', unsafe_allow_html=True)

    if updates:
        st.markdown("#### 📰 Recent Updates")
        for update in updates:
            timestamp = update.get('timestamp', '')
            message = update.get('message', '')
            update_type = update.get('type', 'info')

            icon = {'info': 'ℹ️', 'warning': '⚠️', 'alert': '🚨', 'success': '✅'}.get(update_type, 'ℹ️')

            st.markdown(f"""
            <div class="message-agent">
                {icon} <strong>{timestamp}</strong><br>
                {message}
            </div>
            """, unsafe_allow_html=True)


def send_agent_action(agent_id: str, action: str, reason: str = None) -> Dict[str, Any]:
    """Send action to agent."""
    try:
        payload = {"action": action}
        if reason:
            payload["reason"] = reason

        response = requests.post(
            f"{API_BASE_URL}/agent/{agent_id}/action",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def main():
    """Main Streamlit application."""

    # Theme toggle and navigation
    col1, col2, col3, col4 = st.columns([5, 2, 1, 1])
    with col2:
        if st.button("📊 Observability", use_container_width=True):
            # Fixed navigation path - relative to current directory
            if os.path.exists("../pages/1_📊_Observability.py"):
                st.switch_page("../pages/1_📊_Observability.py")
            else:
                st.switch_page("pages/1_📊_Observability.py")
    with col3:
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(theme_icon, key="theme_toggle"):
            toggle_theme()
            st.rerun()

    # Header
    st.markdown('<div class="main-header">🧳 AI Trip Agent</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Your Intelligent Travel Companion for Assam with Real-Time Monitoring</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar with enhanced options
    with st.sidebar:
        st.markdown("## ⚙️ Trip Configuration")
        
        # Check API health
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.info("Please start the FastAPI backend")
        
        st.markdown("---")
        
        # Persona selection
        st.markdown("### 👤 Travel Persona")
        persona = st.selectbox(
            "Select your travel style",
            options=[
                "student",
                "family",
                "heritage",
                "corporate",
                "green",
                "solo",
                "religious",
                "spiritual",
                "adventure",
                "luxury"
            ],
            format_func=lambda x: {
                "student": "🎓 Student - Budget-friendly",
                "family": "👨‍👩‍👧‍👦 Family - Kid-friendly",
                "heritage": "🏛️ Heritage - Cultural sites",
                "corporate": "💼 Corporate - Business travel",
                "green": "🌿 Green - Sustainable travel",
                "solo": "🚶 Solo - Independent explorer",
                "religious": "🕉️ Religious - Spiritual sites",
                "spiritual": "🧘 Spiritual - Meditation & peace",
                "adventure": "🏔️ Adventure - Thrill seeker",
                "luxury": "💎 Luxury - Premium experience"
            }[x]
        )
        
        st.markdown("---")
        
        # Transport mode selection
        st.markdown("### 🚗 Transport Mode")
        transport_mode = st.selectbox(
            "Select transport preference",
            options=[
                "mixed",
                "car_petrol",
                "car_diesel",
                "car_electric",
                "bus",
                "train",
                "motorcycle",
                "bicycle",
                "walking"
            ],
            format_func=lambda x: {
                "mixed": "🔀 Mixed - Best combination",
                "car_petrol": "🚗 Car (Petrol)",
                "car_diesel": "🚙 Car (Diesel)",
                "car_electric": "⚡ Car (Electric)",
                "bus": "🚌 Bus",
                "train": "🚆 Train",
                "motorcycle": "🏍️ Motorcycle",
                "bicycle": "🚴 Bicycle",
                "walking": "🚶 Walking"
            }[x]
        )
        
        st.markdown("---")
        
        # Stoppage duration
        st.markdown("### ⏱️ Stoppage Duration")
        stoppage_duration = st.selectbox(
            "Maximum stoppage time",
            options=[
                "none",
                "3_hours",
                "6_hours",
                "12_hours_plus"
            ],
            format_func=lambda x: {
                "none": "⚡ No stoppages - Direct",
                "3_hours": "⏰ Up to 3 hours",
                "6_hours": "🕐 Up to 6 hours",
                "12_hours_plus": "🕛 12+ hours OK"
            }[x]
        )

        st.markdown("---")

        # Date and Time selection
        st.markdown("### 📅 Travel Date & Time")

        col1, col2 = st.columns(2)
        with col1:
            travel_date = st.date_input(
                "Departure Date",
                value=None,
                help="Select your departure date"
            )

        with col2:
            travel_time = st.time_input(
                "Departure Time",
                value=None,
                help="Select your departure time"
            )

        # Round trip option
        is_round_trip = st.checkbox(
            "🔄 Round Trip",
            value=False,
            help="Check if you need a return journey"
        )

        if is_round_trip:
            col3, col4 = st.columns(2)
            with col3:
                return_date = st.date_input(
                    "Return Date",
                    value=None,
                    help="Select your return date"
                )

            with col4:
                return_time = st.time_input(
                    "Return Time",
                    value=None,
                    help="Select your return time"
                )
        else:
            return_date = None
            return_time = None

        st.markdown("---")
        
        # Real-time agent toggle
        st.markdown("### 🤖 Real-Time Monitoring")
        enable_realtime_agent = st.checkbox(
            "Enable AI Agent for trip monitoring",
            value=False,
            help="AI agent will monitor news, events, and provide real-time updates during your trip"
        )
        
        if enable_realtime_agent:
            st.info("🔔 Agent will monitor:\n- Weather updates\n- Traffic conditions\n- Local events\n- Travel advisories\n- Alternative routes")
        
        st.markdown("---")
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        st.markdown("""
        - Plan a 3-day wildlife trip to Kaziranga
        - Family vacation to Majuli for 2 days
        - Weekend getaway near Guwahati
        - 5-day cultural heritage tour
        - Budget-friendly student trip
        - Sustainable eco-tourism package
        """)
        
        st.markdown("---")
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.active_agents = {}
            st.rerun()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    
    if "active_agents" not in st.session_state:
        st.session_state.active_agents = {}
    
    # Display active agents
    if st.session_state.active_agents:
        st.markdown("## 🤖 Active Trip Monitoring Agents")
        
        for agent_id, agent_info in list(st.session_state.active_agents.items()):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                status_data = get_agent_status(agent_id)
                if not status_data.get('error'):
                    display_agent_status(agent_id, status_data)
            
            with col2:
                if st.button(f"⏹️ Stop", key=f"stop_{agent_id}"):
                    if stop_agent(agent_id):
                        del st.session_state.active_agents[agent_id]
                        st.success("Agent stopped")
                        st.rerun()
                
                if st.button(f"🔄 Refresh", key=f"refresh_{agent_id}"):
                    st.rerun()
        
        st.markdown("---")
    
    # Display conversation history
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(
                f'<div class="message-user"><strong>👤 You:</strong><br><div class="response-content">{content}</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="message-assistant"><strong>🤖 Assistant:</strong><br><div class="response-content">{content}</div></div>',
                unsafe_allow_html=True
            )
        
        # Display additional data if available
        if "carbon_data" in message:
            display_carbon_info(message["carbon_data"], message.get("alternatives", []))
        
        if "itinerary" in message:
            display_itinerary(message["itinerary"])
    
    # Chat input
    user_query = st.chat_input("Ask me about your trip to Assam...")
    
    if user_query:
        if not api_healthy:
            st.error("❌ Cannot process request: API is not available")
            return
        
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_query
        })
        
        # Show user message immediately
        st.markdown(
            f'<div class="message-user"><strong>👤 You:</strong><br><div class="response-content">{user_query}</div></div>',
            unsafe_allow_html=True
        )

        # Call API
        with st.spinner("🧳 Planning your trip... This may take a moment..."):
            response = plan_trip(
                query=user_query,
                transport_mode=transport_mode,
                persona=persona,
                stoppage_duration=stoppage_duration,
                enable_realtime_agent=enable_realtime_agent,
                travel_date=travel_date,
                travel_time=travel_time,
                is_round_trip=is_round_trip,
                return_date=return_date if is_round_trip else None,
                return_time=return_time if is_round_trip else None,
                session_id=st.session_state.session_id
            )
        
        if response:
            # Update session ID
            st.session_state.session_id = response.get("session_id")
            
            # Register real-time agent if enabled
            if enable_realtime_agent and response.get("agent_id"):
                agent_id = response["agent_id"]
                st.session_state.active_agents[agent_id] = {
                    "created_at": datetime.now().isoformat(),
                    "query": user_query
                }
            
            # Extract response content
            messages = response.get("messages", [])
            
            if not messages:
                content = "I've processed your request. Here's what I found:"
            else:
                content = "\n\n".join(messages) if isinstance(messages, list) else str(messages)
            
            if not content or content.strip() == "":
                content = f"Response received. Planning your trip with:\n"
                content += f"- Persona: {persona}\n"
                content += f"- Transport: {transport_mode}\n"
                content += f"- Stoppage: {stoppage_duration}\n"
                content += f"- Destination: {response.get('destination', 'N/A')}\n"
                content += f"- Duration: {response.get('duration_days', 0)} days\n"
            
            # Prepare assistant message
            assistant_message = {
                "role": "assistant",
                "content": content,
            }
            
            # Add carbon data if available
            if response.get("carbon_emissions"):
                assistant_message["carbon_data"] = response["carbon_emissions"]
                assistant_message["alternatives"] = response.get("green_alternatives", [])
            
            # Add itinerary if available
            if response.get("itinerary"):
                assistant_message["itinerary"] = response["itinerary"]
            
            # Add error if present
            if response.get("error"):
                assistant_message["content"] += f"\n\n⚠️ Error: {response['error']}"
            
            st.session_state.messages.append(assistant_message)
            
            # Rerun to display new message
            st.rerun()


if __name__ == "__main__":
    main()