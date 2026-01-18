#!/bin/bash

###############################################################################
# OmniParser UI Shutdown Script
# Gracefully stops both FastAPI backend and React frontend
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
PID_FILE="$SCRIPT_DIR/.omniparser_ui.pid"
BACKEND_LOG="$SCRIPT_DIR/backend.log"
FRONTEND_LOG="$SCRIPT_DIR/frontend.log"

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Stopping OmniParser UI${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ! -f "$PID_FILE" ]; then
    print_warning "No PID file found. UI may not be running."
    exit 0
fi

# Kill all processes listed in PID file
KILLED=false
while read -r pid; do
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
        print_info "Stopping process $pid..."
        kill "$pid" 2>/dev/null || true
        KILLED=true
    fi
done < "$PID_FILE"

# Remove PID file
rm -f "$PID_FILE"

if [ "$KILLED" = true ]; then
    print_status "UI stopped successfully"
else
    print_warning "No running processes found"
fi

# Optionally remove log files
if [ "$1" == "--clean" ]; then
    print_info "Removing log files..."
    rm -f "$BACKEND_LOG" "$FRONTEND_LOG"
    print_status "Log files removed"
fi

echo ""
