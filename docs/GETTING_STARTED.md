# Getting Started Checklist

Use this checklist to set up and run the AI Trip Agent system.

## ☑️ Prerequisites

- [ ] Python 3.11 or higher installed
- [ ] Docker installed and running
- [ ] Git installed
- [ ] 8GB+ RAM available
- [ ] 10GB+ disk space available

## ☑️ Initial Setup

### 1. Clone and Environment Setup

- [ ] Clone the repository
  ```bash
  cd ~/workspace/poc/ai-trip-agent
  ```

- [ ] Create virtual environment
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  ```

- [ ] Install dependencies
  ```bash
  pip install -r requirements.txt
  ```

### 2. Configuration

- [ ] Copy environment template
  ```bash
  cp .env.example .env
  ```

- [ ] Choose your LLM provider and configure `.env`:

  **Option A: LM Studio (Local, Recommended for PoC)**
  - [ ] Set `LLM_PROVIDER=lmstudio`
  - [ ] Set `LMSTUDIO_API_URL=http://127.0.0.1:1234/v1`
  - [ ] Set `EMBEDDING_PROVIDER=huggingface`

  **Option B: OpenAI**
  - [ ] Set `LLM_PROVIDER=openai`
  - [ ] Set `OPENAI_API_KEY=your-key-here`
  - [ ] Set `EMBEDDING_PROVIDER=openai`

  **Option C: Anthropic Claude**
  - [ ] Set `LLM_PROVIDER=anthropic`
  - [ ] Set `ANTHROPIC_API_KEY=your-key-here`
  - [ ] Set `EMBEDDING_PROVIDER=huggingface`

### 3. Start ChromaDB

- [ ] Create data directory
  ```bash
  mkdir -p chroma_data
  ```

- [ ] Start ChromaDB container
  ```bash
  docker run -d \
    --name ai-trip-agent-chroma \
    -p 8002:8000 \
    -v $(pwd)/chroma_data:/chroma/chroma \
    chromadb/chroma:latest
  ```

- [ ] Verify ChromaDB is running
  ```bash
  curl http://localhost:8002/api/v1/heartbeat
  ```
  Expected: `{}`

### 4. LLM Setup

**If using LM Studio:**

- [ ] Download and install LM Studio from https://lmstudio.ai/
- [ ] Download a model (recommended: `llama-3.2-1b-instruct`)
- [ ] Start the local server in LM Studio
- [ ] Verify server is running
  ```bash
  curl http://127.0.0.1:1234/v1/models
  ```

**If using OpenAI/Claude:**

- [ ] Verify API key is set in `.env`
- [ ] Test API connection (will be tested in next step)

### 5. Seed Vector Database

- [ ] Load sample travel data
  ```bash
  python scripts/seed_vector_store.py --reset
  ```

- [ ] Verify data was loaded
  ```bash
  python -c "from config import get_settings; from services.rag.embeddings import EmbeddingManager; from services.rag.vector_store import VectorStoreManager; s = get_settings(); vm = VectorStoreManager(s, EmbeddingManager(s)); print(vm.get_collection_stats())"
  ```
  Expected: `{'name': 'assam_travel_knowledge', 'count': <number>}`

### 6. Run System Tests

- [ ] Run comprehensive tests
  ```bash
  python scripts/test_system.py
  ```

- [ ] Verify all tests pass ✅
  - Configuration
  - LLM Connection
  - Embeddings
  - Vector Store
  - Carbon Calculator
  - Agent Workflow

## ☑️ Running the Application

### Option A: Development Mode (Separate Terminals)

**Terminal 1: FastAPI Backend**

- [ ] Activate virtual environment
  ```bash
  source .venv/bin/activate
  ```

- [ ] Start FastAPI server
  ```bash
  uvicorn services.api.main:app --reload --port 8001
  ```

- [ ] Verify API is running
  ```bash
  curl http://localhost:8001/health
  ```

**Terminal 2: Streamlit UI**

- [ ] Activate virtual environment
  ```bash
  source .venv/bin/activate
  ```

- [ ] Start Streamlit
  ```bash
  streamlit run ui/streamlit_app.py --server.port 8516
  ```

- [ ] Open browser to http://localhost:8516

### Option B: Docker Compose (Production-like)

- [ ] Start all services
  ```bash
  docker-compose up -d
  ```

- [ ] Check service status
  ```bash
  docker-compose ps
  ```

- [ ] View logs
  ```bash
  docker-compose logs -f
  ```

- [ ] Open browser to http://localhost:8516

## ☑️ Testing the Application

### Basic Functionality

- [ ] Open Streamlit UI (http://localhost:8516)
- [ ] Verify API connection shows "✅ API Connected"
- [ ] Try example query: "Plan a 3-day trip to Kaziranga for wildlife enthusiasts"
- [ ] Verify you receive:
  - [ ] Trip itinerary
  - [ ] Carbon footprint calculation
  - [ ] Green alternatives

### API Testing

- [ ] Test health endpoint
  ```bash
  curl http://localhost:8001/health
  ```

- [ ] Test trip planning endpoint
  ```bash
  curl -X POST http://localhost:8001/plan-trip \
    -H "Content-Type: application/json" \
    -d '{"query": "Plan a 2-day trip to Majuli", "transport_mode": "car_petrol"}'
  ```

- [ ] Check API documentation at http://localhost:8001/docs

## ☑️ Optional: LangSmith Integration

- [ ] Sign up at https://smith.langchain.com/
- [ ] Get API key
- [ ] Update `.env`:
  ```bash
  LANGSMITH_TRACING=true
  LANGSMITH_API_KEY=your-key-here
  LANGSMITH_PROJECT=ai-trip-agent-poc
  ```
- [ ] Restart services
- [ ] Run a query
- [ ] View traces in LangSmith dashboard

## ☑️ Troubleshooting

If you encounter issues:

### ChromaDB Issues

- [ ] Check if container is running: `docker ps | grep chroma`
- [ ] Check logs: `docker logs ai-trip-agent-chroma`
- [ ] Restart: `docker restart ai-trip-agent-chroma`

### LM Studio Issues

- [ ] Verify server is started in LM Studio UI
- [ ] Check if model is loaded
- [ ] Test endpoint: `curl http://127.0.0.1:1234/v1/models`

### Vector Store Empty

- [ ] Re-run seeding: `python scripts/seed_vector_store.py --reset`
- [ ] Check data directory exists: `ls -la data/seed/`

### Port Conflicts

- [ ] Check if ports are in use:
  ```bash
  lsof -i :8001  # FastAPI
  lsof -i :8516  # Streamlit
  lsof -i :8002  # ChromaDB
  ```
- [ ] Kill processes if needed: `lsof -ti:8001 | xargs kill -9`

### Import Errors

- [ ] Verify virtual environment is activated
- [ ] Reinstall dependencies: `pip install -r requirements.txt`

## ☑️ Next Steps

After successful setup:

- [ ] Read the [README.md](README.md) for detailed documentation
- [ ] Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture overview
- [ ] Check [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment options
- [ ] Add your own travel data in `data/seed/`
- [ ] Customize agents in `agents/` directory
- [ ] Experiment with different LLM providers
- [ ] Set up monitoring with LangSmith

## ☑️ Production Deployment

When ready for production:

- [ ] Review security settings in `.env`
- [ ] Set up SSL/TLS certificates
- [ ] Configure domain name
- [ ] Set up monitoring and alerting
- [ ] Configure backups for ChromaDB
- [ ] Review [DEPLOYMENT.md](DEPLOYMENT.md)
- [ ] Test in staging environment first
- [ ] Set up CI/CD pipeline

## 🎉 Success Criteria

You're ready to use the system when:

- ✅ All system tests pass
- ✅ API health check returns 200
- ✅ Streamlit UI loads successfully
- ✅ You can plan a trip and get results
- ✅ Carbon calculations are displayed
- ✅ Vector store has documents

## 📞 Need Help?

- Check the troubleshooting section above
- Review logs: `docker-compose logs` or check terminal output
- Run system tests: `python scripts/test_system.py`
- Check API docs: http://localhost:8001/docs

---

**Estimated Setup Time**: 15-30 minutes (depending on download speeds)

**Recommended for First-Time Setup**: Use LM Studio with HuggingFace embeddings (fully local, no API keys needed)
