#!/bin/bash
# SettleSense Service Manager
# Usage: ./service.sh [start|stop|restart|status]

APP_DIR="/Users/godl1ke/Documents/SettleSense/settle_sense"
VENV_DIR="/Users/godl1ke/Documents/SettleSense/venv"
PID_FILE="/tmp/settlesense.pid"
LOG_FILE="/tmp/settlesense.log"
PORT=${PORT:-8000}

start_app() {
    echo "Starting SettleSense on port $PORT..."
    
    # Activate virtual environment if it exists
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
    fi
    
    # Start the app
    cd "$APP_DIR" && \
    PORT=$PORT nohup python3 app.py > "$LOG_FILE" 2>&1 & 
    echo $! > "$PID_FILE"
    
    echo "SettleSense started with PID: $(cat $PID_FILE)"
    echo "Access the app at: http://127.0.0.1:$PORT"
    echo "Logs available at: $LOG_FILE"
}

stop_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "Stopping SettleSense (PID: $PID)..."
        
        if ps -p "$PID" > /dev/null; then
            kill "$PID"
            sleep 2
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null; then
                echo "Application did not stop gracefully, forcing..."
                kill -9 "$PID"
            fi
            
            echo "SettleSense stopped"
        else
            echo "Process not running but PID file exists"
        fi
        
        rm -f "$PID_FILE"
    else
        echo "SettleSense is not running (no PID file)"
    fi
}

check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        
        if ps -p "$PID" > /dev/null; then
            echo "SettleSense is running (PID: $PID)"
            echo "URL: http://127.0.0.1:$PORT"
            return 0
        else
            echo "SettleSense is not running (stale PID file)"
            return 1
        fi
    else
        echo "SettleSense is not running"
        return 1
    fi
}

case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        stop_app
        sleep 2
        start_app
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
