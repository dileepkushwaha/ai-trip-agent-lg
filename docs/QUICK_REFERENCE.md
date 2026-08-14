# 🚀 AI Trip Agent v2.0 - Quick Reference Card

## 📱 Access Points

| Service | URL | Status |
|---------|-----|--------|
| **Streamlit UI** | http://localhost:8516 | ✅ Running |
| **FastAPI Docs** | http://localhost:8001/docs | ✅ Running |
| **API Health** | http://localhost:8001/health | ✅ Running |

---

## 🎨 UI Features

### Theme Toggle
- **Location**: Top-right corner
- **Light Mode**: ☀️ button
- **Dark Mode**: 🌙 button

### Sidebar Options

#### 1. Travel Persona
```
🎓 Student      👨‍👩‍👧‍👦 Family      🏛️ Heritage
💼 Corporate    🌿 Green        🚶 Solo
🕉️ Religious    🧘 Spiritual    🏔️ Adventure
💎 Luxury
```

#### 2. Transport Mode
```
🔀 Mixed (AI selects best)
🚗 Car (Petrol/Diesel/Electric)
🚌 Bus          🚆 Train
🏍️ Motorcycle   🚴 Bicycle
🚶 Walking
```

#### 3. Stoppage Duration
```
⚡ None (Direct)
⏰ Up to 3 hours
🕐 Up to 6 hours
🕛 12+ hours OK
```

#### 4. Real-Time Monitoring
```
☑️ Enable AI Agent
   - Weather alerts
   - Traffic updates
   - Event discovery
   - Travel advisories
```

---

## 🔌 API Quick Reference

### Plan Trip
```bash
POST /plan-trip
{
  "query": "Your trip query",
  "persona": "family",
  "transport_mode": "mixed",
  "stoppage_duration": "6_hours",
  "enable_realtime_agent": true
}
```

### Agent Status
```bash
GET /agent/{agent_id}/status
```

### Stop Agent
```bash
POST /agent/{agent_id}/stop
```

### List All Agents
```bash
GET /agents
```

---

## 🧪 Testing

### Run Full Test Suite
```bash
source .venv/bin/activate
python scripts/test_v2_features.py
```

### Quick Health Check
```bash
curl http://localhost:8001/health
```

---

## 🎯 Example Queries

### Family Trip
```
"Plan a 3-day family trip to Kaziranga with kids"
Persona: Family
Transport: Mixed
Stoppage: 6 hours
Agent: Enabled
```

### Budget Student Trip
```
"Budget-friendly 2-day trip to Majuli"
Persona: Student
Transport: Bus
Stoppage: 3 hours
Agent: Disabled
```

### Sustainable Solo Adventure
```
"Eco-friendly solo trip to Guwahati"
Persona: Green
Transport: Mixed
Stoppage: None
Agent: Enabled
```

### Corporate Business Trip
```
"Quick business trip to Guwahati"
Persona: Corporate
Transport: Car Electric
Stoppage: None
Agent: Disabled
```

---

## 🔧 Troubleshooting

### UI Issues
```bash
# Clear browser cache
# Refresh page
# Check console for errors
```

### API Issues
```bash
# Check logs
tail -f logs/api.log

# Restart API
# Terminal 1
source .venv/bin/activate
uvicorn services.api.main:app --port 8001 --reload
```

### Agent Issues
```bash
# List agents
curl http://localhost:8001/agents

# Stop specific agent
curl -X POST http://localhost:8001/agent/{id}/stop

# Cleanup old agents
curl -X POST http://localhost:8001/agents/cleanup
```

---

## 📊 Status Indicators

### Agent Status
- 🟢 **Active** - Monitoring in progress
- 🔵 **Monitoring** - Checking for updates
- 🟡 **Alert** - Important update available
- ⚫ **Stopped** - Monitoring ended
- 🔴 **Error** - Issue detected

### Update Types
- ℹ️ **Info** - General information
- ⚠️ **Warning** - Attention needed
- 🚨 **Alert** - Urgent notification
- ✅ **Success** - Positive update

---

## 🎓 Persona Characteristics

| Persona | Focus | Budget | Pace |
|---------|-------|--------|------|
| Student | Educational | Low | Flexible |
| Family | Kid-friendly | Medium | Relaxed |
| Heritage | Cultural | Medium | Moderate |
| Corporate | Efficient | High | Fast |
| Green | Sustainable | Medium | Moderate |
| Solo | Independent | Variable | Flexible |
| Religious | Spiritual | Low | Slow |
| Spiritual | Peaceful | Medium | Slow |
| Adventure | Thrilling | Medium | Fast |
| Luxury | Premium | High | Relaxed |

---

## 📈 Performance Tips

### For Best Results:
1. ✅ Use "mixed" transport for optimal suggestions
2. ✅ Enable agent for multi-day trips
3. ✅ Choose appropriate persona
4. ✅ Set realistic stoppage durations
5. ✅ Stop agents after trip completion

### For Faster Response:
1. ✅ Disable agent for short trips
2. ✅ Use specific transport mode
3. ✅ Keep queries concise
4. ✅ Avoid peak hours

---

## 🔐 Configuration

### Environment Variables
```bash
# .env file
LLM_PROVIDER=lmstudio
LMSTUDIO_API_URL=http://127.0.0.1:1234/v1
EMBEDDING_PROVIDER=huggingface
CHROMA_HOST=localhost
CHROMA_PORT=8002
```

### Agent Settings
```python
# agents/realtime_agent.py
check_interval = 300  # 5 minutes
max_updates = 20      # Keep last 20
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `QUICKSTART.md` | Quick start guide |
| `REALTIME_AGENT_GUIDE.md` | Agent system guide |
| `RELEASE_NOTES_v2.0.md` | Release notes |
| `IMPLEMENTATION_SUMMARY.md` | Implementation details |
| `QUICK_REFERENCE.md` | This file |

---

## 🆘 Quick Help

### Services Not Running?
```bash
# Check if running
curl http://localhost:8001/health
curl http://localhost:8516

# Start services
./scripts/start_services.sh
```

### Agent Not Working?
```bash
# Check agent list
curl http://localhost:8001/agents

# View agent status
curl http://localhost:8001/agent/{id}/status
```

### UI Not Loading?
```bash
# Check Streamlit
ps aux | grep streamlit

# Restart Streamlit
streamlit run ui/streamlit_app.py --server.port 8516
```

---

## 🎉 Success Checklist

Before using the system:
- ✅ API is running (port 8001)
- ✅ UI is running (port 8516)
- ✅ ChromaDB is connected
- ✅ LM Studio is running
- ✅ Vector store is seeded

During trip planning:
- ✅ Select appropriate persona
- ✅ Choose transport mode
- ✅ Set stoppage duration
- ✅ Enable agent if needed
- ✅ Enter clear query

After trip planning:
- ✅ Review itinerary
- ✅ Check carbon footprint
- ✅ Monitor agent updates
- ✅ Stop agent when done
- ✅ Provide feedback

---

## 📞 Support Contacts

### Documentation
- Read guides in project root
- Check API docs at /docs
- Review test results

### Logs
```bash
# API logs
tail -f logs/api.log

# UI logs
tail -f logs/ui.log
```

### Testing
```bash
# Run tests
python scripts/test_v2_features.py

# Check system
python scripts/test_system.py
```

---

## 🌟 Pro Tips

1. **Use Mixed Transport** - Let AI optimize your route
2. **Enable Agent for Long Trips** - Get real-time updates
3. **Choose Right Persona** - Get personalized recommendations
4. **Set Realistic Stoppages** - Balance speed and comfort
5. **Stop Agents After Trip** - Free up resources
6. **Check Updates Regularly** - Stay informed
7. **Use Dark Mode** - Easier on eyes
8. **Save Agent IDs** - Track multiple trips
9. **Review Carbon Footprint** - Make sustainable choices
10. **Provide Clear Queries** - Get better results

---

**Version**: 2.0.0  
**Last Updated**: October 2025  
**Status**: Production Ready

**Happy Traveling! 🧳✈️🌍**
