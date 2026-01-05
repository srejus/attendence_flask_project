#!/bin/bash
set -e

# =========================
# Static Configuration
# =========================
BASE_DIR1="/home/administrator/attendance_base"
VENV_BIN="$BASE_DIR1/venv/bin"
BASE_DIR="/home/administrator/attendance_base/attendence_flask_project"
PORT=8000

# Flask WSGI entry point
# Format: module:app
FLASK_APP_MODULE="app:app"

# Derived values
PROJECT_NAME="$(basename "$BASE_DIR")"
WORKERS=3
LOG_LEVEL=info
TIMEOUT=180

LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/$PROJECT_NAME.log"

mkdir -p "$LOG_DIR"

start_server() {
    echo "Starting Flask ($PROJECT_NAME) on port $PORT..."

    "$VENV_BIN/gunicorn" \
        --workers "$WORKERS" \
        --bind 127.0.0.1:"$PORT" \
        --log-level "$LOG_LEVEL" \
        --access-logfile "$LOG_FILE" \
        --error-logfile "$LOG_FILE" \
        --timeout "$TIMEOUT" \
        "$FLASK_APP_MODULE" &

    echo "Gunicorn started."
}

stop_server() {
    echo "Stopping Flask on port $PORT..."

    PID=$(lsof -ti tcp:"$PORT" || true)

    if [ -n "$PID" ]; then
        kill -9 $PID
        echo "Killed PID $PID"
    else
        echo "No process running on port $PORT"
    fi
}

case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
