"""
Chat Service

Manages chat history and message storage
"""

from typing import List, Dict
from datetime import datetime


class ChatService:
    """Manages chat history"""

    def __init__(self):
        self.messages: List[Dict] = []

    def add_message(self, content: str, role: str = "user"):
        """Add a message to history"""
        message = {
            "content": content,
            "role": role,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        return message

    def get_history(self):
        """Get all messages"""
        return {
            "messages": self.messages,
            "total": len(self.messages)
        }

    def clear_history(self):
        """Clear all messages"""
        self.messages = []


# Global chat service instance
chat_service = ChatService()
