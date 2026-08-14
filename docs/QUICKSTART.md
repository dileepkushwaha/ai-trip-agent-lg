# 🚀 Quick Start Guide

## ✅ Services are Running!

Both FastAPI and Streamlit are now running successfully!

### Access the Application

- **Streamlit UI**: http://localhost:8516
- **FastAPI Docs**: http://localhost:8001/docs
- **API Health Check**: http://localhost:8001/health

---

## 📊 Current Status

✅ **FastAPI Backend** - Running on port 8001
✅ **Streamlit UI** - Running on port 8516
✅ **ChromaDB** - Running on port 8002
✅ **LM Studio** - Connected and ready

---

## 🎯 Try These Example Queries

Open http://localhost:8516 and try:

1. **"Plan a 3-day trip to Kaziranga for wildlife enthusiasts"**
2. **"I want to visit Majuli island for 2 days with my family"**
3. **"Suggest a weekend getaway near Guwahati"**
4. **"Plan a 5-day cultural tour of Assam"**

---

## 🛠️ Managing Services

### Check Service Status

```bash
# Check if services are running
curl http://localhost:8001/health
curl http://localhost:8516

# Check ChromaDB
docker ps | grep chroma
```

### View Logs

```bash
# If using the start script
tail -f logs/api.log
tail -f logs/ui.log

# Or check terminal outputs directly
```

### Stop Services

```bash
# Find process IDs
ps aux | grep uvicorn
ps aux | grep streamlit

# Kill processes
kill <PID>

# Or use Ctrl+C in the terminals
```

### Restart Services

```bash
# Stop current services (Ctrl+C in terminals)

# Start again
# Terminal 1:
source .venv/bin/activate
uvicorn services.api.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2:
source .venv/bin/activate
streamlit run ui/streamlit_app.py --server.port 8516 --server.address 0.0.0.0
```

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port
lsof -ti:8001 | xargs kill -9  # FastAPI
lsof -ti:8516 | xargs kill -9  # Streamlit
```

### ChromaDB Not Responding

```bash
# Restart ChromaDB
docker restart ai-trip-agent-chroma

# Check logs
docker logs ai-trip-agent-chroma
```

### LM Studio Not Connected

```bash
# Test LM Studio
curl http://127.0.0.1:1234/v1/models

# Make sure LM Studio server is started
# and model is loaded
```

### Vector Store Empty

```bash
# Seed the database
source .venv/bin/activate
python scripts/seed_vector_store.py --reset
```

---

## 📝 Next Steps

### 1. Seed the Vector Store (If Not Done)

```bash
source .venv/bin/activate
python scripts/seed_vector_store.py --reset
```

This will load sample data about:
- Kaziranga National Park
- Majuli Island
- Guwahati City

### 2. Test the API

```bash
# Test trip planning
curl -X POST http://localhost:8001/plan-trip \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Plan a 2-day trip to Kaziranga",
    "transport_mode": "car_petrol"
  }'
```

### 3. Explore the UI

1. Open http://localhost:8516
2. Enter a trip planning query
3. Select transport mode
4. Click "Plan Trip"
5. View itinerary and carbon footprint

---

## 🎨 Features to Try

### In Streamlit UI:

- ✅ **Conversation History** - See all your queries
- ✅ **Transport Mode Selection** - Choose your travel method
- ✅ **Carbon Footprint** - View emissions and green alternatives
- ✅ **Detailed Itinerary** - Day-by-day trip plans
- ✅ **Real-time Responses** - Powered by LM Studio

### In FastAPI:

- ✅ **Interactive Docs** - http://localhost:8001/docs
- ✅ **Health Check** - http://localhost:8001/health
- ✅ **Vector Store Stats** - http://localhost:8001/vector-store/stats

---

## 📚 Documentation

- **README.md** - Complete setup and usage guide
- **GETTING_STARTED.md** - Step-by-step checklist
- **DEPLOYMENT.md** - Cloud deployment guide
- **PROJECT_SUMMARY.md** - Architecture overview

---

## 🔐 Configuration

Current configuration (from .env):

```bash
LLM_PROVIDER=lmstudio
LMSTUDIO_API_URL=http://127.0.0.1:1234/v1
EMBEDDING_PROVIDER=huggingface
CHROMA_HOST=localhost
CHROMA_PORT=8002
```

To change providers, edit `.env` and restart services.

---

## 🎉 Success!

Your AI Trip Agent is now running and ready to plan trips!

**What's Working:**
- ✅ FastAPI backend with LangGraph agents
- ✅ Streamlit interactive UI
- ✅ ChromaDB vector store
- ✅ LM Studio local LLM
- ✅ Multi-agent orchestration
- ✅ Carbon footprint calculation

**Next Actions:**
1. Open http://localhost:8516
2. Try the example queries
3. Explore the features
4. Add your own travel data

---

## 💡 Tips

- **First Query Might Be Slow** - The first query loads models and embeddings
- **Seed the Database** - Run the seed script for better results
- **Check Logs** - If something fails, check the terminal outputs
- **LM Studio** - Make sure the server is running and model is loaded

---

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review logs in terminals
3. Run: `python scripts/test_system.py`
4. Check: http://localhost:8001/health

---

**Enjoy planning sustainable trips with AI! 🌍✈️**
