import { useState, useEffect } from 'react'
import Chat from './components/Chat'
import Settings from './components/Settings'
import VNCViewer from './components/VNCViewer'
import apiClient from './api/client'
import wsClient from './api/websocket'
import './styles/App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [settings, setSettings] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [agentStatus, setAgentStatus] = useState('idle')

  // Initialize WebSocket connection
  useEffect(() => {
    const initWebSocket = async () => {
      try {
        await wsClient.connect()
        setIsConnected(true)

        // Set up message handler
        const unsubscribe = wsClient.onMessage((message) => {
          handleWebSocketMessage(message)
        })

        return () => {
          unsubscribe()
          wsClient.disconnect()
        }
      } catch (error) {
        console.error('Failed to connect WebSocket:', error)
      }
    }

    initWebSocket()
  }, [])

  // Load initial settings
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const data = await apiClient.getSettings()
        setSettings(data)
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
    }

    loadSettings()
  }, [])

  const handleWebSocketMessage = (message) => {
    console.log('Received message:', message)

    switch (message.type) {
      case 'agent_message':
        setMessages(prev => [...prev, {
          content: message.data.content,
          sender: message.data.sender,
          timestamp: message.data.timestamp,
        }])
        break

      case 'tool_result':
        setMessages(prev => [...prev, {
          content: message.data.content,
          sender: 'tool',
          timestamp: message.data.timestamp,
        }])
        break

      case 'status':
        if (message.data.status === 'processing') {
          setAgentStatus('running')
        } else if (message.data.status === 'stopped') {
          setAgentStatus('idle')
        }
        break

      case 'error':
        setMessages(prev => [...prev, {
          content: `Error: ${message.data.message}`,
          sender: 'system',
          timestamp: message.data.timestamp,
        }])
        setAgentStatus('error')
        break

      default:
        console.log('Unknown message type:', message.type)
    }
  }

  const handleSendMessage = async (content) => {
    // Add user message to UI immediately
    setMessages(prev => [...prev, {
      content,
      sender: 'user',
      timestamp: new Date().toISOString(),
    }])

    // Send via WebSocket
    try {
      wsClient.sendMessage(content)
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages(prev => [...prev, {
        content: 'Failed to send message. Please check connection.',
        sender: 'system',
        timestamp: new Date().toISOString(),
      }])
    }
  }

  const handleClearHistory = async () => {
    try {
      wsClient.clearHistory()
      setMessages([])
    } catch (error) {
      console.error('Failed to clear history:', error)
    }
  }

  const handleStopAgent = async () => {
    try {
      wsClient.stopAgent()
      setAgentStatus('idle')
    } catch (error) {
      console.error('Failed to stop agent:', error)
    }
  }

  const handleSettingsUpdate = async (newSettings) => {
    try {
      const updated = await apiClient.updateSettings(newSettings)
      setSettings(updated)
    } catch (error) {
      console.error('Failed to update settings:', error)
    }
  }

  if (!settings) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 OmniParser</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <div className="app-content">
        <div className="left-panel">
          <Settings
            settings={settings}
            onUpdate={handleSettingsUpdate}
            agentStatus={agentStatus}
          />
        </div>

        <div className="main-panel">
          <Chat
            messages={messages}
            onSendMessage={handleSendMessage}
            onClearHistory={handleClearHistory}
            onStopAgent={handleStopAgent}
            agentStatus={agentStatus}
          />
        </div>

        <div className="right-panel">
          <VNCViewer
            windowsHostUrl={settings.windows_host_url}
          />
        </div>
      </div>
    </div>
  )
}

export default App
