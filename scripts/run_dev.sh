#!/bin/bash

# Add the src directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Colors for prettier output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Portfolio in development mode...${NC}"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables for development
export PORTFOLIO_ENV="development"
export PORTFOLIO_CONFIG_PATH="config/development/config.yaml"

# Install the package in development mode if not already installed
pip install -e .

# Run the application with uvicorn
uvicorn portfolio.main:app --reload --host 0.0.0.0 --port 8000
