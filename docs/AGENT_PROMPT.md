# 🤖 AI Trip Agent - LLM Agent Prompt

## Project Overview

You are working on the **AI Trip Agent**, an intelligent travel planning assistant for Assam, India. This is a production-ready application that combines multiple AI agents, real-time monitoring, carbon footprint tracking, and an observability dashboard.

**Current Version**: 2.2.0  
**Status**: Production Ready  
**Tech Stack**: FastAPI, Streamlit, LangChain, LangGraph, ChromaDB, LM Studio  
**Architecture**: Multi-agent system with LangGraph orchestration

---

## 🏗️ Project Architecture

### High-Level Structure

```
ai-trip-agent/
├── ui/                          # Streamlit frontend
│   └── streamlit_app.py        # Main UI (945 lines)
├── pages/                       # Streamlit pages
│   └── 1_📊_Observability.py   # Observability dashboard (450 lines)
├── agents/                      # AI agents
│   ├── graph.py                # LangGraph workflow orchestration
│   ├── planner.py              # Trip planning agent
│   ├── itinerary.py            # Itinerary generation agent
│   ├── knowledge.py            # RAG knowledge retrieval agent
│   ├── carbon.py               # Carbon footprint agent
│   ├── realtime_agent.py       # Real-time monitoring agent (443 lines)
│   └── state.py                # Shared state schema
├── services/                    # Backend services
│   ├── api/
│   │   └── main.py             # FastAPI backend (438 lines)
│   ├── rag/
│   │   ├── embeddings.py       # Embedding management
│   │   └── vector_store.py     # ChromaDB integration
│   └── carbon/
│       └── calculator.py       # Carbon emission calculations
├── config/                      # Configuration
│   ├── settings.py             # Environment settings
│   └── llm_adapter.py          # LLM provider adapter
├── data/seed/                   # Knowledge base
│   ├── guwahati.md
│   ├── kaziranga.md
│   └── majuli.md
└── scripts/                     # Utility scripts
    ├── test_v2.2_features.py
    ├── test_action_features.py
    └── seed_vector_store.py
```

---

## 🎯 Core Features (v2.2)

### 1. **Trip Planning**
- Multi-agent workflow using LangGraph
- 10 travel personas (student, family, heritage, corporate, green, solo, religious, spiritual, adventure, luxury)
- 9 transport modes (mixed, car_petrol, car_diesel, car_electric, bus, train, motorcycle, bicycle, walking)
- Stoppage duration options (none, 3h, 6h, 12h+)
- Date/time selection for departure
- Round trip support with return date/time
- Carbon footprint calculation
- Green alternatives suggestions

### 2. **Real-Time Monitoring**
- Background agent monitoring during trips
- 6 action buttons per agent:
  - 🔄 Replan Trip
  - ⏰ Delayed (Personal)
  - 🌤️ Check Weather
  - 📰 Check News
  - 🚨 Security Check
  - ✅ Trip Finished
- Real-time updates (weather, traffic, events, advisories)
- Agent lifecycle management

### 3. **Observability Dashboard**
- System health monitoring (API, LLM, ChromaDB)
- Active agent tracking with metrics
- Agent details: ID, duration, status, parameters
- LangSmith integration for tracing
- Auto-refresh capability
- Multi-page navigation

### 4. **UI/UX**
- Dark/Light theme toggle
- Fully responsive design
- Fixed visibility issues in light mode
- Professional gradient designs
- Real-time feedback

---

## 🔑 Key Components

### 1. **LangGraph Workflow** (`agents/graph.py`)

The core orchestration uses LangGraph with these nodes:
- `planner_node`: Analyzes user query, extracts intent
- `knowledge_node`: Retrieves relevant information from vector store
- `itinerary_node`: Generates detailed trip itinerary
- `carbon_node`: Calculates carbon footprint
- `final_node`: Compiles final response

**State Flow**:
```
User Query → Planner → Knowledge → Itinerary → Carbon → Final Response
```

### 2. **State Schema** (`agents/state.py`)

```python
class AgentState(TypedDict):
    # Core fields
    messages: List[BaseMessage]
    user_query: str
    intent: Optional[str]
    
    # Trip details
    destination: Optional[str]
    duration_days: Optional[int]
    traveler_type: Optional[str]
    interests: List[str]
    
    # Enhanced options (v2.0+)
    persona: Optional[str]
    stoppage_duration: Optional[str]
    transport_mode: Optional[str]
    
    # Date/time (v2.2+)
    travel_date: Optional[str]
    travel_time: Optional[str]
    is_round_trip: bool
    return_date: Optional[str]
    return_time: Optional[str]
    
    # Real-time agent
    enable_realtime_agent: bool
    agent_id: Optional[str]
    agent_status: Optional[str]
    agent_updates: List[Dict[str, Any]]
    
    # Results
    itinerary: Optional[Dict[str, Any]]
    carbon_emissions: Optional[Dict[str, Any]]
    green_alternatives: List[Dict[str, Any]]
```

### 3. **API Endpoints** (`services/api/main.py`)

```python
# Core endpoints
POST   /plan-trip              # Plan a trip
GET    /health                 # API health check

# Agent management
GET    /agents                 # List all agents
GET    /agent/{id}/status      # Get agent status
POST   /agent/{id}/stop        # Stop agent
POST   /agent/{id}/action      # Send action to agent
```

### 4. **Real-Time Agent** (`agents/realtime_agent.py`)

```python
class TripMonitoringAgent:
    agent_id: str
    trip_details: Dict[str, Any]
    status: str  # active, stopped, error
    updates: List[AgentUpdate]
    
    # Methods
    def start()                 # Start monitoring
    def stop()                  # Stop monitoring
    def handle_action()         # Handle user actions
    def _perform_checks()       # Background monitoring
```

**Actions Supported**:
- `replan`: Replan trip with current conditions
- `delayed`: Report delay and adjust schedule
- `check_weather`: Get weather updates
- `check_news`: Fetch latest news
- `security_check`: Security assessment

---

## 🛠️ Development Guidelines

### Code Style

1. **Python**:
   - Use type hints everywhere
   - Follow PEP 8
   - Docstrings for all functions/classes
   - Use `Optional[T]` for nullable types

2. **Async/Await**:
   - FastAPI endpoints are async
   - LangChain/LangGraph calls are sync
   - Use `asyncio` for concurrent operations

3. **Error Handling**:
   - Try-except blocks for external calls
   - HTTPException for API errors
   - Logging for all errors

### File Organization

**When adding new features**:
1. Update state schema in `agents/state.py`
2. Add API model in `services/api/main.py`
3. Update UI in `ui/streamlit_app.py`
4. Add tests in `scripts/test_*.py`
5. Update documentation

**When modifying agents**:
1. Update agent logic in `agents/*.py`
2. Update graph workflow if needed
3. Test with LangSmith tracing
4. Update state schema if new fields

### Testing

**Test files**:
- `scripts/test_v2.2_features.py` - Latest features
- `scripts/test_action_features.py` - Action buttons
- `scripts/test_v2_features.py` - Core v2.0 features
- `scripts/test_system.py` - System integration

**Run tests**:
```bash
source .venv/bin/activate
python scripts/test_v2.2_features.py
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# LLM Provider
LLM_PROVIDER=lmstudio
LMSTUDIO_API_URL=http://127.0.0.1:1234/v1

# Embeddings
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8002
CHROMA_COLLECTION=assam_travel_knowledge

# LangSmith (optional)
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=ai-trip-agent

# Carbon Calculator
CARBON_DEFAULT_EMISSION_FACTOR=0.12
```

### Running Services

**Terminal 1 - API**:
```bash
source .venv/bin/activate
uvicorn services.api.main:app --port 8001 --reload
```

**Terminal 2 - UI**:
```bash
source .venv/bin/activate
streamlit run ui/streamlit_app.py --server.port 8516
```

**Terminal 3 - LM Studio**:
```bash
# Start LM Studio and load Llama-3.2-1B model
# Ensure server is running on http://127.0.0.1:1234
```

---

## 📝 Common Tasks

### Adding a New Feature

1. **Update State Schema**:
```python
# agents/state.py
class AgentState(TypedDict):
    new_field: Optional[str]  # Add your field
```

2. **Update API Model**:
```python
# services/api/main.py
class TripRequest(BaseModel):
    new_field: Optional[str] = Field(None, description="...")
```

3. **Update UI**:
```python
# ui/streamlit_app.py
new_field = st.text_input("New Field")
```

4. **Update Agent Logic**:
```python
# agents/planner.py or relevant agent
def process_new_field(state):
    new_field = state.get("new_field")
    # Process it
```

5. **Test**:
```python
# scripts/test_new_feature.py
def test_new_feature():
    response = requests.post(
        f"{API_BASE_URL}/plan-trip",
        json={"query": "...", "new_field": "value"}
    )
    assert response.status_code == 200
```

### Adding a New Agent Action

1. **Update Real-Time Agent**:
```python
# agents/realtime_agent.py
def handle_action(self, action: str, details: Optional[str]):
    if action == "new_action":
        return self._handle_new_action(details)

def _handle_new_action(self, details: Optional[str]):
    self.add_update(
        message="Processing new action...",
        update_type="info"
    )
    # Your logic here
    return {"success": True, "result": "..."}
```

2. **Update UI**:
```python
# ui/streamlit_app.py - in display_agent_status()
if st.button("🆕 New Action", key=f"new_{agent_id}"):
    result = send_agent_action(agent_id, "new_action")
```

### Adding a New Page

1. **Create Page File**:
```python
# pages/2_🆕_NewPage.py
import streamlit as st

st.set_page_config(
    page_title="New Page",
    page_icon="🆕",
    layout="wide"
)

def main():
    st.title("New Page")
    # Your content

if __name__ == "__main__":
    main()
```

2. **Add Navigation**:
```python
# ui/streamlit_app.py
if st.button("🆕 New Page"):
    st.switch_page("pages/2_🆕_NewPage.py")
```

### Modifying the LangGraph Workflow

1. **Add New Node**:
```python
# agents/graph.py
def new_node(state: AgentState) -> AgentState:
    """New node logic."""
    # Process state
    return state

# Add to graph
graph.add_node("new_node", new_node)
graph.add_edge("existing_node", "new_node")
```

2. **Update Conditional Edges**:
```python
def should_continue(state: AgentState) -> str:
    if condition:
        return "new_node"
    return "existing_node"

graph.add_conditional_edges("start", should_continue)
```

---

## 🐛 Debugging

### Common Issues

**1. LLM Not Responding**:
- Check LM Studio is running: `curl http://127.0.0.1:1234/v1/models`
- Verify model is loaded
- Check API logs: `tail -f logs/api.log`

**2. ChromaDB Connection Failed**:
- Check ChromaDB is running
- Verify port 8002 is available
- Re-seed vector store: `python scripts/seed_vector_store.py`

**3. Agent Not Starting**:
- Check API health: `curl http://localhost:8001/health`
- Verify agent manager is initialized
- Check for errors in logs

**4. UI Not Loading**:
- Check Streamlit is running on port 8516
- Clear browser cache
- Check console for errors

### Logging

**Enable Debug Logging**:
```python
# services/api/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**View Logs**:
```bash
# API logs
tail -f logs/api.log

# Streamlit logs
tail -f logs/ui.log
```

### LangSmith Tracing

**Enable Tracing**:
```bash
# .env
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=ai-trip-agent
```

**View Traces**:
- Go to https://smith.langchain.com
- Select project "ai-trip-agent"
- View all LLM calls, latency, costs

---

## 📚 Documentation Files

**Read these for context**:

1. **README.md** - Project overview, setup instructions
2. **QUICKSTART.md** - Quick start guide
3. **V2.2_IMPLEMENTATION_SUMMARY.md** - Latest features (v2.2)
4. **V2.1_IMPLEMENTATION_SUMMARY.md** - Action features (v2.1)
5. **REALTIME_AGENT_GUIDE.md** - Real-time agent system
6. **ACTION_FEATURES_GUIDE.md** - Action buttons guide
7. **QUICK_REFERENCE.md** - Quick reference card
8. **DEPLOYMENT.md** - Deployment instructions

---

## 🎯 Current State (v2.2)

### What's Working

✅ **Core Trip Planning**:
- Multi-agent workflow
- 10 personas, 9 transport modes
- Carbon footprint tracking
- Green alternatives

✅ **Real-Time Monitoring**:
- Background agent monitoring
- 6 action buttons
- Real-time updates
- Agent lifecycle management

✅ **Date/Time & Round Trip**:
- Date/time pickers
- Round trip support
- Validation logic

✅ **Observability**:
- System health dashboard
- Agent monitoring
- LangSmith integration
- Auto-refresh

✅ **UI/UX**:
- Dark/Light themes
- Fixed all visibility issues
- Multi-page navigation
- Professional design

### Known Limitations

⚠️ **Simulated Data**:
- Weather checks are simulated
- News checks are simulated
- Traffic updates are simulated
- Security checks are simulated

⚠️ **LangSmith**:
- Requires API key for full features
- Trace viewing in dashboard not implemented

⚠️ **System Metrics**:
- Request statistics not implemented
- Resource usage not tracked

---

## 🚀 Future Enhancements

### Planned for v2.3

1. **Real API Integrations**:
   - OpenWeatherMap for weather
   - Google Maps for traffic
   - NewsAPI for news
   - Government APIs for security

2. **Advanced Observability**:
   - Real-time metrics graphs
   - Historical data
   - Performance trends
   - Alert system

3. **Enhanced Features**:
   - Multi-leg trips
   - Flexible dates
   - Booking integration
   - Payment processing

---

## 💡 Tips for Working on This Project

### Understanding the Flow

1. **User makes request** → Streamlit UI
2. **UI calls API** → FastAPI backend
3. **API invokes LangGraph** → Agent workflow
4. **Agents process** → Planner → Knowledge → Itinerary → Carbon
5. **Results returned** → API → UI
6. **If real-time enabled** → Agent created and monitored

### Key Files to Understand

**Start here**:
1. `agents/state.py` - Understand the state schema
2. `agents/graph.py` - Understand the workflow
3. `services/api/main.py` - Understand the API
4. `ui/streamlit_app.py` - Understand the UI

**Then explore**:
5. `agents/planner.py` - Trip planning logic
6. `agents/realtime_agent.py` - Monitoring logic
7. `pages/1_📊_Observability.py` - Dashboard

### Making Changes

**Always**:
1. Update state schema if adding fields
2. Update API models
3. Update UI
4. Add tests
5. Update documentation

**Never**:
1. Break backward compatibility
2. Remove existing features
3. Change API contracts without versioning
4. Skip testing

### Testing Strategy

1. **Unit tests** - Test individual functions
2. **Integration tests** - Test API endpoints
3. **E2E tests** - Test full workflow
4. **Manual tests** - Test UI interactions

---

## 🔐 Security Considerations

1. **API Keys**: Never commit to git
2. **CORS**: Configured for localhost only
3. **Input Validation**: All inputs validated
4. **Error Handling**: No sensitive data in errors
5. **Rate Limiting**: Not implemented (add if needed)

---

## 📊 Performance Considerations

**Current Performance**:
- Trip planning: 8-15 seconds
- Agent actions: 1-3 seconds
- Observability load: 0.5-1 second
- Memory per agent: ~5MB

**Optimization Tips**:
- Cache vector store queries
- Batch LLM calls
- Use async where possible
- Implement request queuing

---

## 🎓 Learning Resources

**LangChain/LangGraph**:
- https://python.langchain.com/docs/
- https://langchain-ai.github.io/langgraph/

**FastAPI**:
- https://fastapi.tiangolo.com/

**Streamlit**:
- https://docs.streamlit.io/

**ChromaDB**:
- https://docs.trychroma.com/

---

## 📞 Getting Help

**When stuck**:
1. Check documentation files
2. Review test files for examples
3. Check logs for errors
4. Use LangSmith for tracing
5. Test individual components

**Common Commands**:
```bash
# Health check
curl http://localhost:8001/health

# List agents
curl http://localhost:8001/agents

# Run tests
python scripts/test_v2.2_features.py

# View logs
tail -f logs/api.log
```

---

## ✅ Checklist for New Features

- [ ] Update state schema
- [ ] Update API models
- [ ] Update UI components
- [ ] Add backend logic
- [ ] Write tests
- [ ] Update documentation
- [ ] Test manually
- [ ] Check light/dark themes
- [ ] Verify backward compatibility
- [ ] Update version number

---

## 🎯 Project Goals

**Primary Goals**:
1. ✅ Provide intelligent trip planning for Assam
2. ✅ Track and minimize carbon footprint
3. ✅ Real-time monitoring during trips
4. ✅ Professional, user-friendly interface
5. ✅ Production-ready code quality

**Secondary Goals**:
1. ⏳ Real API integrations
2. ⏳ Advanced analytics
3. ⏳ Booking integration
4. ⏳ Mobile app

---

## 🏆 Success Metrics

**Current Status**:
- ✅ 100% test pass rate
- ✅ All features working
- ✅ Production-ready code
- ✅ Comprehensive documentation
- ✅ Clean architecture
- ✅ Extensible design

---

**Remember**: This is a production-ready application. Maintain code quality, test thoroughly, and document everything. The codebase is well-structured and follows best practices - keep it that way!

**Version**: 2.2.0  
**Last Updated**: October 2025  
**Status**: Production Ready

**Happy Coding! 🚀**
