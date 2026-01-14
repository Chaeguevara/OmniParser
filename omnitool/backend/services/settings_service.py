"""
Settings Service

Manages application settings
"""

from omnitool.backend.models.schemas import Settings


class SettingsService:
    """Manages application settings"""

    def __init__(self):
        # Default settings
        self.settings = Settings(
            model="omniparser + gpt-4o",
            provider="openai",
            api_key=None,
            max_tokens=4096,
            only_n_images=2,
            windows_host_url="localhost:8006",
            omniparser_server_url="localhost:8000"
        )

    def get_settings(self) -> Settings:
        """Get current settings"""
        return self.settings

    def update_settings(self, updates: dict) -> Settings:
        """Update settings with provided values"""
        for key, value in updates.items():
            if value is not None and hasattr(self.settings, key):
                setattr(self.settings, key, value)
        return self.settings


# Global settings service instance
settings_service = SettingsService()
