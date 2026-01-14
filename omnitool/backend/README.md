# OmniParser Backend API

FastAPI backend for OmniParser with REST + WebSocket API.

## Quick Start

```bash
# Install dependencies (from project root)
pip install fastapi uvicorn websockets

# Run backend server
cd omnitool/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8888/docs
- **ReDoc**: http://localhost:8888/redoc

## Architecture

```
omnitool/backend/
├── main.py                 # FastAPI app entry point
├── routers/                # API endpoint routers
│   ├── chat.py            # Chat endpoints
│   ├── agent.py           # Agent control endpoints
│   ├── settings.py        # Settings endpoints
│   └── websocket.py       # WebSocket endpoint
├── services/              # Business logic
│   ├── agent_service.py   # Agent orchestration
│   ├── chat_service.py    # Chat history management
│   └── settings_service.py# Settings management
└── models/                # Pydantic models
    └── schemas.py         # Request/response models
```

## REST API Endpoints

### Chat
- `POST /api/chat/message` - Send message
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear history

### Agent
- `POST /api/agent/start` - Start agent
- `POST /api/agent/stop` - Stop agent
- `GET /api/agent/status` - Get agent status

### Settings
- `GET /api/settings` - Get settings
- `POST /api/settings` - Update settings

### WebSocket
- `WS /ws/agent/stream` - Real-time agent communication

## WebSocket Protocol

### Client → Server

```json
{
  "type": "user_message",
  "content": "Click the submit button"
}
```

### Server → Client

```json
{
  "type": "agent_message" | "tool_result" | "screenshot" | "error" | "status",
  "data": {
    "content": "...",
    "sender": "bot" | "tool",
    "timestamp": "2025-01-14T12:00:00Z"
  }
}
```

## Environment Variables

```bash
# Optional overrides
OMNIPARSER_SERVER_URL=localhost:8000
WINDOWS_HOST_URL=localhost:8006
```

## Development

```bash
# Run with auto-reload
uvicorn omnitool.backend.main:app --reload --port 8888

# Run with specific host
uvicorn omnitool.backend.main:app --host 0.0.0.0 --port 8888
```

## Production

```bash
# Run with multiple workers
uvicorn omnitool.backend.main:app --host 0.0.0.0 --port 8888 --workers 4
```

## Security

- CORS is configured for `localhost:5173` (Vite) and `localhost:3000` (React dev)
- Update `allow_origins` in `main.py` for production
- Add authentication middleware if needed (JWT, API keys)

## Next Steps

1. Start backend: `uvicorn omnitool.backend.main:app --reload`
2. Test API: Visit http://localhost:8888/docs
3. Connect frontend: Use WebSocket at `ws://localhost:8888/ws/agent/stream`
