import { useState, useRef, useEffect } from 'react'
import MessageItem from './MessageItem'
import '../styles/Chat.css'

function Chat({ messages, onSendMessage, onClearHistory, onStopAgent, agentStatus }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim()) {
      onSendMessage(input)
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Chat</h2>
        <div className="chat-actions">
          {agentStatus === 'running' && (
            <button onClick={onStopAgent} className="btn btn-warning">
              Stop Agent
            </button>
          )}
          <button onClick={onClearHistory} className="btn btn-secondary">
            Clear History
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <p>No messages yet. Start a conversation!</p>
            <p className="chat-hint">
              Try: "Open Chrome and navigate to google.com"
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageItem key={index} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message (Shift+Enter for new line)..."
          className="chat-input"
          rows="3"
          disabled={agentStatus === 'running'}
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={!input.trim() || agentStatus === 'running'}
        >
          Send
        </button>
      </form>

      {agentStatus === 'running' && (
        <div className="agent-status-bar">
          <span className="spinner" />
          Agent is processing...
        </div>
      )}
    </div>
  )
}

export default Chat
