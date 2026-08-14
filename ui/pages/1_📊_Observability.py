"""
Observability Dashboard for AI Trip Agent
Monitors LangSmith traces, active agents, and system metrics
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
import time
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import centralized theme
from styles.theme import THEMES, get_theme_css

# Page configuration
st.set_page_config(
    page_title="Observability Dashboard - AI Trip Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8001"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "ai-trip-agent")

# Initialize session state for theme - Fixed to match main app
if "theme" not in st.session_state:
    st.session_state.theme = "light"  # Default to light to match main app

def toggle_theme():
    """Toggle between light and dark theme."""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Get current theme and apply CSS
current_theme = THEMES[st.session_state.theme]
st.markdown(get_theme_css(current_theme, page_type="observability"), unsafe_allow_html=True)


def get_all_agents() -> List[Dict[str, Any]]:
    """Get all active agents from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/agents", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("agents", [])
    except Exception as e:
        st.error(f"Failed to fetch agents: {e}")
        return []


def get_agent_details(agent_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific agent."""
    try:
        response = requests.get(f"{API_BASE_URL}/agent/{agent_id}/status", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_api_health() -> Dict[str, Any]:
    """Get API health status."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def format_duration(created_at: str) -> str:
    """Calculate duration since agent creation."""
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(created.tzinfo)
        delta = now - created
        
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if delta.days > 0:
            return f"{delta.days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "N/A"


def main():
    """Main observability dashboard."""
    
    # Header with navigation
    col1, col2, col3 = st.columns([6, 2, 1])
    with col1:
        st.markdown('<h1 style="margin: 0;">📊 Observability Dashboard</h1>', unsafe_allow_html=True)
    with col2:
        if st.button("🏠 Back to Main App", use_container_width=True):
            # Fixed navigation path - relative to current directory
            if os.path.exists("../ui/streamlit_app.py"):
                st.switch_page("../ui/streamlit_app.py")
            else:
                st.switch_page("ui/streamlit_app.py")
    with col3:
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(theme_icon, key="theme_toggle"):
            toggle_theme()
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔧 Dashboard Controls")
        
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 5, 60, 10)
        
        st.markdown("---")
        
        st.markdown("### 📊 Metrics")
        show_agents = st.checkbox("Show Active Agents", value=True)
        show_traces = st.checkbox("Show LangSmith Traces", value=True)
        show_system = st.checkbox("Show System Metrics", value=True)
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
    
    # System Health
    st.markdown("## 🏥 System Health")
    health = get_api_health()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = current_theme['success'] if health.get('status') == 'healthy' else current_theme['danger']
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {status_color};">API Status</h3>
            <p style="font-size: 1.5rem; font-weight: bold;">{health.get('status', 'unknown').upper()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Version</h3>
            <p style="font-size: 1.5rem; font-weight: bold;">{health.get('version', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        llm_status = "✅ Connected" if health.get('llm_provider') else "❌ Disconnected"
        st.markdown(f"""
        <div class="metric-card">
            <h3>LLM Provider</h3>
            <p style="font-size: 1.2rem; font-weight: bold;">{health.get('llm_provider', 'N/A')}</p>
            <p style="font-size: 0.9rem;">{llm_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        chroma_status = "✅ Connected" if health.get('chroma_connected') else "❌ Disconnected"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Vector DB</h3>
            <p style="font-size: 1.2rem; font-weight: bold;">ChromaDB</p>
            <p style="font-size: 0.9rem;">{chroma_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    st.markdown("## 🌱 Carbon Footprint Tracking")

    try:
        response = requests.get(f"{API_BASE_URL}/carbon/stats", timeout=5)
        response.raise_for_status()
        carbon_data = response.json()
        stats = carbon_data.get("stats", {})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_carbon = stats.get("total_carbon_kg", 0)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {current_theme['warning']};">Total Emissions</h3>
                <p style="font-size: 1.5rem; font-weight: bold;">{total_carbon:.2f} kg</p>
                <p style="font-size: 0.9rem;">CO₂e</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            total_trips = stats.get("total_trips", 0)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Trips</h3>
                <p style="font-size: 1.5rem; font-weight: bold;">{total_trips}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            avg_carbon = stats.get("average_carbon_kg", 0)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Avg per Trip</h3>
                <p style="font-size: 1.5rem; font-weight: bold;">{avg_carbon:.2f} kg</p>
                <p style="font-size: 0.9rem;">CO₂e</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            trees_needed = total_carbon / 21.77
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {current_theme['success']};">Trees to Offset</h3>
                <p style="font-size: 1.5rem; font-weight: bold;">{trees_needed:.1f}</p>
                <p style="font-size: 0.9rem;">for 1 year</p>
            </div>
            """, unsafe_allow_html=True)

        if total_trips > 0:
            st.markdown("### Recent Trips")
            recent_trips = stats.get("recent_trips", [])
            if recent_trips:
                for trip in recent_trips:
                    trip_carbon = trip.get("carbon_kg", 0)
                    trip_time = trip.get("timestamp", "")
                    trip_details = trip.get("details", {})
                    destination = trip_details.get("destination", "Unknown")
                    distance = trip_details.get("distance_km", 0)

                    st.markdown(f"""
                    <div class="agent-card">
                        <p><strong>📍 {destination.title()}</strong> - {distance:.0f} km</p>
                        <p>💨 {trip_carbon:.2f} kg CO₂e | 🕒 {trip_time[:19]}</p>
                    </div>
                    """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Reset Carbon Data", use_container_width=True, type="secondary"):
                try:
                    reset_response = requests.post(f"{API_BASE_URL}/carbon/reset", timeout=5)
                    reset_response.raise_for_status()
                    st.success("Carbon tracking data has been reset!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to reset: {e}")

    except Exception as e:
        st.error(f"Failed to load carbon footprint data: {e}")
        st.info("Make sure the API is running and carbon tracking is enabled.")
    
    # Active Agents
    if show_agents:
        st.markdown("## 🤖 Active Monitoring Agents")
        
        agents = get_all_agents()
        
        if not agents:
            st.info("No active agents currently running")
        else:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            active_count = sum(1 for a in agents if a.get('status') == 'active')
            stopped_count = sum(1 for a in agents if a.get('status') == 'stopped')
            error_count = sum(1 for a in agents if a.get('status') == 'error')
            
            with col1:
                st.metric("Total Agents", len(agents))
            with col2:
                st.metric("Active", active_count, delta=None)
            with col3:
                st.metric("Stopped", stopped_count, delta=None)
            
            st.markdown("### Agent Details")
            
            # Display each agent
            for agent in agents:
                agent_id = agent.get('agent_id', 'unknown')
                status = agent.get('status', 'unknown')
                created_at = agent.get('created_at', '')
                duration = format_duration(created_at)
                
                # Get detailed info
                details = get_agent_details(agent_id)
                updates_count = len(details.get('updates', []))
                last_check = details.get('last_check', 'N/A')
                
                # Trip details
                trip_details = agent.get('trip_details', {})
                destination = trip_details.get('destination', 'N/A')
                transport = trip_details.get('transport_mode', 'N/A')
                persona = trip_details.get('persona', 'N/A')
                
                # Status badge
                status_class = {
                    'active': 'status-active',
                    'stopped': 'status-stopped',
                    'error': 'status-error'
                }.get(status, 'status-stopped')
                
                status_emoji = {
                    'active': '🟢',
                    'stopped': '⚫',
                    'error': '🔴'
                }.get(status, '⚪')
                
                st.markdown(f"""
                <div class="agent-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0;">{status_emoji} {agent_id}</h3>
                            <span class="status-badge {status_class}">{status.upper()}</span>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; font-size: 0.9rem;">Duration: <strong>{duration}</strong></p>
                            <p style="margin: 0; font-size: 0.9rem;">Updates: <strong>{updates_count}</strong></p>
                        </div>
                    </div>
                    <hr style="margin: 1rem 0; border-color: {current_theme['text_secondary']}33;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                        <div>
                            <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">Destination</p>
                            <p style="margin: 0; font-weight: bold;">{destination}</p>
                        </div>
                        <div>
                            <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">Transport</p>
                            <p style="margin: 0; font-weight: bold;">{transport}</p>
                        </div>
                        <div>
                            <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">Persona</p>
                            <p style="margin: 0; font-weight: bold;">{persona}</p>
                        </div>
                    </div>
                    <p style="margin-top: 0.5rem; font-size: 0.85rem; opacity: 0.7;">Last Check: {last_check}</p>
                </div>
                """, unsafe_allow_html=True)

                # Show recent updates in expander
                if updates_count > 0:
                    with st.expander(f"📰 View {updates_count} Updates"):
                        for update in details.get('updates', [])[-5:]:  # Show last 5
                            timestamp = update.get('timestamp', '')
                            message = update.get('message', '')
                            update_type = update.get('type', 'info')

                            icon = {'info': 'ℹ️', 'warning': '⚠️', 'alert': '🚨', 'success': '✅'}.get(update_type, 'ℹ️')

                            st.markdown(f"""
                            <div class="trace-card">
                                {icon} <strong>{timestamp}</strong><br>
                                {message}
                            </div>
                            """, unsafe_allow_html=True)

    st.markdown("---")

    # LangSmith Traces
    if show_traces:
        st.markdown("## 🔍 LangSmith Traces")

        if LANGSMITH_API_KEY:
            st.info(f"📊 LangSmith Project: **{LANGSMITH_PROJECT}**")
            st.markdown(f"""
            View detailed traces at: [LangSmith Dashboard](https://smith.langchain.com/o/default/projects/p/{LANGSMITH_PROJECT})

            **Features:**
            - 🔍 Trace all LLM calls
            - 📊 Performance metrics
            - 🐛 Debug agent behavior
            - 📈 Cost tracking
            - ⏱️ Latency analysis
            """)

            # Placeholder for trace visualization
            st.markdown("### Recent Traces")
            st.info("Connect to LangSmith API to view recent traces here")
        else:
            st.warning("⚠️ LangSmith API key not configured. Set LANGSMITH_API_KEY environment variable to enable tracing.")
            st.markdown("""
            **To enable LangSmith tracing:**

            1. Sign up at [LangSmith](https://smith.langchain.com/)
            2. Get your API key
            3. Add to `.env` file:
               ```
               LANGSMITH_API_KEY=your_key_here
               LANGSMITH_PROJECT=ai-trip-agent
               ```
            4. Restart the API
            """)

        st.markdown("---")
    
    # System Metrics
    if show_system:
        st.markdown("## 📈 System Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔄 Request Statistics")
            st.info("Coming soon: Request count, success rate, average response time")
        
        with col2:
            st.markdown("### 💾 Resource Usage")
            st.info("Coming soon: Memory usage, CPU usage, disk space")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()