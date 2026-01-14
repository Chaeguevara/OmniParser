"""
Pydantic models for API request/response validation
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# Chat Models
class ChatMessage(BaseModel):
    """Chat message model"""
    content: str = Field(..., min_length=1, description="Message content")
    role: Literal["user", "assistant", "tool"] = Field(..., description="Message role")
    timestamp: Optional[datetime] = None


class ChatMessageRequest(BaseModel):
    """Request to send a chat message"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")


class ChatMessageResponse(BaseModel):
    """Response containing agent's message"""
    message: str
    sender: Literal["bot", "tool"]
    timestamp: datetime


class ChatHistoryResponse(BaseModel):
    """Response containing chat history"""
    messages: List[ChatMessage]
    total: int


# Agent Models
class AgentStartRequest(BaseModel):
    """Request to start agent with configuration"""
    model: str = Field(..., description="Model name")
    provider: str = Field(..., description="API provider")
    api_key: Optional[str] = Field(None, description="API key")
    max_tokens: int = Field(4096, ge=256, le=8192, description="Max tokens")
    only_n_images: int = Field(2, ge=0, le=10, description="Number of recent screenshots")


class AgentStopRequest(BaseModel):
    """Request to stop agent"""
    pass


class AgentStatusResponse(BaseModel):
    """Response containing agent status"""
    status: Literal["idle", "running", "error"]
    model: Optional[str] = None
    provider: Optional[str] = None
    token_usage: int = 0
    cost: float = 0.0


# Settings Models
class Settings(BaseModel):
    """Application settings"""
    model: str = "omniparser + gpt-4o"
    provider: str = "openai"
    api_key: Optional[str] = None
    max_tokens: int = 4096
    only_n_images: int = 2
    windows_host_url: str = "localhost:8006"
    omniparser_server_url: str = "localhost:8000"


class SettingsUpdateRequest(BaseModel):
    """Request to update settings"""
    model: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=256, le=8192)
    only_n_images: Optional[int] = Field(None, ge=0, le=10)
    windows_host_url: Optional[str] = None
    omniparser_server_url: Optional[str] = None


# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: Literal["agent_message", "tool_result", "screenshot", "error", "user_message", "status"]
    data: dict


class WebSocketUserMessage(BaseModel):
    """User message sent via WebSocket"""
    type: Literal["user_message"] = "user_message"
    content: str = Field(..., min_length=1, max_length=10000)
