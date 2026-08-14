#!/bin/bash

# AI Trip Agent - Quick Start Script
# This script sets up and starts the AI Trip Agent system

set -e

echo "=========================================="
echo "AI Trip Agent - Quick Start"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo -e "${GREEN}✅ Python found: $(python3 --version)${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker is not installed${NC}"
    echo "Please install Docker to run ChromaDB"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
fi

# Create data directory
mkdir -p chroma_data

# Check if ChromaDB is running
echo ""
echo "Checking ChromaDB..."
if docker ps | grep -q ai-trip-agent-chroma; then
    echo -e "${GREEN}✅ ChromaDB is already running${NC}"
else
    echo "Starting ChromaDB..."
    docker run -d \
        --name ai-trip-agent-chroma \
        -p 8002:8000 \
        -v $(pwd)/chroma_data:/chroma/chroma \
        chromadb/chroma:latest
    
    echo "Waiting for ChromaDB to start..."
    sleep 5
    echo -e "${GREEN}✅ ChromaDB started${NC}"
fi

# Test ChromaDB connection
if curl -s http://localhost:8002/api/v1/heartbeat > /dev/null; then
    echo -e "${GREEN}✅ ChromaDB is responding${NC}"
else
    echo -e "${RED}❌ ChromaDB is not responding${NC}"
    echo "Please check Docker logs: docker logs ai-trip-agent-chroma"
    exit 1
fi

# Check if vector store has data
echo ""
echo "Checking vector store..."
COLLECTION_COUNT=$(python3 -c "
from config import get_settings
from services.rag.embeddings import EmbeddingManager
from services.rag.vector_store import VectorStoreManager
try:
    s = get_settings()
    vm = VectorStoreManager(s, EmbeddingManager(s))
    stats = vm.get_collection_stats()
    print(stats.get('count', 0))
except:
    print(0)
" 2>/dev/null || echo "0")

if [ "$COLLECTION_COUNT" -eq "0" ]; then
    echo -e "${YELLOW}⚠️  Vector store is empty${NC}"
    echo "Seeding vector store with sample data..."
    python3 scripts/seed_vector_store.py --reset
    echo -e "${GREEN}✅ Vector store seeded${NC}"
else
    echo -e "${GREEN}✅ Vector store has $COLLECTION_COUNT documents${NC}"
fi

# Run system tests
echo ""
echo "Running system tests..."
if python3 scripts/test_system.py > /dev/null 2>&1; then
    echo -e "${GREEN}✅ System tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Some system tests failed${NC}"
    echo "Run 'python scripts/test_system.py' for details"
fi

# Display next steps
echo ""
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure LM Studio is running (if using local LLM):"
echo "   - Open LM Studio"
echo "   - Load model: llama-3.2-1b-instruct"
echo "   - Start server on http://127.0.0.1:1234"
echo ""
echo "2. Start the FastAPI backend:"
echo "   ${GREEN}uvicorn services.api.main:app --reload --port 8001${NC}"
echo ""
echo "3. In a new terminal, start the Streamlit UI:"
echo "   ${GREEN}streamlit run ui/streamlit_app.py --server.port 8516${NC}"
echo ""
echo "4. Open your browser:"
echo "   ${GREEN}http://localhost:8516${NC}"
echo ""
echo "Or use Docker Compose to start everything:"
echo "   ${GREEN}docker-compose up -d${NC}"
echo ""
echo "=========================================="
