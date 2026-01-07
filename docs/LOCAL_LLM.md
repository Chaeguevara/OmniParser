# Local LLM Setup Guide

OmniParser now supports local LLM inference through **Ollama** and **Hugging Face**, enabling:
- ✅ **Zero cloud costs** - Run completely offline
- ✅ **Data privacy** - No data leaves your machine
- ✅ **Air-gapped environments** - Works without internet
- ✅ **Custom models** - Use any vision-capable LLM

## Quick Comparison

| Provider | Setup Difficulty | GPU Required | Best For |
|----------|-----------------|--------------|----------|
| **Ollama** | Easy | Recommended | Quick local setup, beginners |
| **Hugging Face** | Medium | Recommended | Advanced users, custom models |
| OpenAI/Claude | Easy | No | Cloud API, best performance |

---

## 🚀 For Limited GPU Resources (< 8GB VRAM)

If your GPU has limited VRAM, start with these **small/distilled models**:

### Ollama (Easiest)
```bash
# 1B model - Runs on 4GB VRAM (fast but limited capability)
ollama pull llama3.2-vision:1b

# 7B model - Runs on 8GB VRAM (good balance)
ollama pull llava:7b
```

### Hugging Face
| Model | VRAM | Quality | Speed |
|-------|------|---------|-------|
| **Qwen2-VL-2B-Instruct** | 4GB | ⭐⭐⭐ | Very Fast |
| **Phi-3.5-vision-instruct** | 6GB | ⭐⭐⭐⭐ | Fast |
| **Qwen2-VL-7B-Instruct** | 8GB | ⭐⭐⭐⭐ | Medium |

**In Gradio UI**, select from dropdown:
- `omniparser + ollama/llama3.2-vision:1b` (for 4GB GPUs)
- `omniparser + ollama/llava:7b` (for 8GB GPUs)
- `omniparser + hf/Qwen/Qwen2-VL-2B-Instruct` (for 4GB GPUs)
- `omniparser + hf/microsoft/Phi-3.5-vision-instruct` (for 6GB GPUs)

---

## Option 1: Ollama (Recommended for Local)

**Ollama** provides the easiest local LLM experience with a simple installer and automatic model management.

### Installation

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download installer from https://ollama.com/download

**Verify installation:**
```bash
ollama serve  # Start Ollama server
```

### Install Vision Models

Choose and install models based on your GPU capability:

```bash
# For 12GB+ VRAM (Best quality)
ollama pull llama3.2-vision:latest   # 11B model

# For 8GB VRAM (Good balance)
ollama pull llava:7b                # 7B vision model
ollama pull qwen2-vl:7b             # 7B, excellent OCR

# For 4GB VRAM (Small, fast)
ollama pull llama3.2-vision:1b      # 1B tiny model
```

### Usage in OmniParser

1. **Start Ollama server:**
   ```bash
   ollama serve
   ```

2. **Install your chosen model:**
   ```bash
   ollama pull llama3.2-vision:latest  # Or whichever model you want
   ```

3. **Start OmniParser:**
   ```bash
   cd omnitool/gradio
   python app.py
   ```

4. **In Gradio UI:**
   - Select model from dropdown:
     - `omniparser + ollama/llama3.2-vision:latest` (11B)
     - `omniparser + ollama/llava:7b` (7B)
     - `omniparser + ollama/llama3.2-vision:1b` (1B)
     - `omniparser + ollama/qwen2-vl:7b` (7B, OCR)
   - Set API Provider: `ollama` (auto-selected)
   - API Key: Leave empty (not required for local)
   - Start chatting with your local model!

### Configuration

**Custom Ollama server URL:**
```bash
export OLLAMA_BASE_URL="http://localhost:11434/v1"
```

**List installed models:**
```bash
ollama list
```

**Remove a model:**
```bash
ollama rm llama3.2-vision
```

---

## Option 2: Hugging Face

Hugging Face provides more flexibility and access to thousands of models, but requires more setup.

### Method A: Hugging Face Inference API (Cloud)

**Setup:**
1. Get API token from https://huggingface.co/settings/tokens
2. Set environment variable:
   ```bash
   export HF_API_TOKEN="hf_your_token_here"
   ```

**Usage in OmniParser:**
- Select model: `omniparser + huggingface`
- Set API Provider: `huggingface`
- API Key: Your HF API token

**Supported models (examples):**
- `meta-llama/Llama-3.2-11B-Vision-Instruct`
- `Qwen/Qwen2-VL-7B-Instruct`
- `microsoft/Phi-3.5-vision-instruct`

### Method B: Text Generation Inference (Local Server)

**For advanced users who want to run models locally.**

**1. Install TGI:**
```bash
pip install text-generation-inference
```

**2. Start TGI server:**
```bash
# Using command line
text-generation-launcher --model-id meta-llama/Llama-3.2-11B-Vision-Instruct

# Or using Docker (recommended)
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id meta-llama/Llama-3.2-11B-Vision-Instruct
```

**3. Usage in OmniParser:**
- Select model: `omniparser + huggingface`
- Set API Provider: `huggingface`
- API Key: Can be empty for local TGI
- Set environment variable:
  ```bash
  export HF_BASE_URL="http://localhost:8080/v1"
  ```

---

## GPU Requirements

### Minimum Requirements

| Model Size | VRAM Required | Recommended GPU |
|------------|---------------|-----------------|
| 7B | 8 GB | RTX 3060 12GB, RTX 4060 |
| 11B | 12 GB | RTX 3080, RTX 4070 |
| 70B | 40 GB+ | A100, H100 (or multi-GPU) |

### CPU-Only (Slow)

Ollama and TGI support CPU inference, but it's **very slow** (30-60s per response):

```bash
# Ollama on CPU
ollama run llama3.2-vision  # Automatically uses CPU if no GPU
```

---

## Recommended Vision Models

### For Ollama

| Model | Size | VRAM | Quality | Use Case | UI Selection |
|-------|------|------|---------|----------|--------------|
| **llama3.2-vision:latest** | 11B | 12GB | ⭐⭐⭐⭐ | Best balance | `omniparser + ollama/llama3.2-vision:latest` |
| llava:7b | 7B | 8GB | ⭐⭐⭐ | Budget GPUs | `omniparser + ollama/llava:7b` |
| qwen2-vl:7b | 7B | 8GB | ⭐⭐⭐⭐ | Good OCR | `omniparser + ollama/qwen2-vl:7b` |
| llama3.2-vision:1b | 1B | 4GB | ⭐⭐ | Very limited GPU | `omniparser + ollama/llama3.2-vision:1b` |

### For Hugging Face

| Model | Size | VRAM | Quality | Use Case | UI Selection |
|-------|------|------|---------|----------|--------------|
| **Llama-3.2-11B-Vision-Instruct** | 11B | 12GB | ⭐⭐⭐⭐⭐ | Best overall | `omniparser + hf/meta-llama/Llama-3.2-11B-Vision-Instruct` |
| Qwen2-VL-7B-Instruct | 7B | 8GB | ⭐⭐⭐⭐ | Excellent OCR | `omniparser + hf/Qwen/Qwen2-VL-7B-Instruct` |
| Phi-3.5-vision-instruct | 4.2B | 6GB | ⭐⭐⭐⭐ | Very efficient | `omniparser + hf/microsoft/Phi-3.5-vision-instruct` |
| Qwen2-VL-2B-Instruct | 2B | 4GB | ⭐⭐⭐ | Low VRAM | `omniparser + hf/Qwen/Qwen2-VL-2B-Instruct` |

---

## Troubleshooting

### Ollama

**"Connection refused" error:**
```bash
# Make sure Ollama is running
ollama serve
```

**Model not found:**
```bash
# Pull the model first
ollama pull llama3.2-vision
```

**Slow inference:**
- Check GPU is being used: `nvidia-smi`
- Reduce image resolution in OmniParser settings
- Use smaller model (e.g., llava instead of llama3.2-vision)

### Hugging Face

**"Unauthorized" error:**
```bash
# Set your HF token
export HF_API_TOKEN="hf_your_token_here"
```

**TGI server crashes:**
- Check VRAM usage: `nvidia-smi`
- Model might be too large for your GPU
- Try smaller model or quantized version

**Rate limiting (Inference API):**
- Free tier has limits
- Upgrade to Pro: https://huggingface.co/pricing
- Or use local TGI instead

---

## Performance Comparison

Based on llama3.2-vision 11B model:

| Environment | Latency/Response | Cost |
|-------------|------------------|------|
| **Ollama (Local, RTX 4080)** | ~3-5s | $0 |
| **TGI (Local, RTX 4080)** | ~3-5s | $0 |
| HF Inference API (Cloud) | ~8-12s | Free tier |
| GPT-4o (Cloud) | ~2-3s | $0.0025/response |
| Claude 3.5 Sonnet (Cloud) | ~2-3s | $0.003/response |

*Latency varies based on image resolution and task complexity.*

---

## Environment Variables Reference

```bash
# Ollama
export OLLAMA_BASE_URL="http://localhost:11434/v1"

# Hugging Face
export HF_API_TOKEN="hf_your_token_here"
export HF_BASE_URL="http://localhost:8080/v1"  # For local TGI
export HUGGINGFACE_API_TOKEN="hf_your_token_here"  # Alternative to HF_API_TOKEN
```

---

## Next Steps

1. **Try Ollama first** - Easiest to get started
2. **Test with simple tasks** - "List all open windows"
3. **Adjust settings** - Reduce screenshot count if slow
4. **Compare quality** - Local vs cloud models for your use case

For questions and issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
