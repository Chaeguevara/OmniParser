# OmniParser UI Quick Start

## One-Command Startup

The easiest way to run the OmniParser React UI:

```bash
./start_ui.sh
```

This script automatically:
- ✅ Checks prerequisites (Python venv, Node.js)
- ✅ Installs frontend dependencies (npm install)
- ✅ Starts FastAPI backend (port 8888)
- ✅ Starts React frontend (port 5173)
- ✅ Shows combined logs from both servers

**Access the UI**: http://localhost:5173

**Stop the servers**: Press `Ctrl+C` or run `./stop_ui.sh`

## Requirements

Before running `start_ui.sh`, ensure you have:

1. **Python environment** set up:
   ```bash
   ./install.sh  # Creates venv and installs dependencies
   ```

2. **Node.js 18+** installed:
   - **macOS**: `brew install node`
   - **Ubuntu/Debian**: `sudo apt-get install nodejs npm`
   - **Windows**: Download from https://nodejs.org/

## What Gets Started

### Backend (FastAPI)
- **Port**: 8888
- **API Documentation**: http://localhost:8888/docs
- **WebSocket**: ws://localhost:8888/ws/agent/stream
- **Log file**: `backend.log`

### Frontend (React + Vite)
- **Port**: 5173
- **UI**: http://localhost:5173
- **Hot reload**: Enabled (changes update instantly)
- **Log file**: `frontend.log`

## Manual Startup (Alternative)

If you prefer separate terminal windows:

### Terminal 1: Backend
```bash
source venv/bin/activate
cd omnitool/backend
uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

### Terminal 2: Frontend
```bash
cd omnitool/frontend
npm install
npm run dev
```

## Troubleshooting

### "Node.js not found"
Install Node.js 18+ from https://nodejs.org/ or use your package manager:
```bash
# macOS
brew install node

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nodejs npm

# Verify installation
node -v  # Should show v18.0.0 or higher
```

### "Virtual environment not found"
Run the installation script first:
```bash
./install.sh
```

### "Backend failed to start"
Check the backend log:
```bash
tail -f backend.log
```

Common issues:
- Port 8888 already in use: Change `BACKEND_PORT` in `start_ui.sh`
- Missing dependencies: Run `pip install -r requirements.txt`

### "Frontend failed to start"
Check the frontend log:
```bash
tail -f frontend.log
```

Common issues:
- Port 5173 already in use: Vite will auto-select another port
- Missing dependencies: Run `cd omnitool/frontend && npm install`

### Clean Shutdown

To stop both servers gracefully:
```bash
./stop_ui.sh
```

To also remove log files:
```bash
./stop_ui.sh --clean
```

## Production Deployment

For production, build the frontend and serve it from the backend:

```bash
# Build frontend
cd omnitool/frontend
npm run build

# Serve from backend
cd ../backend
uvicorn main:app --host 0.0.0.0 --port 8888 --workers 4
```

The backend automatically serves static files from `omnitool/frontend/dist/`.

## Next Steps

- **Configure settings**: Click the settings icon in the UI
- **Select model**: Choose from Cloud API or Local LLM options
- **Start chatting**: Send instructions to the agent
- **View documentation**: http://localhost:8888/docs

For detailed documentation, see:
- `omnitool/frontend/README.md` - Frontend development guide
- `omnitool/backend/README.md` - Backend API reference
- `docs/FRONTEND_BACKEND_ARCHITECTURE.md` - Full architecture details
