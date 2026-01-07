"""
Ollama client for local LLM inference.

Ollama provides OpenAI-compatible API, so we reuse the OAI client implementation.
Default Ollama server runs at http://localhost:11434
"""
import os
from .oaiclient import run_oai_interleaved


def run_ollama_interleaved(
    messages: list,
    system: str,
    model_name: str,
    api_key: str = "ollama",  # Ollama doesn't require API key, but keep for consistency
    max_tokens: int = 256,
    temperature: float = 0,
    ollama_base_url: str = None
):
    """
    Run chat completion through Ollama's OpenAI-compatible API.

    Args:
        messages: List of message dicts or strings
        system: System prompt
        model_name: Ollama model name (e.g., "llama3.2-vision", "qwen2.5-vl")
        api_key: Not used by Ollama, but kept for API consistency
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        ollama_base_url: Custom Ollama server URL (default: http://localhost:11434/v1)

    Returns:
        Tuple of (response_text, token_usage)

    Notes:
        - Ollama must be running locally: `ollama serve`
        - Install models: `ollama pull llama3.2-vision`
        - Vision-capable models: llama3.2-vision, llava, qwen2.5-vl, bakllava
    """
    # Get Ollama base URL from environment or use default
    if ollama_base_url is None:
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    # Ollama doesn't require authentication, but API expects a key
    # Use dummy key if not provided
    if not api_key or api_key == "":
        api_key = "ollama"

    try:
        return run_oai_interleaved(
            messages=messages,
            system=system,
            model_name=model_name,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
            provider_base_url=ollama_base_url
        )
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        print(f"Make sure Ollama is running at {ollama_base_url}")
        print(f"Start Ollama with: ollama serve")
        print(f"Pull model with: ollama pull {model_name}")
        return str(e), 0


def list_ollama_models(ollama_base_url: str = None):
    """
    List available Ollama models.

    Returns:
        List of model names
    """
    import requests

    if ollama_base_url is None:
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    try:
        # Ollama's native API endpoint (not OpenAI-compatible)
        response = requests.get(f"{ollama_base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        else:
            print(f"Failed to list Ollama models: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error listing Ollama models: {e}")
        return []
