"""
Backend API Server for OmniParser

Replaces Gradio with FastAPI REST + WebSocket API for frontend/backend separation.

Usage:
    python -m uvicorn omnitool.backend.main:app --host 0.0.0.0 --port 8888 --reload
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from omnitool.backend.routers import chat, agent, settings, websocket as ws

app = FastAPI(
    title="OmniParser API",
    description="Backend API for OmniParser - AI agent with UI automation",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(ws.router, prefix="/ws", tags=["WebSocket"])

# Mount static files (frontend build) for production
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "omniparser-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
