"""
Agent Router

Handles agent control REST API endpoints
"""

from fastapi import APIRouter, HTTPException
from omnitool.backend.models import (
    AgentStartRequest,
    AgentStopRequest,
    AgentStatusResponse
)
from omnitool.backend.services.agent_service import agent_service

router = APIRouter()


@router.post("/start")
async def start_agent(request: AgentStartRequest):
    """
    Start the agent with specified configuration

    Note: The actual agent loop runs via WebSocket connection.
    This endpoint prepares the agent for execution.
    """
    try:
        agent_service.start(
            model=request.model,
            provider=request.provider,
            api_key=request.api_key,
            max_tokens=request.max_tokens,
            only_n_images=request.only_n_images
        )
        return {
            "message": "Agent started successfully",
            "status": "running"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")


@router.post("/stop")
async def stop_agent(request: AgentStopRequest):
    """Stop the agent"""
    try:
        agent_service.stop()
        return {
            "message": "Agent stopped successfully",
            "status": "idle"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")


@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """Get current agent status"""
    status = agent_service.get_status()
    return AgentStatusResponse(**status)
