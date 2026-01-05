#!/bin/bash
set -e

# =========================
# Configuration
# =========================
BASE_DIR1="/home/administrator/attendance_base"
VENV_BIN="$BASE_DIR1/venv/bin"
BASE_DIR="$BASE_DIR1/attendence_flask_project"

PORT=8000
FLASK_APP_MODULE="app:app"

WORKERS=3
LOG_LEVEL=info
TIMEOUT=180

PROJECT_NAME="$(basename "$BASE_DIR")"

LOG_DIR="$BASE_DIR/logs"
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"
PID_FILE="$LOG_DIR/gunicorn.pid"

# =========================
# Pre-flight checks
# =========================
if [ ! -x "$VENV_BIN/gunicorn" ]; then
    echo "ERROR: gunicorn not found in venv"
    exit 1
fi

mkdir -p "$LOG_DIR"
cd "$BASE_DIR"

# =========================
# Functions
# =========================
start_server() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Server already running (PID $(cat "$PID_FILE"))"
        exit 0
    fi

    echo "Starting Flask ($PROJECT_NAME) on port $PORT..."

    "$VENV_BIN/gunicorn" \
        --workers "$WORKERS" \
        --bind 127.0.0.1:"$PORT" \
        --log-level "$LOG_LEVEL" \
        --access-logfile "$ACCESS_LOG" \
        --error-logfile "$ERROR_LOG" \
        --timeout "$TIMEOUT" \
        --pid "$PID_FILE" \
        "$FLASK_APP_MODULE" \
        --daemon

    echo "Gunicorn started with PID $(cat "$PID_FILE")"
}

stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        echo "No PID file found. Server not running?"
        return
    fi

    PID=$(cat "$PID_FILE")

    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping Gunicorn (PID $PID)..."
        kill "$PID"
        sleep 2

        if kill -0 "$PID" 2>/dev/null; then
            echo "Force killing Gunicorn..."
            kill -9 "$PID"
        fi
    fi

    rm -f "$PID_FILE"
    echo "Server stopped."
}

# =========================
# Command Router
# =========================
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        start_server
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
