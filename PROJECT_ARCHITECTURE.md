# 🏗️ AI Trip Agent - Project Architecture

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Agent System](#agent-system)
6. [API Endpoints](#api-endpoints)
7. [Configuration](#configuration)
8. [Modification Guide](#modification-guide)
9. [Best Practices](#best-practices)

---

## Overview

The AI Trip Agent is a multi-agent system built with LangGraph and LangChain that provides intelligent travel planning for Assam, India. The system combines RAG (Retrieval-Augmented Generation), carbon footprint tracking, and multi-LLM support to deliver comprehensive trip planning with environmental awareness.

### Key Technologies
- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: LLM abstraction and chain management
- **FastAPI**: REST API backend
- **Streamlit**: Interactive web UI
- **ChromaDB**: Vector database for RAG
- **Sentence Transformers**: Text embeddings
- **Pydantic**: Data validation and settings management

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  Streamlit Chat UI   │    │ Observability Dashboard│     │
│  │   (Port 8516)        │    │  (Carbon Tracking)     │     │
│  └──────────┬───────────┘    └──────────┬─────────────┘     │
└─────────────┼──────────────────────────┼───────────────────┘
              │                           │
              │         HTTP/REST         │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           FastAPI Backend (Port 8001)                │   │
│  │  - Trip Planning Endpoint                            │   │
│  │  - Carbon Tracking Endpoints                         │   │
│  │  - Agent Management                                  │   │
│  │  - Vector Store Management                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────┬───────────────────────────────────────────────┘
              │
    ┌─────────┼─────────┬─────────────┬──────────────┐
    │         │         │             │              │
    ▼         ▼         ▼             ▼              ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│LangGraph│ │ChromaDB│ │  Carbon  │ │   LLM    │ │ Carbon   │
│ Agents  │ │Vector  │ │Calculator│ │ Adapter  │ │ Tracker  │
│         │ │Store   │ │          │ │          │ │          │
└────────┘ └────────┘ └──────────┘ └──────────┘ └──────────┘
```

### Component Interaction

```
┌──────────────┐
│ User Request │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    Agent Graph                            │
│                                                           │
│  ┌──────────────┐                                        │
│  │Planner Agent │ → Extract requirements                 │
│  └──────┬───────┘                                        │
│         │                                                 │
│         ▼                                                 │
│  ┌──────────────┐                                        │
│  │Knowledge     │ → Query ChromaDB (RAG)                 │
│  │Agent         │   Retrieve relevant documents          │
│  └──────┬───────┘                                        │
│         │                                                 │
│         ▼                                                 │
│  ┌──────────────┐                                        │
│  │Itinerary     │ → Generate timeline & budget           │
│  │Agent         │   Create structured itinerary          │
│  └──────┬───────┘                                        │
│         │                                                 │
│         ▼                                                 │
│  ┌──────────────┐                                        │
│  │Carbon Agent  │ → Calculate emissions                  │
│  │              │   Track cumulative footprint           │
│  └──────┬───────┘   Suggest alternatives                 │
│         │                                                 │
└─────────┼─────────────────────────────────────────────────┘
          │
          ▼
    ┌──────────────┐
    │Final Response│
    └──────────────┘
```

---

## Component Details

### 1. Agents (`agents/`)

#### State Management (`state.py`)
Defines the shared state structure used across all agents:

```python
class AgentState(TypedDict):
    # User input
    query: str
    destination: Optional[str]
    duration: Optional[int]
    budget: Optional[float]
    interests: List[str]
    transport_mode: Optional[str]
    
    # Agent outputs
    itinerary: Optional[Dict[str, Any]]
    timeline: List[Dict[str, Any]]  # NEW: Timeline with images
    budget_breakdown: Optional[Dict[str, Any]]  # NEW: Budget details
    carbon_emissions: Optional[Dict[str, Any]]
    cumulative_carbon_footprint: Optional[float]  # NEW: Persistent tracking
    
    # System
    messages: List[BaseMessage]
    retrieved_docs: List[Document]
    error: Optional[str]
    next_agent: Optional[str]
    should_continue: bool
```

#### Planner Agent (`planner.py`)
**Purpose**: Extract trip requirements from user query

**Responsibilities**:
- Parse natural language queries
- Extract destination, duration, budget, interests
- Validate and normalize inputs
- Set initial state

**Key Methods**:
- `__call__(state: AgentState) -> Dict[str, Any]`
- `_extract_requirements(query: str) -> Dict`

#### Knowledge Agent (`knowledge.py`)
**Purpose**: Retrieve relevant information using RAG

**Responsibilities**:
- Query ChromaDB vector store
- Retrieve relevant documents
- Rank and filter results
- Add context to state

**Key Methods**:
- `__call__(state: AgentState) -> Dict[str, Any]`
- `_retrieve_documents(query: str, k: int) -> List[Document]`

#### Itinerary Agent (`itinerary.py`)
**Purpose**: Generate detailed trip itinerary

**Responsibilities**:
- Create day-by-day timeline
- Generate time-slotted activities
- Calculate budget breakdown
- Add images and locations
- Format structured output

**Key Methods**:
- `__call__(state: AgentState) -> Dict[str, Any]`
- `_generate_timeline_and_budget(state: AgentState) -> tuple`
- `_create_fallback_timeline(state: AgentState) -> List[Dict]`

**Output Structure**:
```json
{
  "timeline": [
    {
      "day": 1,
      "date": "2024-01-15",
      "activities": [
        {
          "time": "09:00 AM - 11:00 AM",
          "activity": "Activity Name",
          "description": "Details",
          "location": "Place",
          "image_url": "https://..."
        }
      ]
    }
  ],
  "budget_breakdown": {
    "accommodation": {"cost": 3000, "details": "..."},
    "activities": {"cost": 2500, "details": "..."},
    "transport": {"cost": 1500, "details": "..."},
    "food": {"cost": 2000, "details": "..."},
    "total": 9000,
    "currency": "INR"
  }
}
```

#### Carbon Agent (`carbon.py`)
**Purpose**: Calculate and track carbon footprint

**Responsibilities**:
- Calculate trip emissions
- Track cumulative footprint
- Suggest green alternatives
- Persist tracking data

**Key Methods**:
- `__call__(state: AgentState) -> Dict[str, Any]`
- `_estimate_distance(destination: str) -> float`
- `_format_carbon_message(result, alternatives, cumulative) -> str`

**Emission Factors** (kg CO₂e per km):
- Car (Petrol): 0.192
- Car (Diesel): 0.171
- Bus: 0.089
- Train: 0.041
- Flight: 0.255
- Electric Vehicle: 0.053

#### Realtime Agent (`realtime_agent.py`)
**Purpose**: Monitor and manage long-running agent tasks

**Responsibilities**:
- Track agent execution status
- Provide real-time updates
- Handle agent lifecycle
- Clean up old agents

---

### 2. Services (`services/`)

#### API Service (`services/api/main.py`)

**Endpoints**:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/plan-trip` | Plan a trip |
| POST | `/plan-trip-async` | Async trip planning |
| GET | `/agent/{agent_id}/status` | Get agent status |
| POST | `/agent/{agent_id}/stop` | Stop agent |
| GET | `/agents` | List all agents |
| POST | `/agents/cleanup` | Cleanup old agents |
| GET | `/carbon/stats` | Get carbon statistics |
| POST | `/carbon/reset` | Reset carbon tracking |
| GET | `/vector-store/stats` | Vector store statistics |
| POST | `/vector-store/seed` | Seed vector store |

**Request/Response Models**:

```python
class TripRequest(BaseModel):
    query: str
    destination: Optional[str] = None
    duration: Optional[int] = None
    budget: Optional[float] = None
    interests: List[str] = []
    transport_mode: Optional[str] = "car_petrol"

class TripResponse(BaseModel):
    success: bool
    itinerary: Optional[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    budget_breakdown: Optional[Dict[str, Any]]
    carbon_emissions: Optional[Dict[str, Any]]
    cumulative_carbon_footprint: Optional[float]
    messages: List[str]
    error: Optional[str]
```

#### RAG Service (`services/rag/`)

**Embeddings Manager** (`embeddings.py`):
- Manages sentence-transformers models
- Generates text embeddings
- Supports multiple embedding models

**Vector Store Manager** (`vector_store.py`):
- ChromaDB client management
- Document ingestion
- Similarity search
- Collection management

**Key Methods**:
```python
class VectorStoreManager:
    def add_documents(self, documents: List[Document])
    def similarity_search(self, query: str, k: int) -> List[Document]
    def get_stats() -> Dict[str, Any]
```

#### Carbon Service (`services/carbon/`)

**Calculator** (`calculator.py`):
- Emission calculations
- Transport mode comparisons
- Green alternatives

**Tracker** (`tracker.py`):
- Persistent storage (JSON)
- Trip history
- Statistics aggregation
- Reset functionality

```python
class CarbonTracker:
    def add_trip(self, carbon_kg: float, trip_details: Dict)
    def get_total_carbon() -> float
    def get_stats() -> Dict[str, Any]
    def reset()
```

---

### 3. Configuration (`config/`)

#### Settings (`settings.py`)
Pydantic-based configuration management:

```python
class Settings(BaseSettings):
    # App
    app_name: str
    app_version: str
    debug: bool
    
    # API
    api_host: str
    api_port: int
    
    # LLM
    llm_provider: LLMProvider
    llm_temperature: float
    llm_max_tokens: int
    
    # ChromaDB
    chroma_host: str
    chroma_port: int
    
    # Carbon
    carbon_default_emission_factor: float
    
    # LangSmith
    langsmith_tracing: bool
    langsmith_api_key: Optional[str]
```

#### LLM Adapter (`llm_adapter.py`)
Multi-provider LLM abstraction:

**Supported Providers**:
- LM Studio (local)
- OpenAI
- Anthropic Claude
- Azure OpenAI
- Ollama

```python
class LLMAdapter:
    def get_llm(self) -> BaseChatModel
    def _create_lm_studio_llm() -> ChatOpenAI
    def _create_openai_llm() -> ChatOpenAI
    def _create_anthropic_llm() -> ChatAnthropic
    def _create_azure_llm() -> AzureChatOpenAI
    def _create_ollama_llm() -> ChatOllama
```

---

### 4. UI (`ui/`)

#### Main App (`streamlit_app.py`)
- Chat interface
- Trip planning form
- Response display
- Session management

#### Observability Dashboard (`pages/1_📊_Observability.py`)
- System health metrics
- Carbon footprint tracking
- Active agents monitoring
- Vector store statistics

**Features**:
- Real-time metrics
- Carbon statistics with reset
- Recent trips display
- Agent status tracking

---

## Data Flow

### Trip Planning Flow

```
1. User Input
   ↓
2. API Request (POST /plan-trip)
   ↓
3. Agent Graph Execution
   │
   ├─→ Planner Agent
   │   └─→ Extract: destination, duration, budget, interests
   │
   ├─→ Knowledge Agent
   │   └─→ Query ChromaDB
   │       └─→ Retrieve relevant documents
   │
   ├─→ Itinerary Agent
   │   └─→ Generate timeline with LLM
   │       ├─→ Parse JSON response
   │       ├─→ Create timeline structure
   │       └─→ Calculate budget breakdown
   │
   └─→ Carbon Agent
       └─→ Calculate emissions
           ├─→ Estimate distance
           ├─→ Apply emission factors
           ├─→ Track cumulative footprint
           └─→ Suggest alternatives
   ↓
4. Response Assembly
   ↓
5. UI Display
```

### Carbon Tracking Flow

```
1. Trip Completed
   ↓
2. Carbon Agent Calculates Emissions
   ↓
3. CarbonTracker.add_trip()
   ↓
4. Persist to data/carbon_tracking.json
   {
     "total_carbon_kg": 150.5,
     "trips": [
       {
         "carbon_kg": 45.2,
         "timestamp": "2024-01-15T10:30:00",
         "details": {...}
       }
     ]
   }
   ↓
5. Update Cumulative Total
   ↓
6. Display in Dashboard
```

---

## Modification Guide

### Adding a New Agent

1. **Create Agent File** (`agents/new_agent.py`):
```python
from typing import Dict, Any
from agents.state import AgentState

class NewAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        # Agent logic here
        return {
            "new_field": "value",
            "next_agent": "next_agent_name",
            "should_continue": True
        }
```

2. **Update State** (`agents/state.py`):
```python
class AgentState(TypedDict):
    # ... existing fields ...
    new_field: Optional[str]  # Add new field
```

3. **Register in Graph** (`agents/graph.py`):
```python
from agents.new_agent import NewAgent

def create_agent_graph(llm, vector_store, carbon_calculator):
    new_agent = NewAgent(llm)
    
    workflow.add_node("new_agent", new_agent)
    workflow.add_edge("previous_agent", "new_agent")
    workflow.add_edge("new_agent", "next_agent")
```

### Adding a New API Endpoint

1. **Define Models** (`services/api/main.py`):
```python
class NewRequest(BaseModel):
    field1: str
    field2: Optional[int] = None

class NewResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
```

2. **Create Endpoint**:
```python
@app.post("/new-endpoint", response_model=NewResponse)
async def new_endpoint(request: NewRequest):
    try:
        # Endpoint logic
        return NewResponse(success=True, data={})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Adding a New LLM Provider

1. **Update Enum** (`config/settings.py`):
```python
class LLMProvider(str, Enum):
    # ... existing providers ...
    NEW_PROVIDER = "new_provider"
```

2. **Add Configuration**:
```python
class Settings(BaseSettings):
    # ... existing settings ...
    new_provider_api_key: Optional[str] = None
    new_provider_model: str = "default-model"
```

3. **Implement Adapter** (`config/llm_adapter.py`):
```python
def _create_new_provider_llm(self) -> BaseChatModel:
    from langchain_newprovider import ChatNewProvider
    
    return ChatNewProvider(
        api_key=self.settings.new_provider_api_key,
        model=self.settings.new_provider_model,
        temperature=self.settings.llm_temperature
    )
```

4. **Update Factory Method**:
```python
def get_llm(self) -> BaseChatModel:
    if self.settings.llm_provider == LLMProvider.NEW_PROVIDER:
        return self._create_new_provider_llm()
    # ... existing providers ...
```

### Adding New Seed Data

1. **Create Markdown File** (`data/seed/new_place.md`):
```markdown
# New Place

## Overview
Description of the place...

## Attractions
- Attraction 1 (₹500) ![Image](https://example.com/image1.jpg)
- Attraction 2 (₹300) ![Image](https://example.com/image2.jpg)

## Accommodation
- Hotel Name (₹2000/night) ![Image](https://example.com/hotel.jpg)

## Transport
- Local transport: ₹500/day
```

2. **Seed Vector Store**:
```bash
python scripts/seed_vector_store.py
```

### Modifying Carbon Emission Factors

Edit `services/carbon/calculator.py`:

```python
class TransportMode(Enum):
    # ... existing modes ...
    NEW_MODE = "new_mode"

EMISSION_FACTORS = {
    # ... existing factors ...
    TransportMode.NEW_MODE: 0.XXX,  # kg CO2e per km
}
```

---

## Best Practices

### Code Organization
1. Keep agents focused on single responsibilities
2. Use type hints for all function signatures
3. Document complex logic with docstrings
4. Follow PEP 8 style guidelines

### Error Handling
```python
try:
    # Agent logic
    result = process_data(state)
    return {"data": result, "error": None}
except Exception as e:
    logger.error(f"Agent error: {e}", exc_info=True)
    return {"error": str(e), "should_continue": False}
```

### State Management
- Always return a dictionary from agents
- Include `next_agent` and `should_continue` keys
- Validate state before processing
- Use Optional types for nullable fields

### Testing
```python
def test_agent():
    agent = MyAgent(llm)
    state = AgentState(query="test", ...)
    result = agent(state)
    assert result["success"] == True
    assert "data" in result
```

### Performance
- Use async operations where possible
- Cache frequently accessed data
- Limit LLM token usage
- Implement request timeouts

### Security
- Never commit API keys
- Use environment variables
- Validate all user inputs
- Sanitize LLM outputs
- Implement rate limiting

---

## Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale api=3
```

### Environment Variables

Required for production:
```bash
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Database
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# Monitoring
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...

# Security
API_CORS_ORIGINS=["https://yourdomain.com"]
```

### Monitoring

1. **LangSmith**: Track agent executions
2. **FastAPI Docs**: Monitor API usage at `/docs`
3. **Observability Dashboard**: View system health
4. **Logs**: Check application logs for errors

---

## Troubleshooting

### Common Issues

**ChromaDB Connection Failed**:
```bash
# Check if ChromaDB is running
curl http://localhost:8002/api/v1/heartbeat

# Restart ChromaDB
docker-compose restart chromadb
```

**LLM Provider Errors**:
- Verify API keys in `.env`
- Check provider status
- Review rate limits
- Validate model names

**Agent Execution Timeout**:
- Increase timeout in settings
- Optimize LLM prompts
- Reduce max_tokens
- Check network connectivity

**Carbon Tracking Not Persisting**:
- Verify `data/` directory exists
- Check file permissions
- Review tracker logs

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following best practices
4. Add tests for new features
5. Update documentation
6. Submit pull request

---

## License

This project is a Proof of Concept (PoC) for educational purposes.

---

## Support

For issues and questions:
- Check documentation
- Review logs
- Test with minimal configuration
- Report bugs with detailed information
