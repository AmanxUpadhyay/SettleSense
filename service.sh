#!/bin/bash
#
# SettleSense Service Manager
# ---------------------------
# This script manages the SettleSense application service
# Usage: ./service.sh [start|stop|restart|status|logs]
#
# Author: godl1ke
# Date: May 9, 2025

# Colors for prettier output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Application constants
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTLE_SENSE_DIR="${APP_DIR}/settle_sense"
VENV_DIR="${APP_DIR}/venv"
PID_FILE="${APP_DIR}/.settlesense.pid"
LOG_FILE="${APP_DIR}/settlesense.log"
PORT=${PORT:-8000}
HOST=${HOST:-"127.0.0.1"}
URL="http://${HOST}:${PORT}"

# Print banner
print_banner() {
    echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       ${GREEN}SettleSense Service Manager${BLUE}    ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
    echo
}

# Start the application
start_app() {
    echo -e "${YELLOW}➤ Starting SettleSense service...${NC}"
    
    # Check if already running
    if [ -f "$PID_FILE" ] && ps -p "$(cat $PID_FILE)" >/dev/null 2>&1; then
        echo -e "${RED}✗ SettleSense is already running with PID: $(cat $PID_FILE)${NC}"
        return 1
    fi
    
    # Create necessary directories
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Activate virtual environment
    if [ -d "$VENV_DIR" ]; then
        source "${VENV_DIR}/bin/activate"
    else
        echo -e "${YELLOW}ⓘ Virtual environment not found, initializing...${NC}"
        python3 -m venv "$VENV_DIR"
        source "${VENV_DIR}/bin/activate"
        pip install -r "${SETTLE_SENSE_DIR}/requirements.txt" >/dev/null 2>&1
    fi
    
    # Set environment variables from .env if it exists
    if [ -f "${APP_DIR}/.env" ]; then
        export $(grep -v '^#' "${APP_DIR}/.env" | xargs)
    fi
    
    # Start the app as a background process
    echo -e "${YELLOW}➤ Launching application...${NC}"
    cd "${SETTLE_SENSE_DIR}" && \
    nohup python3 app.py > "$LOG_FILE" 2>&1 & 
    APP_PID=$!
    
    # Check if process started successfully
    sleep 2
    if ps -p $APP_PID >/dev/null; then
        echo $APP_PID > "$PID_FILE"
        echo -e "${GREEN}✓ SettleSense started successfully!${NC}"
        echo -e "${CYAN}ⓘ Service Details:${NC}"
        echo -e "  • ${CYAN}Process ID:${NC} $APP_PID"
        echo -e "  • ${CYAN}Access URL:${NC} $URL"
        echo -e "  • ${CYAN}Log File:${NC} $LOG_FILE"
    else
        echo -e "${RED}✗ Failed to start SettleSense${NC}"
        echo -e "${YELLOW}ⓘ Check log for details: $LOG_FILE${NC}"
        return 1
    fi
}

# Stop the application
stop_app() {
    echo -e "${YELLOW}➤ Stopping SettleSense service...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        
        if ps -p "$PID" >/dev/null 2>&1; then
            echo -e "${YELLOW}➤ Sending termination signal to process $PID...${NC}"
            kill "$PID"
            
            # Wait for process to terminate gracefully
            for i in {1..10}; do
                echo -n "."
                sleep 0.5
                if ! ps -p "$PID" >/dev/null 2>&1; then
                    echo -e "\n${GREEN}✓ SettleSense stopped successfully${NC}"
                    rm -f "$PID_FILE"
                    return 0
                fi
            done
            
            # Force termination if still running
            echo -e "\n${RED}! Process did not terminate gracefully, forcing...${NC}"
            kill -9 "$PID" >/dev/null 2>&1
            
            if ! ps -p "$PID" >/dev/null 2>&1; then
                echo -e "${GREEN}✓ SettleSense forcefully terminated${NC}"
                rm -f "$PID_FILE"
                return 0
            else
                echo -e "${RED}✗ Failed to terminate SettleSense${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}ⓘ Process not running but PID file exists${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}ⓘ SettleSense is not running (no PID file)${NC}"
    fi
}

# Check application status
check_status() {
    echo -e "${YELLOW}➤ Checking SettleSense service status...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        
        if ps -p "$PID" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ SettleSense is running${NC}"
            echo -e "${CYAN}ⓘ Service Details:${NC}"
            echo -e "  • ${CYAN}Process ID:${NC} $PID"
            echo -e "  • ${CYAN}Access URL:${NC} $URL"
            echo -e "  • ${CYAN}Log File:${NC} $LOG_FILE"
            echo -e "  • ${CYAN}Uptime:${NC} $(ps -p $PID -o etime= | xargs)"
            return 0
        else
            echo -e "${RED}✗ SettleSense is not running (stale PID file)${NC}"
            echo -e "${YELLOW}ⓘ Removing stale PID file${NC}"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo -e "${YELLOW}ⓘ SettleSense is not running${NC}"
        return 1
    fi
}

# View logs
view_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}➤ Displaying recent logs...${NC}"
        echo -e "${BLUE}─────────────── Log Start ───────────────${NC}"
        tail -n 50 "$LOG_FILE"
        echo -e "${BLUE}──────────────── Log End ────────────────${NC}"
        echo -e "${CYAN}ⓘ Complete logs available at: $LOG_FILE${NC}"
    else
        echo -e "${RED}✗ Log file not found${NC}"
        return 1
    fi
}

# Main function
main() {
    print_banner
    
    case "$1" in
        start)
            start_app
            ;;
        stop)
            stop_app
            ;;
        restart)
            stop_app
            echo
            sleep 2
            start_app
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs
            ;;
        *)
            echo -e "${CYAN}Usage: $0 {start|stop|restart|status|logs}${NC}"
            exit 1
            ;;
    esac
    
    exit $?
}

# Run main function
main "$@"
