"""
Agent Service

Manages agent lifecycle and orchestration, migrated from Gradio app.py
"""

import asyncio
from typing import Optional, Callable
from datetime import datetime
import sys
from pathlib import Path

# Add gradio dir to path to import existing agent code
gradio_dir = Path(__file__).parent.parent.parent / "gradio"
sys.path.insert(0, str(gradio_dir))

from loop import sampling_loop_sync, APIProvider


class AgentService:
    """Manages agent lifecycle and state"""

    def __init__(self):
        self.status = "idle"
        self.model: Optional[str] = None
        self.provider: Optional[str] = None
        self.api_key: Optional[str] = None
        self.max_tokens: int = 4096
        self.only_n_images: int = 2
        self.messages = []
        self.token_usage = 0
        self.cost = 0.0
        self.stop_requested = False

        # Callbacks for WebSocket streaming
        self.output_callback: Optional[Callable] = None
        self.tool_output_callback: Optional[Callable] = None
        self.api_response_callback: Optional[Callable] = None

    def set_callbacks(
        self,
        output_callback: Callable,
        tool_output_callback: Callable,
        api_response_callback: Callable
    ):
        """Set callbacks for streaming outputs to WebSocket"""
        self.output_callback = output_callback
        self.tool_output_callback = tool_output_callback
        self.api_response_callback = api_response_callback

    def start(
        self,
        model: str,
        provider: str,
        api_key: str,
        max_tokens: int = 4096,
        only_n_images: int = 2,
        user_message: str = ""
    ):
        """Start agent with configuration"""
        if self.status == "running":
            raise ValueError("Agent is already running")

        self.model = model
        self.provider = provider
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.only_n_images = only_n_images
        self.status = "running"
        self.stop_requested = False

        # Add user message to history
        if user_message:
            self.messages.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })

    async def run_agent_loop(
        self,
        windows_host_url: str = "localhost:8006",
        omniparser_server_url: str = "localhost:8000"
    ):
        """Run the agent orchestration loop"""
        try:
            # Convert provider string to enum
            provider_enum = APIProvider(self.provider)

            # Run sampling loop (this will call callbacks)
            for message in sampling_loop_sync(
                model=self.model,
                provider=provider_enum,
                api_key=self.api_key,
                messages=self.messages,
                output_callback=self.output_callback or self._default_callback,
                tool_output_callback=self.tool_output_callback or self._default_callback,
                api_response_callback=self.api_response_callback or self._default_callback,
                max_tokens=self.max_tokens,
                only_n_most_recent_images=self.only_n_images,
                windows_host_url=windows_host_url,
                omniparser_server_url=omniparser_server_url
            ):
                # Check if stop was requested
                if self.stop_requested:
                    break

                # Yield control to allow other coroutines to run
                await asyncio.sleep(0)

            self.status = "idle"
        except Exception as e:
            self.status = "error"
            if self.output_callback:
                self.output_callback(f"Error: {str(e)}", sender="bot")
            raise

    def stop(self):
        """Stop the agent"""
        self.stop_requested = True
        self.status = "idle"

    def get_status(self):
        """Get current agent status"""
        return {
            "status": self.status,
            "model": self.model,
            "provider": self.provider,
            "token_usage": self.token_usage,
            "cost": self.cost
        }

    def clear_history(self):
        """Clear chat history"""
        self.messages = []
        self.token_usage = 0
        self.cost = 0.0

    def _default_callback(self, message: str, sender: str = "bot"):
        """Default callback if none set"""
        print(f"[{sender}] {message}")


# Global agent service instance
agent_service = AgentService()
