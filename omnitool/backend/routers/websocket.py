"""
WebSocket Router

Handles real-time bidirectional communication with agent
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from omnitool.backend.services.agent_service import agent_service
from omnitool.backend.services.chat_service import chat_service
from omnitool.backend.services.settings_service import settings_service
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/agent/stream")
async def websocket_agent_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent communication

    Message format (from client):
    {
        "type": "user_message",
        "content": "user message here"
    }

    Message format (to client):
    {
        "type": "agent_message" | "tool_result" | "screenshot" | "error" | "status",
        "data": {...}
    }
    """
    await manager.connect(websocket)

    try:
        # Set up callbacks for agent to send messages via WebSocket
        def output_callback(message: str, sender: str = "bot"):
            """Callback for agent output"""
            asyncio.create_task(manager.send_message({
                "type": "agent_message",
                "data": {
                    "content": message,
                    "sender": sender,
                    "timestamp": datetime.now().isoformat()
                }
            }, websocket))

        def tool_output_callback(message: str, sender: str = "tool"):
            """Callback for tool output"""
            asyncio.create_task(manager.send_message({
                "type": "tool_result",
                "data": {
                    "content": message,
                    "sender": sender,
                    "timestamp": datetime.now().isoformat()
                }
            }, websocket))

        def api_response_callback(response):
            """Callback for API responses"""
            # Send status updates
            asyncio.create_task(manager.send_message({
                "type": "status",
                "data": {
                    "status": "processing",
                    "timestamp": datetime.now().isoformat()
                }
            }, websocket))

        # Set callbacks on agent service
        agent_service.set_callbacks(
            output_callback=output_callback,
            tool_output_callback=tool_output_callback,
            api_response_callback=api_response_callback
        )

        # Send initial connection message
        await manager.send_message({
            "type": "status",
            "data": {
                "status": "connected",
                "message": "WebSocket connected successfully",
                "timestamp": datetime.now().isoformat()
            }
        }, websocket)

        # Listen for messages from client
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "user_message":
                content = message.get("content", "")

                # Add to chat history
                chat_service.add_message(content, role="user")

                # Send acknowledgment
                await manager.send_message({
                    "type": "status",
                    "data": {
                        "status": "message_received",
                        "timestamp": datetime.now().isoformat()
                    }
                }, websocket)

                # Get current settings
                settings = settings_service.get_settings()

                # Start agent if not running
                if agent_service.status != "running":
                    agent_service.start(
                        model=settings.model,
                        provider=settings.provider,
                        api_key=settings.api_key or "",
                        max_tokens=settings.max_tokens,
                        only_n_images=settings.only_n_images,
                        user_message=content
                    )

                    # Run agent loop in background
                    asyncio.create_task(agent_service.run_agent_loop(
                        windows_host_url=settings.windows_host_url,
                        omniparser_server_url=settings.omniparser_server_url
                    ))
                else:
                    # Agent already running, just add message to queue
                    agent_service.messages.append({
                        "role": "user",
                        "content": content,
                        "timestamp": datetime.now().isoformat()
                    })

            elif message.get("type") == "stop_agent":
                # Stop agent
                agent_service.stop()
                await manager.send_message({
                    "type": "status",
                    "data": {
                        "status": "stopped",
                        "message": "Agent stopped",
                        "timestamp": datetime.now().isoformat()
                    }
                }, websocket)

            elif message.get("type") == "clear_history":
                # Clear chat history
                chat_service.clear_history()
                agent_service.clear_history()
                await manager.send_message({
                    "type": "status",
                    "data": {
                        "status": "history_cleared",
                        "message": "Chat history cleared",
                        "timestamp": datetime.now().isoformat()
                    }
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # Stop agent if running
        if agent_service.status == "running":
            agent_service.stop()
    except Exception as e:
        await manager.send_message({
            "type": "error",
            "data": {
                "message": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        }, websocket)
        manager.disconnect(websocket)
