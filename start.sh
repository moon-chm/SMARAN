#!/bin/bash
# start.sh - Single command startup script for SMARAN

# Stop on first error
set -e

# Define colors for output formatting
GREEN='\03C[0;32m'
RED='\03C[0;31m'
YELLOW='\03C[1;33m'
NC='\03C[0m' # No Color

echo -e "${GREEN}🚀 Starting SMARAN Initialization Pipeline...${NC}\n"

# Verify .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ ERROR: .env file missing in the root directory!${NC}"
    echo "Please copy .env.example to .env and configure the required keys."
    exit 1
fi

# Function to check required .env keys
check_env_key() {
    if ! grep -q "^$1=" .env; then
        echo -e "${RED}❌ ERROR: Required configuration key '$1' not found in .env!${NC}"
        exit 1
    fi
}

echo "1. Checking environment keys..."
check_env_key "NEO4J_URI"
check_env_key "NEO4J_USER"
check_env_key "NEO4J_PASSWORD"
check_env_key "GROQ_API_KEY"
check_env_key "JWT_SECRET"
echo -e "${GREEN}✅ .env Configuration OK${NC}\n"

# Check if port 8000 is occupied
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️ WARNING: Port 8000 is already in use. Please stop the existing process before continuing.${NC}"
    exit 1
fi

export PYTHONPATH=$PWD

# Step 1: Initialize Neo4j Graph
echo "Step 1: Initializing Neo4j Schema (Constraints & Indices)..."
python app/graph/init_graph.py
echo -e "${GREEN}✅ Graph Initialized${NC}\n"

# Start the API in the background
echo "Step 2: Booting FastAPI layer..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for API to come online
echo "Waiting for API to hit Health check bounds..."
until $(curl --output /dev/null --silent --head --fail http://localhost:8000/health); do
    printf '.'
    sleep 2
done
echo -e "\n${GREEN}✅ FastAPI Online${NC}\n"

# Step 3: Start Streamlit Dashboards
echo "Step 3: Starting Streamlit Panels..."
streamlit run frontend/caregiver_panel.py --server.port 8501 --server.headless true > /dev/null 2>&1 &
CG_PID=$!

streamlit run frontend/elder_panel.py --server.port 8502 --server.headless true > /dev/null 2>&1 &
ELDER_PID=$!

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}🌟 SMARAN SYSTEM IS LIVE 🌟${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "📖 FastAPI Docs:        http://localhost:8000/docs"
echo -e "🩺 Health Check:        http://localhost:8000/health"
echo -e "🏥 Caregiver Panel:     http://localhost:8501"
echo -e "💖 Elder Panel:         http://localhost:8502"
echo -e "🔑 Credentials:         caregiver_demo / password123"
echo -e "                        elder_123 / password123"
echo -e "${GREEN}================================================${NC}"
echo -e "\nPress Ctrl+C to stop all services..."

# Wait traps
trap "echo -e '\n${YELLOW}Shutting down SMARAN...${NC}'; kill $API_PID $CG_PID $ELDER_PID" SIGINT SIGTERM
wait
