#!/bin/bash

# Port number for the server
PORT=5000

# Name of the temporary virtual environment directory
VENV_DIR="./nchds_temp_env"

echo "=================================================================="
echo "    NCHDS Bangladesh - Centralized Healthcare System Prototype     "
echo "=================================================================="
echo ""

# 1. Create a temporary Python virtual environment
echo "[1/4] Initializing temporary virtual environment..."
python3 -m venv "$VENV_DIR"
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

# 2. Activate virtual environment and install Flask
echo "[2/4] Installing necessary dependencies (Flask)..."
source "$VENV_DIR/bin/activate"
pip install --quiet Flask

# 3. Start the Flask server in the background
echo "[3/4] Starting live server in background..."
python3 server.py &
SERVER_PID=$!

# Ensure the server started successfully
sleep 2.5
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "Error: Failed to start Flask server."
    rm -rf "$VENV_DIR"
    exit 1
fi

# 4. Open each section in separate browser tabs
echo "[4/4] Opening the 5 Centralized Sections in separate browser tabs..."

# Helper function to open URL using system default browser
open_url() {
    local url=$1
    if command -v xdg-open &>/dev/null; then
        xdg-open "$url"
    elif command -v gnome-open &>/dev/null; then
        gnome-open "$url"
    elif command -v google-chrome &>/dev/null; then
        google-chrome "$url"
    elif command -v firefox &>/dev/null; then
        firefox "$url"
    else
        echo "Please open in browser: $url"
    fi
}

open_url "http://localhost:$PORT/ministry"
sleep 0.5
open_url "http://localhost:$PORT/hospital"
sleep 0.5
open_url "http://localhost:$PORT/doctor"
sleep 0.5
open_url "http://localhost:$PORT/patient"
sleep 0.5
open_url "http://localhost:$PORT/pharmacy"

echo ""
echo "------------------------------------------------------------------"
echo " -> Prototype is live on http://localhost:$PORT"
echo " -> Active PID: $SERVER_PID"
echo " -> Temporary environment location: $VENV_DIR"
echo "------------------------------------------------------------------"
echo ""
echo "IMPORTANT: Keep this terminal window open to keep the prototype running."
echo "When you are done, press [Ctrl+C] or close the terminal."
echo "All temporary dependencies (venv) will be deleted immediately to optimize memory."
echo ""

# 5. Define cleanup trap function
cleanup() {
    echo ""
    echo "Shutting down Flask server (PID: $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    
    echo "Deleting temporary virtual environment and cleaning up workspace..."
    rm -rf "$VENV_DIR"
    
    # Optionally delete SQLite database to restore pristine state
    if [ -f "nchds.db" ]; then
        rm "nchds.db"
    fi
    
    echo "Cleanup complete! System memory and disk space optimized."
    exit 0
}

# Trap terminal shutdown signals
trap cleanup SIGINT SIGTERM EXIT

# Keep script running to maintain the background server and trap exit
wait $SERVER_PID
