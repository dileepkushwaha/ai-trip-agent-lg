# Real-Time AI Agent System - Documentation

## Overview

The AI Trip Agent now includes a sophisticated real-time monitoring system that tracks your trip and provides live updates about weather, traffic, events, and travel advisories.

---

## Features

### 1. **Enhanced Trip Planning Options**

#### Travel Personas
Choose from 10 different travel personas that customize your trip recommendations:

- **🎓 Student** - Budget-friendly, educational, social experiences
- **👨‍👩‍👧‍👦 Family** - Kid-friendly activities, safe environments, comfortable accommodations
- **🏛️ Heritage** - Cultural sites, historical places, traditional experiences
- **💼 Corporate** - Efficient routes, professional venues, time-conscious planning
- **🌿 Green** - Sustainable travel, eco-friendly options, low-carbon choices
- **🚶 Solo** - Flexible itineraries, independent exploration, adventure
- **🕉️ Religious** - Spiritual sites, temples, peaceful environments
- **🧘 Spiritual** - Meditation centers, yoga retreats, tranquil locations
- **🏔️ Adventure** - Thrilling activities, outdoor experiences, active pursuits
- **💎 Luxury** - Premium accommodations, exclusive experiences, comfort

#### Transport Modes
Select your preferred mode of transportation:

- **🔀 Mixed** - AI selects the best combination of transport modes
- **🚗 Car (Petrol/Diesel/Electric)** - Private vehicle travel
- **🚌 Bus** - Public bus transportation
- **🚆 Train** - Rail travel
- **🏍️ Motorcycle** - Two-wheeler travel
- **🚴 Bicycle** - Eco-friendly cycling
- **🚶 Walking** - On-foot exploration

#### Stoppage Duration
Control your travel pace:

- **⚡ None** - Direct routes, no stoppages
- **⏰ Up to 3 hours** - Short breaks allowed
- **🕐 Up to 6 hours** - Medium-length stops
- **🕛 12+ hours** - Extended stoppages acceptable

---

### 2. **Real-Time Trip Monitoring Agent**

#### What It Does

When enabled, the AI agent continuously monitors your trip and provides real-time updates about:

- **🌤️ Weather Changes** - Alerts about rain, storms, or extreme weather
- **🚗 Traffic Conditions** - Updates on congestion and alternative routes
- **🎉 Local Events** - Notifications about festivals, exhibitions, and activities
- **⚠️ Travel Advisories** - Important alerts about road conditions, closures, etc.
- **🔄 Alternative Suggestions** - Dynamic route and activity recommendations

#### How It Works

1. **Activation**: Enable "Real-Time Monitoring" when planning your trip
2. **Agent Creation**: A unique monitoring agent is created with a tracking ID
3. **Background Monitoring**: The agent runs in the background, checking every 5 minutes
4. **Update Delivery**: Receive notifications about relevant changes
5. **Continuous Operation**: Agent monitors until you stop it or your trip ends

#### Agent Lifecycle

```
User Request → Agent Created → Monitoring Active → Updates Sent → Agent Stopped
     ↓              ↓                ↓                  ↓              ↓
  Enable RT    Unique ID        Background         Real-time      Manual/Auto
  Monitoring   Generated         Thread            Notifications    Cleanup
```

---

## API Endpoints

### Trip Planning

#### `POST /plan-trip`

Plan a trip with enhanced options.

**Request Body:**
```json
{
  "query": "Plan a 3-day trip to Kaziranga",
  "transport_mode": "mixed",
  "persona": "family",
  "stoppage_duration": "6_hours",
  "enable_realtime_agent": true,
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "session_123456",
  "destination": "Kaziranga National Park",
  "duration_days": 3,
  "itinerary": {...},
  "carbon_emissions": {...},
  "green_alternatives": [...],
  "messages": ["Trip planned successfully!"],
  "agent_id": "agent_abc123def456",
  "timestamp": "2025-10-06T12:00:00"
}
```

### Agent Management

#### `GET /agent/{agent_id}/status`

Get the current status of a monitoring agent.

**Response:**
```json
{
  "agent_id": "agent_abc123def456",
  "status": "active",
  "created_at": "2025-10-06T12:00:00",
  "last_check": "2025-10-06T12:05:00",
  "updates": [
    {
      "timestamp": "2025-10-06T12:03:00",
      "message": "Weather alert: Rain expected in Kaziranga",
      "type": "warning",
      "data": {...}
    }
  ],
  "trip_details": {...}
}
```

#### `POST /agent/{agent_id}/stop`

Stop a monitoring agent.

**Response:**
```json
{
  "success": true,
  "message": "Agent stopped successfully",
  "timestamp": "2025-10-06T12:10:00"
}
```

#### `GET /agents`

List all active monitoring agents.

**Response:**
```json
{
  "agents": [...],
  "count": 5,
  "timestamp": "2025-10-06T12:00:00"
}
```

#### `POST /agents/cleanup`

Clean up old agents (default: 24 hours).

**Query Parameters:**
- `max_age_hours` (optional): Maximum age in hours (default: 24)

**Response:**
```json
{
  "success": true,
  "removed_count": 3,
  "message": "Cleaned up 3 old agents",
  "timestamp": "2025-10-06T12:00:00"
}
```

---

## UI Features

### Dark/Light Mode

Toggle between dark and light themes using the button in the top-right corner:
- **☀️** - Switch to light mode
- **🌙** - Switch to dark mode

### Trip Configuration Panel

Located in the sidebar, configure all trip options:

1. **Travel Persona** - Select your travel style
2. **Transport Mode** - Choose transportation
3. **Stoppage Duration** - Set maximum stoppage time
4. **Real-Time Monitoring** - Enable/disable agent

### Active Agents Display

When agents are active, they appear at the top of the main panel showing:
- Agent ID
- Current status (🟢 Active, 🔵 Monitoring, 🟡 Alert, ⚫ Stopped, 🔴 Error)
- Last check time
- Recent updates
- Stop and Refresh buttons

### Message Display

Messages are color-coded:
- **Blue** - User messages
- **Green** - Assistant responses
- **Orange** - Agent updates

---

## Technical Architecture

### Components

1. **Streamlit UI** (`ui/streamlit_app.py`)
   - Enhanced interface with theme support
   - Real-time agent status display
   - Configuration options

2. **Real-Time Agent** (`agents/realtime_agent.py`)
   - Background monitoring thread
   - Update generation
   - Agent lifecycle management

3. **Agent Manager** (`agents/realtime_agent.py`)
   - Agent creation and tracking
   - Status queries
   - Cleanup operations

4. **API Endpoints** (`services/api/main.py`)
   - Trip planning with agent creation
   - Agent status and control
   - Agent listing and cleanup

5. **State Management** (`agents/state.py`)
   - Enhanced state schema
   - Persona and preferences
   - Agent tracking fields

### Data Flow

```
User Input → Streamlit UI → FastAPI → Agent Graph → LLM
                ↓              ↓           ↓
            Agent Manager ← Response ← State Update
                ↓
         Background Thread
                ↓
         Monitoring Loop
                ↓
         Update Generation
                ↓
         Status Query ← Streamlit UI
```

---

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Real-time agent settings
AGENT_CHECK_INTERVAL=300  # 5 minutes
AGENT_MAX_AGE_HOURS=24
AGENT_MAX_UPDATES=20
```

### Agent Settings

Customize in `agents/realtime_agent.py`:

```python
check_interval: int = 300  # Check every 5 minutes
max_updates: int = 20      # Keep last 20 updates
```

---

## Usage Examples

### Example 1: Family Trip with Real-Time Monitoring

```python
# Request
{
  "query": "Plan a 3-day family trip to Kaziranga with kids",
  "persona": "family",
  "transport_mode": "car_petrol",
  "stoppage_duration": "6_hours",
  "enable_realtime_agent": true
}

# Agent monitors:
# - Weather for outdoor activities
# - Kid-friendly events
# - Traffic on family routes
# - Safety advisories
```

### Example 2: Sustainable Solo Adventure

```python
# Request
{
  "query": "Eco-friendly solo trip to Majuli for 2 days",
  "persona": "green",
  "transport_mode": "mixed",
  "stoppage_duration": "3_hours",
  "enable_realtime_agent": true
}

# Agent monitors:
# - Eco-friendly events
# - Public transport options
# - Sustainable activities
# - Carbon-saving alternatives
```

### Example 3: Corporate Business Trip

```python
# Request
{
  "query": "Quick business trip to Guwahati",
  "persona": "corporate",
  "transport_mode": "car_electric",
  "stoppage_duration": "none",
  "enable_realtime_agent": false
}

# Optimized for:
# - Efficient routes
# - Professional venues
# - Time-conscious planning
# - No monitoring needed
```

---

## Best Practices

### When to Enable Real-Time Monitoring

✅ **Enable for:**
- Multi-day trips
- Outdoor activities
- Weather-dependent plans
- Unfamiliar destinations
- Peak travel seasons

❌ **Skip for:**
- Short day trips
- Indoor activities
- Familiar routes
- Off-season travel
- Quick business trips

### Agent Management

1. **Stop agents** when trip is complete
2. **Refresh status** periodically during trip
3. **Review updates** before making changes
4. **Clean up old agents** regularly

### Performance Tips

1. Use "mixed" transport for optimal suggestions
2. Set realistic stoppage durations
3. Choose appropriate persona
4. Enable monitoring only when needed
5. Stop agents after trip completion

---

## Troubleshooting

### Agent Not Starting

**Problem**: Agent ID not returned after trip planning

**Solutions**:
- Ensure `enable_realtime_agent` is `true`
- Check API logs for errors
- Verify agent manager is initialized

### No Updates Received

**Problem**: Agent status shows no updates

**Solutions**:
- Wait for check interval (5 minutes)
- Refresh agent status
- Check agent status is "active"
- Review API logs

### Agent Stuck in Error State

**Problem**: Agent shows error status

**Solutions**:
- Stop and recreate agent
- Check API connectivity
- Review error logs
- Restart API service

---

## Future Enhancements

### Planned Features

1. **Real API Integrations**
   - Weather API (OpenWeatherMap)
   - Traffic API (Google Maps)
   - Events API (Eventbrite)
   - News API (NewsAPI)

2. **Advanced Notifications**
   - Email alerts
   - SMS notifications
   - Push notifications
   - Webhook support

3. **Machine Learning**
   - Predictive analytics
   - Pattern recognition
   - Personalized recommendations
   - Anomaly detection

4. **Enhanced Monitoring**
   - Real-time location tracking
   - Geofencing alerts
   - Dynamic rerouting
   - Emergency assistance

---

## Support

For issues or questions:
- Check API logs: `tail -f logs/api.log`
- Check UI logs: `tail -f logs/ui.log`
- Review agent status: `GET /agents`
- Test system: `python scripts/test_system.py`

---

**Version**: 2.0.0  
**Last Updated**: October 2025  
**Status**: Production Ready
