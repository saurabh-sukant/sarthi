#!/bin/bash

# SARTHI Setup and Run Script
# Supports both local and Docker deployments

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${CYAN}  SARTHI - Incident Co-Pilot Setup${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
}

check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env file not found${NC}"
        if [ -f .env.example ]; then
            echo -e "${YELLOW}Copying .env.example to .env${NC}"
            cp .env.example .env
            echo -e "${YELLOW}Please edit .env with your OpenAI API key and SECRET_KEY${NC}"
            exit 1
        fi
    fi
}

run_local() {
    echo -e "${GREEN}🚀 Starting SARTHI locally...${NC}"
    
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -r requirements.txt > /dev/null 2>&1
    
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm ci > /dev/null 2>&1
    cd ..
    
    echo -e "${YELLOW}Starting services...${NC}"
    echo ""
    echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
    echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
    echo ""
    
    # Run backend in background
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Run frontend in background
    cd frontend
    VITE_API_BASE_URL=http://localhost:8000 npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✓ Services running (PIDs: $BACKEND_PID, $FRONTEND_PID)${NC}"
    
    # Cleanup on exit
    trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
    wait
}

run_docker() {
    echo -e "${GREEN}🐳 Starting SARTHI with Docker Compose...${NC}"
    
    check_env
    
    echo -e "${YELLOW}Building images...${NC}"
    docker-compose build
    
    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✓ Services running:${NC}"
    echo -e "${GREEN}  Frontend: http://localhost:5173${NC}"
    echo -e "${GREEN}  API: http://localhost:8000${NC}"
    echo -e "${GREEN}  API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}  Chroma: http://localhost:8001${NC}"
    echo ""
    echo -e "${YELLOW}View logs: docker-compose logs -f${NC}"
    echo -e "${YELLOW}Stop: docker-compose down${NC}"
}

print_header

if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage: ./setup.sh [local|docker]${NC}"
    echo ""
    echo "  local   - Run locally (requires Python, Node, npm)"
    echo "  docker  - Run with Docker Compose"
    echo ""
    exit 1
fi

case "$1" in
    local)
        run_local
        ;;
    docker)
        run_docker
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        exit 1
        ;;
esac
