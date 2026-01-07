"""
Hugging Face client for local and cloud LLM inference.

Supports:
1. Hugging Face Inference API (cloud)
2. Text Generation Inference (TGI) server (local)
3. Hugging Face Inference Endpoints (custom)

All use OpenAI-compatible API format.
"""
import os
from .oaiclient import run_oai_interleaved


def run_hf_interleaved(
    messages: list,
    system: str,
    model_name: str,
    api_key: str = None,
    max_tokens: int = 256,
    temperature: float = 0,
    hf_base_url: str = None
):
    """
    Run chat completion through Hugging Face API.

    Args:
        messages: List of message dicts or strings
        system: System prompt
        model_name: HF model name (e.g., "meta-llama/Llama-3.2-11B-Vision-Instruct")
        api_key: Hugging Face API token (get from https://huggingface.co/settings/tokens)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        hf_base_url: Custom HF endpoint URL. Options:
            - None: Use HF Inference API (default)
            - "http://localhost:8080/v1": Local TGI server
            - "https://your-endpoint.aws.endpoints.huggingface.cloud/v1": Custom endpoint

    Returns:
        Tuple of (response_text, token_usage)

    Notes:
        **Cloud (Hugging Face Inference API)**:
        - Get API token: https://huggingface.co/settings/tokens
        - Free tier available with rate limits
        - Supports many models including vision models

        **Local (Text Generation Inference)**:
        - Install: `pip install text-generation-inference`
        - Run server: `text-generation-launcher --model-id meta-llama/Llama-3.2-11B-Vision-Instruct`
        - Or Docker: `docker run --gpus all -p 8080:80 ghcr.io/huggingface/text-generation-inference:latest --model-id meta-llama/Llama-3.2-11B-Vision-Instruct`

        **Vision Models on HF**:
        - meta-llama/Llama-3.2-11B-Vision-Instruct
        - meta-llama/Llama-3.2-90B-Vision-Instruct
        - Qwen/Qwen2-VL-7B-Instruct
        - microsoft/Phi-3.5-vision-instruct
    """
    # Determine base URL
    if hf_base_url is None:
        # Use HF Inference API (cloud)
        hf_base_url = os.environ.get("HF_BASE_URL", "https://api-inference.huggingface.co/models")
        # Append model name to URL for Inference API
        if not hf_base_url.endswith("/v1"):
            hf_base_url = f"{hf_base_url}/{model_name}/v1"

    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.environ.get("HF_API_TOKEN") or os.environ.get("HUGGINGFACE_API_TOKEN")

    if not api_key and "localhost" not in hf_base_url:
        raise ValueError(
            "Hugging Face API token required for cloud inference. "
            "Get token at https://huggingface.co/settings/tokens and set HF_API_TOKEN environment variable."
        )

    # For local TGI servers, API key is optional
    if api_key is None:
        api_key = "hf"

    try:
        return run_oai_interleaved(
            messages=messages,
            system=system,
            model_name=model_name,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
            provider_base_url=hf_base_url
        )
    except Exception as e:
        print(f"Error connecting to Hugging Face: {e}")
        if "localhost" in hf_base_url:
            print(f"Make sure TGI server is running at {hf_base_url}")
            print(f"Start TGI with: text-generation-launcher --model-id {model_name}")
        else:
            print(f"Make sure HF_API_TOKEN is set correctly")
            print(f"Get token at: https://huggingface.co/settings/tokens")
        return str(e), 0


def run_hf_tgi_interleaved(
    messages: list,
    system: str,
    model_name: str,
    max_tokens: int = 256,
    temperature: float = 0,
    tgi_base_url: str = "http://localhost:8080/v1"
):
    """
    Convenience function for local TGI server.

    Args:
        messages: List of message dicts or strings
        system: System prompt
        model_name: Model name (used for reference, TGI server already has model loaded)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        tgi_base_url: TGI server URL (default: http://localhost:8080/v1)

    Returns:
        Tuple of (response_text, token_usage)
    """
    return run_hf_interleaved(
        messages=messages,
        system=system,
        model_name=model_name,
        api_key="tgi",  # TGI doesn't require API key
        max_tokens=max_tokens,
        temperature=temperature,
        hf_base_url=tgi_base_url
    )
