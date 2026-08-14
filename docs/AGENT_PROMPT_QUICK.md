# 🤖 AI Trip Agent - Quick Agent Prompt

## TL;DR

**Project**: AI Trip Agent v2.2 - Intelligent travel planning for Assam, India  
**Tech**: FastAPI + Streamlit + LangChain/LangGraph + ChromaDB + LM Studio  
**Status**: Production Ready (100% test coverage)

---

## 📁 Key Files

```
ui/streamlit_app.py          # Main UI (945 lines)
pages/1_📊_Observability.py  # Dashboard (450 lines)
agents/graph.py              # LangGraph workflow
agents/realtime_agent.py     # Real-time monitoring (443 lines)
agents/state.py              # State schema (CRITICAL)
services/api/main.py         # FastAPI backend (438 lines)
```

---

## 🎯 Core Features

1. **Trip Planning**: Multi-agent workflow, 10 personas, 9 transport modes, carbon tracking
2. **Real-Time Monitoring**: Background agents with 6 action buttons
3. **Date/Time & Round Trip**: Full scheduling support
4. **Observability**: System health, agent monitoring, LangSmith integration

---

## 🔑 State Schema (agents/state.py)

```python
class AgentState(TypedDict):
    # Core
    messages: List[BaseMessage]
    user_query: str
    intent: Optional[str]
    
    # Trip
    destination: Optional[str]
    duration_days: Optional[int]
    persona: Optional[str]
    transport_mode: Optional[str]
    stoppage_duration: Optional[str]
    
    # Date/Time (v2.2)
    travel_date: Optional[str]
    travel_time: Optional[str]
    is_round_trip: bool
    return_date: Optional[str]
    return_time: Optional[str]
    
    # Real-time
    enable_realtime_agent: bool
    agent_id: Optional[str]
    agent_updates: List[Dict]
    
    # Results
    itinerary: Optional[Dict]
    carbon_emissions: Optional[Dict]
```

---

## 🛠️ Quick Commands

```bash
# Start API
uvicorn services.api.main:app --port 8001 --reload

# Start UI
streamlit run ui/streamlit_app.py --server.port 8516

# Test
python scripts/test_v2.2_features.py

# Health check
curl http://localhost:8001/health
```

---

## 📝 Adding a Feature (4 Steps)

1. **Update State**: `agents/state.py` - Add field to `AgentState`
2. **Update API**: `services/api/main.py` - Add field to `TripRequest`
3. **Update UI**: `ui/streamlit_app.py` - Add input widget
4. **Test**: Create test in `scripts/test_*.py`

---

## 🔧 API Endpoints

```python
POST   /plan-trip              # Plan trip
GET    /health                 # Health check
GET    /agents                 # List agents
GET    /agent/{id}/status      # Agent status
POST   /agent/{id}/action      # Send action
POST   /agent/{id}/stop        # Stop agent
```

---

## 🎨 Agent Actions

```python
# agents/realtime_agent.py
actions = [
    "replan",          # Replan trip
    "delayed",         # Report delay
    "check_weather",   # Weather update
    "check_news",      # News update
    "security_check"   # Security check
]
```

---

## 🐛 Common Issues

**LLM not responding**: Check LM Studio running on port 1234  
**ChromaDB error**: Re-seed with `python scripts/seed_vector_store.py`  
**Agent not starting**: Check `/health` endpoint  
**UI not loading**: Clear cache, check port 8516

---

## 📚 Documentation

- `README.md` - Setup & overview
- `V2.2_IMPLEMENTATION_SUMMARY.md` - Latest features
- `AGENT_PROMPT.md` - Full agent prompt (this file's parent)
- `QUICK_REFERENCE.md` - Quick reference

---

## 🎯 Current Version (v2.2)

**Working**:
✅ Trip planning with 10 personas  
✅ Real-time monitoring with 6 actions  
✅ Date/time & round trip  
✅ Observability dashboard  
✅ Dark/Light themes  
✅ LangSmith integration

**Limitations**:
⚠️ Weather/news/traffic are simulated  
⚠️ No real API integrations yet  
⚠️ System metrics not tracked

---

## 💡 Key Principles

1. **Always update state schema first**
2. **Test everything**
3. **Maintain backward compatibility**
4. **Document all changes**
5. **Follow existing patterns**

---

## 🚀 Workflow

```
User Query → Streamlit UI → FastAPI → LangGraph → Agents → Response
                                          ↓
                                    Real-time Agent (optional)
```

---

## 📊 Performance

- Trip planning: 8-15s
- Agent actions: 1-3s
- Observability: <1s
- Memory/agent: ~5MB

---

## ✅ Before Committing

- [ ] Update state schema if needed
- [ ] Update API models
- [ ] Update UI
- [ ] Write/update tests
- [ ] Test light & dark themes
- [ ] Update documentation
- [ ] Run all tests
- [ ] Check for errors

---

**Version**: 2.2.0 | **Status**: Production Ready | **Tests**: 100% Pass

**Need more details?** Read `AGENT_PROMPT.md` (full version)
