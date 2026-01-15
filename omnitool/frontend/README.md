# OmniParser Frontend

Modern React frontend for OmniParser with real-time WebSocket communication.

## Quick Start

```bash
# Install dependencies
cd omnitool/frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Development

```bash
# Start backend (in another terminal)
cd omnitool/backend
python -m uvicorn main:app --reload --port 8888

# Start frontend dev server
cd omnitool/frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

## Architecture

```
omnitool/frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Chat.jsx        # Chat interface
│   │   ├── MessageItem.jsx # Message display
│   │   ├── Settings.jsx    # Settings panel
│   │   └── VNCViewer.jsx   # Windows VM viewer
│   ├── api/                 # API clients
│   │   ├── client.js       # REST API client
│   │   └── websocket.js    # WebSocket client
│   ├── styles/              # CSS modules
│   │   ├── index.css       # Global styles
│   │   ├── App.css         # App layout
│   │   ├── Chat.css        # Chat styles
│   │   ├── MessageItem.css # Message styles
│   │   ├── Settings.css    # Settings styles
│   │   └── VNCViewer.css   # VNC viewer styles
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
├── public/                  # Static assets
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
└── package.json             # Dependencies
```

## Features

### ✅ Real-Time Communication
- WebSocket connection for bidirectional agent communication
- Automatic reconnection with exponential backoff
- Message queuing during disconnection

### ✅ Chat Interface
- Message history with sender identification
- Rich message rendering (HTML, images, code blocks)
- Auto-scroll to latest message
- Clear history functionality

### ✅ Settings Panel
- Model selection (Cloud API + Local LLMs)
- Provider auto-selection
- API key management
- Max tokens and screenshot controls
- Agent status display

### ✅ Windows VM Viewer
- Embedded noVNC viewer
- Real-time screen viewing
- Fullscreen support

### ✅ Responsive Design
- Desktop-first layout (3-column grid)
- Tablet support (2-column grid)
- Mobile support (single column)
- Dark mode support

## API Communication

### REST API Endpoints

```javascript
import apiClient from './api/client'

// Chat
await apiClient.sendMessage("Click the button")
await apiClient.getChatHistory()
await apiClient.clearChatHistory()

// Agent
await apiClient.startAgent({ model, provider, api_key })
await apiClient.stopAgent()
await apiClient.getAgentStatus()

// Settings
await apiClient.getSettings()
await apiClient.updateSettings({ model: "new-model" })
```

### WebSocket Protocol

```javascript
import wsClient from './api/websocket'

// Connect
await wsClient.connect()

// Send message
wsClient.sendMessage("Open Chrome")

// Listen for messages
wsClient.onMessage((message) => {
  switch (message.type) {
    case 'agent_message':
      // Handle agent response
      break
    case 'tool_result':
      // Handle tool execution result
      break
    case 'status':
      // Handle status update
      break
    case 'error':
      // Handle error
      break
  }
})

// Disconnect
wsClient.disconnect()
```

## Environment Variables

Create `.env` file in `omnitool/frontend/`:

```bash
# Backend API URL (default: http://localhost:8888)
VITE_API_URL=http://localhost:8888

# WebSocket URL (default: ws://localhost:8888)
VITE_WS_URL=ws://localhost:8888
```

## Building for Production

```bash
# Build
npm run build

# Preview
npm run preview

# Output directory
dist/
```

The built files can be served by the FastAPI backend:

```python
# Backend automatically serves frontend from omnitool/frontend/dist
```

## Styling

- CSS Variables for theming
- Dark mode support via `prefers-color-scheme`
- Responsive breakpoints:
  - Desktop: > 1280px (3-column)
  - Tablet: 768px - 1280px (2-column)
  - Mobile: < 768px (single column)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Android)

## Development Tips

### Hot Reload

Vite provides instant hot module replacement (HMR):
- Save any file → instant update in browser
- WebSocket connection persists during HMR
- State is preserved when possible

### API Proxy

Vite proxies API requests during development:

```javascript
// In code, use relative URLs:
fetch('/api/chat/history')

// Vite automatically proxies to http://localhost:8888/api/chat/history
```

### WebSocket Debugging

```javascript
// Enable WebSocket logging
wsClient.ws.onmessage = (event) => {
  console.log('[WS]', JSON.parse(event.data))
}
```

## Troubleshooting

### "WebSocket not connected"
- Ensure backend is running on port 8888
- Check browser console for connection errors
- Verify CORS settings in backend

### "API request failed"
- Verify backend is running
- Check network tab in browser DevTools
- Ensure VITE_API_URL is correct

### Styles not loading
- Clear browser cache
- Run `npm run dev` again
- Check CSS file imports in components

## Next Steps

1. **Customize UI**: Modify styles in `src/styles/`
2. **Add features**: Create new components in `src/components/`
3. **Extend API**: Add new endpoints in `src/api/client.js`
4. **Deploy**: Build and serve from FastAPI backend

## Security Notes

- CORS is configured for `localhost:5173` in development
- Update backend CORS settings for production domains
- Never commit API keys to git
- Use HTTPS in production

## Contributing

See [FRONTEND_BACKEND_ARCHITECTURE.md](../../docs/FRONTEND_BACKEND_ARCHITECTURE.md) for full architecture details.
