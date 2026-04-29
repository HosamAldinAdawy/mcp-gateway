#!/bin/bash
# MCP Gateway — Smart Start Script
# Detects if Docker is available and starts accordingly

set -e

GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

echo -e "${CYAN}"
echo "  MCP Gateway — Starting..."
echo -e "${RESET}"

# Copy .env if not exists
if [ ! -f .env ]; then
  cp .env.example .env
  echo -e "${YELLOW}Created .env from .env.example — please fill your credentials${RESET}"
fi

# Check if Docker available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
  echo -e "${GREEN}Docker detected — starting with Docker${RESET}"
  echo ""
  echo "Pick your profile:"
  echo "  1. Core only (gateway + echo)"
  echo "  2. QA tools (jira, testrail, pytest)"
  echo "  3. Dev tools (github, git, azure)"
  echo "  4. General tools (filesystem, slack, search)"
  echo "  5. Everything"
  echo ""
  read -p "Choice [1]: " choice
  choice=${choice:-1}

  case $choice in
    1) docker-compose -f infra/docker-compose.yml up --build ;;
    2) docker-compose -f infra/docker-compose.yml --profile qa up --build ;;
    3) docker-compose -f infra/docker-compose.yml --profile dev up --build ;;
    4) docker-compose -f infra/docker-compose.yml --profile general up --build ;;
    5) docker-compose -f infra/docker-compose.yml --profile all up --build ;;
    *) docker-compose -f infra/docker-compose.yml up --build ;;
  esac
else
  echo -e "${YELLOW}Docker not found — starting locally${RESET}"
  pip install -r requirements.txt -q
  uvicorn gateway.main:app --reload --port 8000
fi
