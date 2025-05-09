#!/bin/bash
#
# SettleSense Installation Script
# -------------------------------
# This script installs the SettleSense application
# and sets up the environment.

# Colors for prettier output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Application constants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
CONFIG_FILE="${SCRIPT_DIR}/.env"

# Print banner
echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          ${GREEN}SettleSense Installer${BLUE}               ║${NC}"
echo -e "${BLUE}║         ${YELLOW}Debt Management Made Easy${BLUE}           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo

# Check Python version
echo -e "${YELLOW}➤ Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
    else
        echo -e "${RED}✗ Python 3.8 or higher is required, found $PYTHON_VERSION${NC}"
        echo -e "${YELLOW}➤ Please install Python 3.8 or higher and try again${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo -e "${YELLOW}➤ Please install Python 3.8 or higher and try again${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}➤ Setting up virtual environment...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}ⓘ Virtual environment already exists, upgrading...${NC}"
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to create virtual environment${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment created at $VENV_DIR${NC}"

# Activate virtual environment
source "${VENV_DIR}/bin/activate"

# Install dependencies
echo -e "\n${YELLOW}➤ Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null
pip install -r "${SCRIPT_DIR}/settle_sense/requirements.txt"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencies installed successfully${NC}"

# Create configuration file
echo -e "\n${YELLOW}➤ Setting up configuration...${NC}"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}ⓘ Configuration file already exists${NC}"
else
    echo -e "${YELLOW}ⓘ Creating configuration file...${NC}"
    cp "${SCRIPT_DIR}/.env.example" "$CONFIG_FILE"
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "" "s/changeme_this_is_not_secure_in_production/$SECRET_KEY/" "$CONFIG_FILE"
    echo -e "${GREEN}✓ Configuration file created with a secure secret key${NC}"
fi

# Create necessary directories
echo -e "\n${YELLOW}➤ Creating required directories...${NC}"
mkdir -p "${SCRIPT_DIR}/settle_sense/instance"
mkdir -p "${SCRIPT_DIR}/settle_sense/backups"
echo -e "${GREEN}✓ Directories created${NC}"

# Make scripts executable
echo -e "\n${YELLOW}➤ Setting permissions...${NC}"
chmod +x "${SCRIPT_DIR}/run.sh"
chmod +x "${SCRIPT_DIR}/service.sh"
echo -e "${GREEN}✓ Scripts are now executable${NC}"

# Final message
echo -e "\n${GREEN}✅ SettleSense installation complete!${NC}"
echo -e "${BLUE}───────────────────────────────────────────────${NC}"
echo -e "${YELLOW}➤ To start the application:${NC}"
echo -e "  ${BLUE}•${NC} Development mode: ${YELLOW}./run.sh${NC}"
echo -e "  ${BLUE}•${NC} Service mode:     ${YELLOW}./service.sh start${NC}"
echo -e "${YELLOW}➤ Access the application at:${NC} http://127.0.0.1:5000"
echo -e "${BLUE}───────────────────────────────────────────────${NC}"

# Cleanup
deactivate
