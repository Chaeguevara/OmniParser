import '../styles/MessageItem.css'

function MessageItem({ message }) {
  const { content, sender, timestamp } = message

  const formatTime = (isoString) => {
    try {
      const date = new Date(isoString)
      return date.toLocaleTimeString()
    } catch {
      return ''
    }
  }

  const getSenderLabel = (sender) => {
    switch (sender) {
      case 'user':
        return 'You'
      case 'bot':
      case 'assistant':
        return 'Agent'
      case 'tool':
        return 'Tool'
      case 'system':
        return 'System'
      default:
        return sender
    }
  }

  const getSenderClass = (sender) => {
    switch (sender) {
      case 'user':
        return 'message-user'
      case 'bot':
      case 'assistant':
        return 'message-agent'
      case 'tool':
        return 'message-tool'
      case 'system':
        return 'message-system'
      default:
        return 'message-default'
    }
  }

  // Check if content contains HTML (screenshots, etc.)
  const isHTML = content.includes('<img') || content.includes('<details>')

  return (
    <div className={`message ${getSenderClass(sender)}`}>
      <div className="message-header">
        <span className="message-sender">{getSenderLabel(sender)}</span>
        <span className="message-time">{formatTime(timestamp)}</span>
      </div>
      <div className="message-content">
        {isHTML ? (
          <div dangerouslySetInnerHTML={{ __html: content }} />
        ) : (
          <p>{content}</p>
        )}
      </div>
    </div>
  )
}

export default MessageItem
