# Frontend/Backend Architecture Migration

## Overview

This document outlines the plan to migrate from Gradio-based UI to a Node.js-based frontend (React/Vanilla JS) with proper frontend/backend separation.

## Problem Statement

### Current Architecture Issues

1. **Gradio Security Concerns**
   - Gradio makes external calls to gradio.app servers to check versions
   - Version checking behavior cannot be fully disabled
   - Creates security vulnerabilities in air-gapped/secured corporate environments
   - Network traffic to external domains is blocked by enterprise firewalls

2. **Tight Coupling**
   - Current architecture mixes UI and business logic
   - Gradio components are tightly coupled with agent orchestration
   - Difficult to customize UI without modifying agent code

3. **Limited Customization**
   - Gradio provides pre-built components with limited styling
   - Hard to implement custom UI/UX requirements
   - Mobile responsiveness is suboptimal

## Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Gradio Frontend (app.py)                 │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │   Chat UI  │  │  Settings  │  │  VNC Viewer (iframe)│   │
│  └────────────┘  └────────────┘  └─────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │      Agent Orchestration (loop.py)                   │    │
│  │  - AnthropicActor / VLMAgent                         │    │
│  │  - AnthropicExecutor                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────┬──────────────────────┬──────────────────────┘
                │                       │
                ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  OmniParser Server       │  │  Windows VM (Flask)      │
│  FastAPI (port 8000)     │  │  Computer Control        │
│  - /parse endpoint       │  │  (port 5000)             │
└──────────────────────────┘  └──────────────────────────┘
```

## Proposed Architecture

```
┌───────────────────────────────────────────────────────┐
│           Node.js Frontend (React/Vanilla JS)         │
│  ┌────────────┐  ┌────────────┐  ┌───────────────┐   │
│  │   Chat UI  │  │  Settings  │  │  VNC Viewer   │   │
│  │  (React)   │  │  (React)   │  │  (noVNC)      │   │
│  └────────────┘  └────────────┘  └───────────────┘   │
│                                                         │
│  Communication: REST API + WebSocket                   │
└────────────────┬──────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API Server (FastAPI)               │
│  ┌────────────────────────────────────────────────┐    │
│  │          REST API Endpoints                     │    │
│  │  - POST /api/chat/message                       │    │
│  │  - GET  /api/chat/history                       │    │
│  │  - POST /api/agent/start                        │    │
│  │  - POST /api/agent/stop                         │    │
│  │  - GET  /api/settings                           │    │
│  │  - POST /api/settings                           │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │          WebSocket Endpoint                     │    │
│  │  - /ws/agent/stream (real-time updates)        │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │      Agent Orchestration (loop.py)              │    │
│  │  - AnthropicActor / VLMAgent                    │    │
│  │  - AnthropicExecutor                            │    │
│  └────────────────────────────────────────────────┘    │
└──────────────┬──────────────────────┬──────────────────┘
               │                       │
               ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  OmniParser Server       │  │  Windows VM (Flask)      │
│  FastAPI (port 8000)     │  │  Computer Control        │
│  - /parse endpoint       │  │  (port 5000)             │
└──────────────────────────┘  └──────────────────────────┘
```

## Detailed Design

### 1. Backend API Server (FastAPI)

**File Structure:**
```
omnitool/
├── backend/
│   ├── main.py                  # FastAPI app with all endpoints
│   ├── routers/
│   │   ├── chat.py              # Chat endpoints
│   │   ├── agent.py             # Agent control endpoints
│   │   ├── settings.py          # Settings endpoints
│   │   └── websocket.py         # WebSocket endpoint
│   ├── services/
│   │   ├── agent_service.py     # Agent orchestration logic
│   │   └── chat_service.py      # Chat history management
│   └── models/
│       └── schemas.py           # Pydantic models for API
```

**API Endpoints:**

```python
# Chat Endpoints
POST   /api/chat/message          # Send message to agent
GET    /api/chat/history          # Get chat history
DELETE /api/chat/history          # Clear chat history

# Agent Control Endpoints
POST   /api/agent/start           # Start agent loop
POST   /api/agent/stop            # Stop agent loop
GET    /api/agent/status          # Get agent status

# Settings Endpoints
GET    /api/settings              # Get current settings
POST   /api/settings              # Update settings

# WebSocket Endpoint
WS     /ws/agent/stream           # Real-time agent updates
```

**WebSocket Message Format:**
```json
{
  "type": "agent_message" | "tool_result" | "screenshot" | "error",
  "data": {
    "content": "...",
    "sender": "bot" | "tool",
    "timestamp": "2025-01-14T12:00:00Z"
  }
}
```

### 2. Frontend (React or Vanilla JS)

**File Structure:**
```
omnitool/
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── index.html
│   │   ├── main.js              # Entry point
│   │   ├── api/
│   │   │   ├── client.js        # REST API client
│   │   │   └── websocket.js     # WebSocket client
│   │   ├── components/
│   │   │   ├── Chat.js          # Chat interface
│   │   │   ├── Settings.js      # Settings panel
│   │   │   ├── VNCViewer.js     # noVNC viewer
│   │   │   └── MessageItem.js   # Chat message component
│   │   └── styles/
│   │       └── main.css
│   └── vite.config.js           # Build config (if using Vite)
```

**Technology Stack Options:**

**Option A: React + Vite (Recommended)**
- Modern, fast development
- Component reusability
- Rich ecosystem

**Option B: Vanilla JS + Vite**
- No framework overhead
- Direct DOM manipulation
- Lightweight

**Option C: Svelte + Vite**
- Compile-time framework
- Smaller bundle size
- Excellent performance

### 3. Communication Protocol

**REST API for:**
- Chat history retrieval
- Settings management
- Agent start/stop control

**WebSocket for:**
- Real-time agent messages
- Tool execution results
- Screenshot updates
- Error notifications

**Example WebSocket Client:**
```javascript
class AgentWebSocket {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.ws.onmessage = this.handleMessage.bind(this);
  }

  handleMessage(event) {
    const message = JSON.parse(event.data);
    switch(message.type) {
      case 'agent_message':
        this.onAgentMessage(message.data);
        break;
      case 'tool_result':
        this.onToolResult(message.data);
        break;
      case 'screenshot':
        this.onScreenshot(message.data);
        break;
      case 'error':
        this.onError(message.data);
        break;
    }
  }

  sendMessage(content) {
    this.ws.send(JSON.stringify({
      type: 'user_message',
      content: content
    }));
  }
}
```

## Migration Plan

### Phase 1: Backend API Implementation (Week 1-2)

1. **Create FastAPI backend structure**
   - Set up routers for chat, agent, settings
   - Implement WebSocket endpoint
   - Migrate agent orchestration logic from Gradio callbacks

2. **Implement REST API endpoints**
   - Chat message handling
   - Settings CRUD operations
   - Agent control (start/stop/status)

3. **Implement WebSocket streaming**
   - Real-time message streaming
   - Tool result streaming
   - Error handling

4. **Testing**
   - Unit tests for API endpoints
   - Integration tests with agent orchestration
   - WebSocket connection testing

### Phase 2: Frontend Implementation (Week 2-3)

1. **Set up frontend project**
   - Choose technology stack (React/Vanilla JS/Svelte)
   - Set up build system (Vite)
   - Configure dev server with proxy to backend

2. **Implement core components**
   - Chat interface with message list
   - Message input with submit button
   - Settings panel with dropdowns
   - VNC viewer integration (noVNC)

3. **Implement API client**
   - REST API client with fetch/axios
   - WebSocket client for real-time updates
   - Error handling and reconnection logic

4. **Styling and UX**
   - Responsive design
   - Dark/light theme support
   - Loading states and error messages

### Phase 3: Integration and Testing (Week 3-4)

1. **Integration testing**
   - End-to-end testing with Playwright/Cypress
   - Test chat flow with real agent
   - Test settings persistence
   - Test WebSocket reconnection

2. **Performance optimization**
   - Bundle size optimization
   - API response caching
   - WebSocket message batching

3. **Documentation**
   - API documentation (OpenAPI/Swagger)
   - Frontend setup instructions
   - Deployment guide

### Phase 4: Deployment (Week 4)

1. **Production build**
   - Build frontend with minification
   - Set up static file serving from FastAPI
   - Configure CORS for security

2. **Docker configuration**
   - Update Dockerfile for backend + frontend
   - Docker compose for full stack
   - Environment variable configuration

## Security Considerations

### 1. Gradio Removal Benefits

- ✅ No external calls to gradio.app servers
- ✅ Full control over network traffic
- ✅ Air-gapped deployment support
- ✅ Corporate firewall compatibility

### 2. API Security

- Use CORS properly to restrict origins
- Implement rate limiting (slowapi)
- Add authentication if needed (JWT tokens)
- Validate all inputs with Pydantic

### 3. WebSocket Security

- Implement connection authentication
- Add message rate limiting
- Validate message format
- Handle connection timeouts

## Performance Considerations

### 1. Frontend

- Code splitting for faster initial load
- Lazy loading for heavy components
- Virtual scrolling for long chat history
- Image optimization for screenshots

### 2. Backend

- WebSocket connection pooling
- Message queuing for high load
- Database for persistent chat history (optional)
- Caching for repeated requests

## Advantages of New Architecture

| Aspect | Gradio (Current) | Node.js Frontend (Proposed) |
|--------|------------------|------------------------------|
| **Security** | External calls to gradio.app | ✅ No external dependencies |
| **Air-gapped Support** | ❌ Not supported | ✅ Fully supported |
| **Customization** | Limited | ✅ Full control |
| **Performance** | Moderate | ✅ Optimized bundles |
| **Mobile Support** | Limited | ✅ Responsive design |
| **Deployment** | Single Python app | Backend + Static frontend |
| **Technology Debt** | Coupled to Gradio | ✅ Standard web stack |

## Backward Compatibility

During migration, both systems can coexist:

1. Keep Gradio app as `app_gradio.py`
2. New backend as `app_backend.py`
3. Users can choose which to run
4. Deprecate Gradio after frontend is stable

## Estimated Effort

| Phase | Effort | Priority |
|-------|--------|----------|
| Phase 1: Backend API | 2 weeks | High |
| Phase 2: Frontend | 1.5 weeks | High |
| Phase 3: Integration | 1 week | High |
| Phase 4: Deployment | 0.5 weeks | Medium |
| **Total** | **5 weeks** | |

## Next Steps

1. **Get approval** for architecture approach
2. **Choose frontend technology** (React/Vanilla JS/Svelte)
3. **Start Phase 1** - Backend API implementation
4. **Prototype frontend** with mock data
5. **Integration testing** with real agent

## Related Documentation

- [API.md](API.md) - Current REST API reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system design
- [LOCAL_LLM.md](LOCAL_LLM.md) - Local LLM integration
- [EXTENDING.md](EXTENDING.md) - Adding new features

## Questions?

For implementation questions or clarifications, please open an issue or discussion in the repository.
