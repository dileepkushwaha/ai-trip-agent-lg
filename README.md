# 🧠 AI Trip Agent - Proof of Concept (PoC)

An intelligent, sustainable, and hyperlocal **travel planning assistant** for **Assam, India**, powered by cutting-edge AI agent technology.

## 🌟 Features

- 🤖 **Multi-Agent System** - LangGraph-based orchestration with specialized agents
- 🧩 **Multi-LLM Support** - Works with LM Studio, OpenAI, Claude, Azure, and Ollama
- 💾 **RAG System** - ChromaDB vector store for local knowledge retrieval
- ♻️ **Carbon Tracking** - GHG Protocol compliant emission calculations with persistent tracking
- 📅 **Timeline-Based Itinerary** - Detailed day-by-day schedules with time slots and images
- 💰 **Budget Breakdown** - Comprehensive cost analysis for accommodations, activities, and transport
- 🌍 **Interactive UI** - Streamlit-based conversational interface with observability dashboard
- 📊 **Experiment Tracking** - LangSmith integration for debugging and monitoring
- 🔧 **LangChain CLI** - Integrated CLI for chain management and deployment
- 🐳 **Cloud-Ready** - Docker Compose for easy deployment
- 🔒 **DevSecOps** - Modular, secure, and scalable architecture

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI (Port 8516)               │
│                  Interactive Chat Interface                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend (Port 8001)                │
│              Orchestration & API Gateway                     │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│  LangGraph   │  │  ChromaDB   │  │   Carbon   │
│   Agents     │  │ Vector Store│  │ Calculator │
│              │  │ (Port 8002) │  │            │
└──────┬───────┘  └─────────────┘  └────────────┘
       │
       ├─ Planner Agent (Intent & Requirements)
       ├─ Knowledge Agent (RAG Retrieval)
       ├─ Itinerary Agent (Trip Planning)
       └─ Carbon Agent (Emissions & Alternatives)
```

---

## 📁 Project Structure

```
ai-trip-agent/
├── agents/                    # LangGraph AI agents
│   ├── __init__.py
│   ├── state.py              # Shared agent state with timeline & budget
│   ├── graph.py              # LangGraph workflow
│   ├── planner.py            # Trip planning agent
│   ├── knowledge.py          # RAG retrieval agent
│   ├── itinerary.py          # Itinerary generation with timeline & budget
│   ├── carbon.py             # Carbon calculation agent
│   └── realtime_agent.py     # Real-time monitoring agent
│
├── config/                    # Configuration management
│   ├── __init__.py
│   ├── settings.py           # Pydantic settings
│   └── llm_adapter.py        # Multi-LLM adapter
│
├── services/                  # Core services
│   ├── api/
│   │   └── main.py           # FastAPI application with carbon endpoints
│   ├── rag/
│   │   ├── embeddings.py     # Embedding manager
│   │   └── vector_store.py   # ChromaDB manager
│   └── carbon/
│       ├── calculator.py     # Carbon footprint calculator
│       └── tracker.py        # Persistent carbon tracking
│
├── ui/
│   ├── streamlit_app.py      # Main Streamlit interface
│   └── pages/
│       └── 1_📊_Observability.py  # Dashboard with carbon tracking
│
├── data/
│   ├── seed/                 # Sample travel data with images & pricing
│   │   ├── kaziranga.md
│   │   ├── majuli.md
│   │   └── guwahati.md
│   └── carbon_tracking.json  # Persistent carbon footprint data
│
├── scripts/
│   ├── seed_vector_store.py  # Data seeding script
│   └── test_system.py        # System validation
│
├── tests/                     # Test suite
│
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── langchain.toml            # LangChain CLI configuration
├── docker-compose.yml        # Container orchestration
├── Dockerfile.api            # API container
├── Dockerfile.ui             # UI container
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **LM Studio** (for local LLM) or API keys for OpenAI/Claude
- **8GB+ RAM** recommended

### 1. Clone and Setup

```bash
# Clone the repository
cd ~/workspace/poc/ai-trip-agent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Minimal configuration for local setup:**

```bash
# Use LM Studio (local, no API key needed)
LLM_PROVIDER=lmstudio
LMSTUDIO_API_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL=llama-3.2-1b-instruct

# Use HuggingFace embeddings (local, no API key needed)
EMBEDDING_PROVIDER=huggingface

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8002
```

### 3. Start ChromaDB

```bash
# Using Docker
docker run -d \
  --name ai-trip-agent-chroma \
  -p 8002:8000 \
  -v $(pwd)/chroma_data:/chroma/chroma \
  chromadb/chroma:latest

# Verify it's running
curl http://localhost:8002/api/v1/heartbeat
```

### 4. Start LM Studio

1. Open **LM Studio**
2. Download model: `llama-3.2-1b-instruct` (or any compatible model)
3. Start local server on `http://127.0.0.1:1234`
4. Test: `curl http://127.0.0.1:1234/v1/models`

### 5. Seed Vector Database

```bash
# Load travel knowledge into ChromaDB
python scripts/seed_vector_store.py --reset

# This will:
# - Load markdown files from data/seed/
# - Create embeddings
# - Store in ChromaDB
```

### 6. Test the System

```bash
# Run comprehensive system tests
python scripts/test_system.py

# Should show all tests passing ✅
```

### 7. Start the Application

**Option A: Run services separately (Development)**

```bash
# Terminal 1: Start FastAPI backend
uvicorn services.api.main:app --reload --port 8001

# Terminal 2: Start Streamlit UI
streamlit run ui/streamlit_app.py --server.port 8516
```

**Option B: Use Docker Compose (Production-like)**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 8. Access the Application

- **Streamlit UI**: http://localhost:8516
- **FastAPI Docs**: http://localhost:8001/docs
- **ChromaDB**: http://localhost:8002

---

## 🎯 Usage Examples

### Example Queries

Try these in the Streamlit interface:

```
1. "Plan a 3-day trip to Kaziranga for wildlife enthusiasts"
2. "I want to visit Majuli island for 2 days with my family"
3. "Suggest a weekend getaway near Guwahati for students"
4. "Plan a 5-day cultural tour of Assam"
5. "Budget-friendly trip to Kaziranga with carbon footprint analysis"
```

### API Usage

```python
import requests

response = requests.post(
    "http://localhost:8001/plan-trip",
    json={
        "query": "Plan a 3-day trip to Kaziranga",
        "transport_mode": "car_petrol"
    }
)

result = response.json()
print(result["itinerary"])
print(result["carbon_emissions"])
```

---

## 🔧 Configuration

### LLM Providers

#### LM Studio (Local - Default)
```bash
LLM_PROVIDER=lmstudio
LMSTUDIO_API_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL=llama-3.2-1b-instruct
```

#### OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=ssk-proj-Fzr0xBPq_uJQvdk4yXQ04Y7E6kgBe3zDoaV7oe5J-Yf726829USWiBwhgDGtMhS4_i64VroQR5T3BlbkFJSovRzxKmlvZC5LdZP7K-dgI4A-MwiT8f5PM1rslexRqRLOGMsJ2uyZlx5OCF0j10KV2HwqxcsA
OPENAI_MODEL=gpt-5.2
```

#### Anthropic Claude
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

#### Azure OpenAI
```bash
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment
```

#### Ollama (Local Alternative)
```bash
LLM_PROVIDER=ollama
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### LangSmith Integration (Optional)

Enable experiment tracking and debugging:

```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=ai-trip-agent-poc
```

Get your API key from: https://smith.langchain.com/

---

## 📊 Agent Workflow

The system uses **LangGraph** to orchestrate multiple specialized agents:

```
User Query
    ↓
┌─────────────────┐
│ Planner Agent   │ → Extracts: destination, duration, budget, interests
└────────┬────────┘
         ↓
┌─────────────────┐
│ Knowledge Agent │ → Retrieves: relevant docs from ChromaDB (RAG)
└────────┬────────┘
         ↓
┌─────────────────┐
│ Itinerary Agent │ → Generates: timeline with images & budget breakdown
└────────┬────────┘
         ↓
┌─────────────────┐
│ Carbon Agent    │ → Calculates: emissions & tracks cumulative footprint
└────────┬────────┘
         ↓
    Final Response
```

Each agent:
- Has a specific responsibility
- Updates shared state
- Can be tested independently
- Supports error recovery

---

## 🆕 New Features

### Timeline-Based Itinerary

The itinerary agent now generates structured timelines with:
- **Time slots** for each activity (e.g., "09:00 AM - 11:00 AM")
- **Activity details** with descriptions
- **Image URLs** for visual representation
- **Location information** for each activity

Example timeline structure:
```json
{
  "day": 1,
  "date": "2024-01-15",
  "activities": [
    {
      "time": "09:00 AM - 11:00 AM",
      "activity": "Jeep Safari",
      "description": "Morning wildlife safari",
      "location": "Kaziranga National Park",
      "image_url": "https://example.com/safari.jpg"
    }
  ]
}
```

### Budget Breakdown

Comprehensive cost analysis including:
- **Accommodation costs** per night
- **Activity costs** for each experience
- **Transport costs** (local and inter-city)
- **Food costs** (meals and snacks)
- **Total estimated cost** with breakdown

Example budget structure:
```json
{
  "accommodation": {"cost": 3000, "details": "Hotel per night"},
  "activities": {"cost": 2500, "details": "Safari and boat rides"},
  "transport": {"cost": 1500, "details": "Local transport"},
  "food": {"cost": 2000, "details": "Meals for 2 days"},
  "total": 9000,
  "currency": "INR"
}
```

### Persistent Carbon Tracking

Track your environmental impact across all trips:
- **Cumulative emissions** in kg CO₂e
- **Trip history** with details
- **Average emissions** per trip
- **Trees needed** to offset emissions
- **Reset functionality** to start fresh

Access carbon tracking via:
- **Dashboard**: View stats in the Observability page
- **API**: `/carbon/stats` and `/carbon/reset` endpoints

### LangChain CLI Integration

Use LangChain CLI for advanced operations:

```bash
# Install dependencies
pip install -r requirements.txt

# View available chains
langchain list

# Serve the agent graph
langchain serve

# Test individual agents
langchain run trip_planning --input "Plan a trip to Kaziranga"
```

Configuration is available in `langchain.toml`.

---

## 🌱 Carbon Footprint Calculation

Based on **GHG Protocol** and **SBTi** standards:

### Emission Factors (kg CO2e per km per passenger)

| Transport Mode | Emission Factor |
|----------------|-----------------|
| Petrol Car     | 0.192          |
| Diesel Car     | 0.171          |
| Electric Car   | 0.053          |
| Bus            | 0.089          |
| Train          | 0.041          |
| Motorcycle     | 0.113          |
| Bicycle        | 0.000          |
| Walking        | 0.000          |

### Features

- ✅ Real-time emission calculation
- ✅ Green alternative suggestions
- ✅ Tree offset equivalents
- ✅ Savings percentage comparison

---

## 🧪 Testing

### Run All Tests

```bash
python scripts/test_system.py
```

### Individual Component Tests

```bash
# Test LLM connection
python -c "from config.llm_adapter import LLMAdapter; from config import get_settings; llm = LLMAdapter(get_settings()).get_llm(); print(llm.invoke('Hello'))"

# Test vector store
python -c "from services.rag.vector_store import VectorStoreManager; from services.rag.embeddings import EmbeddingManager; from config import get_settings; s = get_settings(); vm = VectorStoreManager(s, EmbeddingManager(s)); print(vm.get_collection_stats())"

# Test carbon calculator
python -c "from services.carbon import CarbonCalculator, TransportMode; c = CarbonCalculator(); print(c.calculate(200, TransportMode.CAR_PETROL))"
```

---

## 🐳 Docker Deployment

### Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f ui

# Restart a service
docker-compose restart api

# Stop all services
docker-compose down
```

### Cloud Deployment

The system is designed to be cloud-agnostic and can be deployed on:

- **AWS**: ECS, EKS, or EC2
- **GCP**: Cloud Run, GKE, or Compute Engine
- **Azure**: Container Instances, AKS, or VMs

#### Deployment Checklist

1. ✅ Set environment variables in cloud provider
2. ✅ Configure static IP or domain name
3. ✅ Set up SSL/TLS certificates
4. ✅ Configure firewall rules (ports 8001, 8516, 8002)
5. ✅ Set up persistent volumes for ChromaDB
6. ✅ Configure logging and monitoring
7. ✅ Set up backup strategy for vector store

#### Example: AWS EC2 Deployment

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-static-ip

# Clone repository
git clone <your-repo-url>
cd ai-trip-agent

# Set up environment
cp .env.example .env
nano .env  # Configure for production

# Start with Docker Compose
docker-compose up -d

# Configure nginx reverse proxy (optional)
sudo apt install nginx
# Configure nginx to proxy to ports 8001 and 8516
```

---

## 📚 Adding New Data

### Add Travel Destinations

1. Create markdown file in `data/seed/`:

```markdown
# Your Destination

## Overview
Description of the place...

## Best Time to Visit
- Season information

## How to Reach
- Transportation details

## Attractions
- List of places to visit
```

2. Re-seed the vector store:

```bash
python scripts/seed_vector_store.py --reset
```

### Supported Formats

- Markdown (`.md`)
- Plain text (`.txt`)
- PDF (`.pdf`) - requires pypdf

---

## 🔍 Debugging with LangSmith

Enable LangSmith tracing to debug agent workflows:

1. Get API key from https://smith.langchain.com/
2. Update `.env`:
   ```bash
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=your-key
   LANGSMITH_PROJECT=ai-trip-agent-poc
   ```
3. Run your queries
4. View traces in LangSmith dashboard

### What You Can See

- Agent execution flow
- LLM prompts and responses
- Retrieval results
- Execution time per agent
- Error traces

---

## 🛠️ Development

### Project Guidelines

- **Modularity**: Each agent and service is independent
- **Type Safety**: Use Pydantic models for validation
- **Error Handling**: Graceful degradation
- **Logging**: Comprehensive logging at INFO level
- **Testing**: Test each component independently
- **Documentation**: Docstrings for all functions

### Adding a New Agent

1. Create agent file in `agents/`:

```python
from agents.state import AgentState
from typing import Dict, Any

class MyAgent:
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        # Your logic here
        return {
            "next_agent": "next_agent_name",
            "should_continue": True,
        }
```

2. Register in `agents/graph.py`:

```python
my_agent = MyAgent()
workflow.add_node("my_agent", my_agent)
```

3. Update routing logic

---

## 🐛 Troubleshooting

### ChromaDB Connection Failed

```bash
# Check if ChromaDB is running
docker ps | grep chroma

# Restart ChromaDB
docker restart ai-trip-agent-chroma

# Check logs
docker logs ai-trip-agent-chroma
```

### LM Studio Not Responding

```bash
# Test LM Studio API
curl http://127.0.0.1:1234/v1/models

# Restart LM Studio
# Make sure the server is started in LM Studio UI
```

### Vector Store Empty

```bash
# Re-seed the database
python scripts/seed_vector_store.py --reset

# Check collection stats
python -c "from services.rag.vector_store import VectorStoreManager; from services.rag.embeddings import EmbeddingManager; from config import get_settings; s = get_settings(); vm = VectorStoreManager(s, EmbeddingManager(s)); print(vm.get_collection_stats())"
```

### Port Already in Use

```bash
# Find and kill process on port 8001
lsof -ti:8001 | xargs kill -9

# Or use different port
uvicorn services.api.main:app --port 8003
```

---

## 📈 Performance Optimization

### For Local Development

- Use smaller LLM models (1B-3B parameters)
- Reduce `RAG_TOP_K` to 3
- Use HuggingFace embeddings (local)
- Limit `LLM_MAX_TOKENS` to 1024

### For Production

- Use larger models (7B+ parameters) or cloud APIs
- Increase `RAG_TOP_K` to 5-10
- Use OpenAI embeddings for better quality
- Enable caching for embeddings
- Use GPU for local LLMs

---

## 🤝 Contributing

This is a PoC project. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

This project is for educational and proof-of-concept purposes.

---

## 🙏 Acknowledgments

- **LangChain & LangGraph** - Agent orchestration
- **ChromaDB** - Vector database
- **FastAPI** - Modern Python web framework
- **Streamlit** - Rapid UI development
- **Assam Tourism** - Travel information

---

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Run `python scripts/test_system.py`
3. Check logs: `docker-compose logs`
4. Review LangSmith traces (if enabled)

---

## 🗺️ Roadmap

- [ ] Weather API integration
- [ ] Real-time traffic data
- [ ] Hotel booking integration
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Voice interface
- [ ] Offline mode
- [ ] Advanced analytics dashboard

---

**Built with ❤️ for sustainable and intelligent travel planning in Assam**
