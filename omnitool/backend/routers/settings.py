"""
Settings Router

Handles settings-related REST API endpoints
"""

from fastapi import APIRouter, HTTPException
from omnitool.backend.models import Settings, SettingsUpdateRequest
from omnitool.backend.services.settings_service import settings_service

router = APIRouter()


@router.get("/", response_model=Settings)
async def get_settings():
    """Get current application settings"""
    return settings_service.get_settings()


@router.post("/", response_model=Settings)
async def update_settings(request: SettingsUpdateRequest):
    """Update application settings"""
    try:
        # Convert request to dict, excluding None values
        updates = request.dict(exclude_none=True)
        updated_settings = settings_service.update_settings(updates)
        return updated_settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
