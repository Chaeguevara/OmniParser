"""
Chat Router

Handles chat-related REST API endpoints
"""

from fastapi import APIRouter, HTTPException
from omnitool.backend.models import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse
)
from omnitool.backend.services.chat_service import chat_service
from datetime import datetime

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Send a message to the agent

    Note: This is a simplified endpoint. In practice, you would use WebSocket
    for real-time bidirectional communication with the agent.
    """
    # Add message to history
    chat_service.add_message(request.message, role="user")

    # Return acknowledgment (actual agent response comes via WebSocket)
    return ChatMessageResponse(
        message="Message received. Connect to WebSocket for agent response.",
        sender="bot",
        timestamp=datetime.now()
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_history():
    """Get chat history"""
    history = chat_service.get_history()
    return ChatHistoryResponse(
        messages=history["messages"],
        total=history["total"]
    )


@router.delete("/history")
async def clear_history():
    """Clear chat history"""
    chat_service.clear_history()
    return {"message": "Chat history cleared successfully"}
