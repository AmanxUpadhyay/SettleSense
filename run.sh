#!/bin/bash
#
# SettleSense Application Runner
# -----------------------------
# This script sets up and runs the SettleSense application
# with proper environment configuration.

# Colors for prettier output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Application constants
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${APP_DIR}/venv"
APP_PORT=${PORT:-5000}
APP_HOST=${HOST:-"127.0.0.1"}
DEBUG=${DEBUG:-"true"}

echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        ${GREEN}SettleSense Application${BLUE}        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"

# Setup virtual environment
setup_environment() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "\n${YELLOW}➤ Setting up virtual environment...${NC}"
        python3 -m venv "$VENV_DIR" || { 
            echo -e "${RED}✗ Failed to create virtual environment${NC}"; 
            exit 1; 
        }
        source "${VENV_DIR}/bin/activate"
        echo -e "${GREEN}✓ Virtual environment created${NC}"
        
        echo -e "\n${YELLOW}➤ Installing dependencies...${NC}"
        pip install --upgrade pip > /dev/null
        pip install -r "${APP_DIR}/settle_sense/requirements.txt" || {
            echo -e "${RED}✗ Failed to install dependencies${NC}";
            exit 1;
        }
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "\n${YELLOW}➤ Activating virtual environment...${NC}"
        source "${VENV_DIR}/bin/activate"
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    fi
}

# Run the application
run_application() {
    echo -e "\n${YELLOW}➤ Starting SettleSense...${NC}"
    
    # Check if .env file exists and source it
    if [ -f "${APP_DIR}/.env" ]; then
        echo -e "${BLUE}ⓘ Using environment variables from .env file${NC}"
        export $(grep -v '^#' "${APP_DIR}/.env" | xargs)
    fi
    
    # Change to application directory
    cd "${APP_DIR}/settle_sense"
    
    # Set environment variables
    export PORT=$APP_PORT
    export HOST=$APP_HOST
    export DEBUG=$DEBUG
    export FLASK_APP=app.py
    
    # Display info
    echo -e "\n${BLUE}ⓘ Configuration:${NC}"
    echo -e "  • ${BLUE}Host:${NC} $APP_HOST"
    echo -e "  • ${BLUE}Port:${NC} $APP_PORT"
    echo -e "  • ${BLUE}Debug mode:${NC} $([ "$DEBUG" == "true" ] && echo "Enabled" || echo "Disabled")"
    
    echo -e "\n${GREEN}✓ Application starting at http://$APP_HOST:$APP_PORT${NC}\n"
    
    # Run the app
    python app.py
    
    # Store exit code
    EXIT_CODE=$?
    
    # If we exited abnormally
    if [ $EXIT_CODE -ne 0 ]; then
        echo -e "\n${RED}✗ Application exited with code $EXIT_CODE${NC}"
    fi
    
    return $EXIT_CODE
}

# Clean up on exit
cleanup() {
    deactivate 2>/dev/null
    echo -e "\n${BLUE}ⓘ Environment deactivated${NC}"
}

# Register cleanup on exit
trap cleanup EXIT

# Run the program
setup_environment
run_application

exit $?
