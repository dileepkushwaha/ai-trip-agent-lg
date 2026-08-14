#!/bin/bash

# AI Trip Agent - Start Services Script
# This script starts both FastAPI and Streamlit services

echo "=========================================="
echo "AI Trip Agent - Starting Services"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if ChromaDB is running
if ! docker ps | grep -q ai-trip-agent-chroma; then
    echo "⚠️  ChromaDB is not running. Starting it..."
    docker run -d \
        --name ai-trip-agent-chroma \
        -p 8002:8000 \
        -v $(pwd)/chroma_data:/chroma/chroma \
        chromadb/chroma:latest
    sleep 3
fi

echo "✅ ChromaDB is running"
echo ""

# Start FastAPI in background
echo "Starting FastAPI backend on http://localhost:8001..."
uvicorn services.api.main:app --host 0.0.0.0 --port 8001 --reload > logs/api.log 2>&1 &
API_PID=$!
echo "✅ FastAPI started (PID: $API_PID)"
echo ""

# Wait for API to be ready
sleep 3

# Start Streamlit in background
echo "Starting Streamlit UI on http://localhost:8516..."
streamlit run ui/streamlit_app.py --server.port 8516 --server.address 0.0.0.0 > logs/ui.log 2>&1 &
UI_PID=$!
echo "✅ Streamlit started (PID: $UI_PID)"
echo ""

# Wait for services to start
sleep 5

# Check if services are running
echo "Checking services..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ FastAPI is responding"
else
    echo "❌ FastAPI is not responding"
fi

if curl -s http://localhost:8516 > /dev/null; then
    echo "✅ Streamlit is responding"
else
    echo "❌ Streamlit is not responding"
fi

echo ""
echo "=========================================="
echo "Services Started Successfully! 🎉"
echo "=========================================="
echo ""
echo "Access the application:"
echo "  • Streamlit UI:  http://localhost:8516"
echo "  • FastAPI Docs:  http://localhost:8001/docs"
echo "  • API Health:    http://localhost:8001/health"
echo ""
echo "Process IDs:"
echo "  • FastAPI PID:   $API_PID"
echo "  • Streamlit PID: $UI_PID"
echo ""
echo "To stop services:"
echo "  kill $API_PID $UI_PID"
echo ""
echo "Logs:"
echo "  • API:  tail -f logs/api.log"
echo "  • UI:   tail -f logs/ui.log"
echo ""
echo "=========================================="
