#!/bin/bash

###############################################################################
# OmniParser UI Startup Script
# Starts both FastAPI backend and React frontend
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/omnitool/backend"
FRONTEND_DIR="$SCRIPT_DIR/omnitool/frontend"
VENV_DIR="$SCRIPT_DIR/venv"
PID_FILE="$SCRIPT_DIR/.omniparser_ui.pid"

# Configuration
BACKEND_PORT=8888
FRONTEND_PORT=5173
BACKEND_LOG="$SCRIPT_DIR/backend.log"
FRONTEND_LOG="$SCRIPT_DIR/frontend.log"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  OmniParser UI Launcher${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found. Run './install.sh' first."
        exit 1
    fi

    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Install Node.js 18+ to run the frontend."
        print_info "On macOS: brew install node"
        print_info "On Ubuntu: sudo apt-get install nodejs npm"
        exit 1
    fi

    # Check Node.js version
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_warning "Node.js $NODE_VERSION detected. Node.js 18+ recommended."
    fi

    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi

    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi

    print_status "Prerequisites check passed"
    echo ""
}

install_frontend_deps() {
    print_info "Checking frontend dependencies..."

    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        print_info "Installing frontend dependencies (this may take a minute)..."
        cd "$FRONTEND_DIR"
        npm install --quiet
        cd "$SCRIPT_DIR"
        print_status "Frontend dependencies installed"
    else
        print_status "Frontend dependencies already installed"
    fi
    echo ""
}

cleanup() {
    echo ""
    print_info "Shutting down..."

    if [ -f "$PID_FILE" ]; then
        # Kill all processes in the process group
        if [ -s "$PID_FILE" ]; then
            while read -r pid; do
                if ps -p "$pid" > /dev/null 2>&1; then
                    kill "$pid" 2>/dev/null || true
                fi
            done < "$PID_FILE"
        fi
        rm -f "$PID_FILE"
    fi

    print_status "Shutdown complete"
    exit 0
}

start_backend() {
    print_info "Starting FastAPI backend on port $BACKEND_PORT..."

    # Activate virtual environment and start backend
    cd "$BACKEND_DIR"
    (
        source "$VENV_DIR/bin/activate"
        uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$BACKEND_LOG" 2>&1 &
        echo $! >> "$PID_FILE"
    )
    cd "$SCRIPT_DIR"

    # Wait for backend to start
    sleep 2

    # Check if backend is running
    if curl -s "http://localhost:$BACKEND_PORT/docs" > /dev/null 2>&1; then
        print_status "Backend started successfully"
        print_info "API docs: ${BLUE}http://localhost:$BACKEND_PORT/docs${NC}"
    else
        print_warning "Backend may still be starting (check $BACKEND_LOG for details)"
    fi
    echo ""
}

start_frontend() {
    print_info "Starting React frontend on port $FRONTEND_PORT..."

    cd "$FRONTEND_DIR"
    npm run dev > "$FRONTEND_LOG" 2>&1 &
    echo $! >> "$PID_FILE"
    cd "$SCRIPT_DIR"

    # Wait for frontend to start
    sleep 3

    print_status "Frontend started successfully"
    print_info "UI: ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
    echo ""
}

show_logs() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  OmniParser UI is running!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  Frontend: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "  Backend:  ${GREEN}http://localhost:$BACKEND_PORT${NC}"
    echo -e "  API Docs: ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"
    echo ""
    echo -e "  Backend log: $BACKEND_LOG"
    echo -e "  Frontend log: $FRONTEND_LOG"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Tail both logs
    print_info "Showing combined logs (Ctrl+C to stop)..."
    echo ""
    tail -f "$BACKEND_LOG" -f "$FRONTEND_LOG" 2>/dev/null || true
}

###############################################################################
# Main Script
###############################################################################

# Set up cleanup on exit
trap cleanup SIGINT SIGTERM EXIT

# Clear old PID file
> "$PID_FILE"

print_header
check_prerequisites
install_frontend_deps
start_backend
start_frontend
show_logs
