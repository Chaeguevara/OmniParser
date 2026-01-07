# Local LLM Setup Guide

OmniParser now supports local LLM inference through **Ollama** and **Hugging Face**, enabling:
- ✅ **Zero cloud costs** - Run completely offline
- ✅ **Data privacy** - No data leaves your machine
- ✅ **Air-gapped environments** - Works without internet
- ✅ **Custom models** - Use any LLM (text-only or vision)

## 💡 Text-Only vs Vision Models

**IMPORTANT:** OmniParser provides **structured text output** (bounding boxes, coordinates, element labels) from screenshots. The LLM receives this structured data as TEXT, not images.

**Text-only models are RECOMMENDED** because:
- ✅ **3-4x lighter:** 7-8B parameters vs 11B+ for vision models
- ✅ **Lower VRAM:** 2-4GB vs 8-12GB
- ✅ **2-3x faster inference**
- ✅ **Microsoft explicitly supports text-only models** (o1, o3-mini, R1 with OmniParser)
- ✅ **Vision capabilities are redundant** - OmniParser already parsed the UI

**Vision models are optional** for advanced use cases where you need the LLM to directly interpret raw screenshots.

## Quick Comparison

| Provider | Setup Difficulty | GPU Required | Best For |
|----------|-----------------|--------------|----------|
| **Ollama** | Easy | Recommended | Quick local setup, beginners |
| **Hugging Face** | Medium | Recommended | Advanced users, custom models |
| OpenAI/Claude | Easy | No | Cloud API, best performance |

---

## 🚀 Recommended Models for Limited GPU Resources

### Text-Only Models (RECOMMENDED - Lower VRAM, Faster)

#### Ollama (Easiest)
```bash
# 8B text-only - Runs on 4GB VRAM (BEST for limited GPU)
ollama pull llama3.1:8b-instruct-q4_K_M

# 7B reasoning model - Runs on 4GB VRAM
ollama pull deepseek-r1:7b

# 7B efficient model - Runs on 4GB VRAM
ollama pull qwen2.5:7b-instruct
```

#### Hugging Face
| Model | VRAM | Quality | Speed | UI Selection |
|-------|------|---------|-------|--------------|
| **Llama-3.1-8B-Instruct** | 4GB | ⭐⭐⭐⭐ | Very Fast | `omniparser + hf/meta-llama/Llama-3.1-8B-Instruct` |
| **Qwen2.5-7B-Instruct** | 4GB | ⭐⭐⭐⭐ | Very Fast | `omniparser + hf/Qwen/Qwen2.5-7B-Instruct` |
| **Phi-3-medium-4k-instruct** | 4GB | ⭐⭐⭐⭐ | Fast | `omniparser + hf/microsoft/Phi-3-medium-4k-instruct` |
| **DeepSeek-R1-Distill-Llama-8B** | 4GB | ⭐⭐⭐⭐⭐ | Fast | `omniparser + hf/deepseek-ai/DeepSeek-R1-Distill-Llama-8B` |

### Vision Models (Optional - Higher VRAM)

#### Ollama
```bash
# 1B vision model - Runs on 4GB VRAM (fast but limited)
ollama pull llama3.2-vision:1b

# 7B vision model - Runs on 8GB VRAM
ollama pull llava:7b
```

#### Hugging Face
| Model | VRAM | Quality | Speed | UI Selection |
|-------|------|---------|-------|--------------|
| **Qwen2-VL-2B-Instruct** | 4GB | ⭐⭐⭐ | Very Fast | `omniparser + hf/Qwen/Qwen2-VL-2B-Instruct` |
| **Phi-3.5-vision-instruct** | 6GB | ⭐⭐⭐⭐ | Fast | `omniparser + hf/microsoft/Phi-3.5-vision-instruct` |
| **Qwen2-VL-7B-Instruct** | 8GB | ⭐⭐⭐⭐ | Medium | `omniparser + hf/Qwen/Qwen2-VL-7B-Instruct` |

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

### Install Models

Choose and install models based on your GPU capability:

**Text-Only Models (RECOMMENDED - Faster, Lower VRAM):**
```bash
# For 4GB VRAM (Best for limited GPU)
ollama pull llama3.1:8b-instruct-q4_K_M   # 8B text-only
ollama pull deepseek-r1:7b                # 7B reasoning
ollama pull qwen2.5:7b-instruct           # 7B efficient
```

**Vision Models (Optional - Higher VRAM):**
```bash
# For 12GB+ VRAM
ollama pull llama3.2-vision:latest   # 11B vision model

# For 8GB VRAM
ollama pull llava:7b                # 7B vision model
ollama pull qwen2-vl:7b             # 7B, excellent OCR

# For 4GB VRAM
ollama pull llama3.2-vision:1b      # 1B tiny vision model
```

### Usage in OmniParser

1. **Start Ollama server:**
   ```bash
   ollama serve
   ```

2. **Install your chosen model:**
   ```bash
   # Text-only (RECOMMENDED)
   ollama pull llama3.1:8b-instruct-q4_K_M

   # Or vision model (optional)
   ollama pull llama3.2-vision:latest
   ```

3. **Start OmniParser:**
   ```bash
   cd omnitool/gradio
   python app.py
   ```

4. **In Gradio UI:**
   - Select model from dropdown:
     - **Text-only (RECOMMENDED):**
       - `omniparser + ollama/llama3.1:8b-instruct-q4_K_M` (8B, 4GB VRAM)
       - `omniparser + ollama/deepseek-r1:7b` (7B, 4GB VRAM)
       - `omniparser + ollama/qwen2.5:7b-instruct` (7B, 4GB VRAM)
     - **Vision (optional):**
       - `omniparser + ollama/llama3.2-vision:latest` (11B, 12GB VRAM)
       - `omniparser + ollama/llava:7b` (7B, 8GB VRAM)
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

**Text-Only Models (RECOMMENDED):**
| Model Size | VRAM Required | Recommended GPU |
|------------|---------------|-----------------|
| 7-8B | 2-4 GB | RTX 3050, RTX 4050, GTX 1660 |

**Vision Models (Optional):**
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

## Recommended Models

### Text-Only Models (RECOMMENDED for OmniParser)

#### For Ollama

| Model | Size | VRAM | Quality | Use Case | UI Selection |
|-------|------|------|---------|----------|--------------|
| **llama3.1:8b-instruct-q4_K_M** | 8B | 4GB | ⭐⭐⭐⭐⭐ | Best for limited GPU | `omniparser + ollama/llama3.1:8b-instruct-q4_K_M` |
| **deepseek-r1:7b** | 7B | 4GB | ⭐⭐⭐⭐⭐ | Reasoning model | `omniparser + ollama/deepseek-r1:7b` |
| **qwen2.5:7b-instruct** | 7B | 4GB | ⭐⭐⭐⭐ | Efficient | `omniparser + ollama/qwen2.5:7b-instruct` |

#### For Hugging Face

| Model | Size | VRAM | Quality | Use Case | UI Selection |
|-------|------|------|---------|----------|--------------|
| **Llama-3.1-8B-Instruct** | 8B | 4GB | ⭐⭐⭐⭐⭐ | Best for limited GPU | `omniparser + hf/meta-llama/Llama-3.1-8B-Instruct` |
| **DeepSeek-R1-Distill-Llama-8B** | 8B | 4GB | ⭐⭐⭐⭐⭐ | Reasoning model | `omniparser + hf/deepseek-ai/DeepSeek-R1-Distill-Llama-8B` |
| **Qwen2.5-7B-Instruct** | 7B | 4GB | ⭐⭐⭐⭐ | Efficient | `omniparser + hf/Qwen/Qwen2.5-7B-Instruct` |
| **Phi-3-medium-4k-instruct** | 7B | 4GB | ⭐⭐⭐⭐ | Very efficient | `omniparser + hf/microsoft/Phi-3-medium-4k-instruct` |

### Vision Models (Optional - Higher VRAM)

#### For Ollama

| Model | Size | VRAM | Quality | Use Case | UI Selection |
|-------|------|------|---------|----------|--------------|
| **llama3.2-vision:latest** | 11B | 12GB | ⭐⭐⭐⭐ | Best vision quality | `omniparser + ollama/llama3.2-vision:latest` |
| llava:7b | 7B | 8GB | ⭐⭐⭐ | Budget GPUs | `omniparser + ollama/llava:7b` |
| qwen2-vl:7b | 7B | 8GB | ⭐⭐⭐⭐ | Good OCR | `omniparser + ollama/qwen2-vl:7b` |
| llama3.2-vision:1b | 1B | 4GB | ⭐⭐ | Very limited GPU | `omniparser + ollama/llama3.2-vision:1b` |

#### For Hugging Face

| Model | Size | VRAM | Quality | Use Case | UI Selection |
|-------|------|------|---------|----------|--------------|
| **Llama-3.2-11B-Vision-Instruct** | 11B | 12GB | ⭐⭐⭐⭐⭐ | Best vision quality | `omniparser + hf/meta-llama/Llama-3.2-11B-Vision-Instruct` |
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

**Text-Only Models (RECOMMENDED for OmniParser):**

| Environment | Model | Latency/Response | VRAM | Cost |
|-------------|-------|------------------|------|------|
| **Ollama (Local, RTX 4060)** | llama3.1:8b-instruct | ~1-2s | 4GB | $0 |
| **Ollama (Local, RTX 4060)** | deepseek-r1:7b | ~1-2s | 4GB | $0 |
| **TGI (Local, RTX 4060)** | Llama-3.1-8B-Instruct | ~1-2s | 4GB | $0 |

**Vision Models (Optional, for comparison):**

| Environment | Model | Latency/Response | VRAM | Cost |
|-------------|-------|------------------|------|------|
| **Ollama (Local, RTX 4080)** | llama3.2-vision:11b | ~3-5s | 12GB | $0 |
| **TGI (Local, RTX 4080)** | Llama-3.2-11B-Vision | ~3-5s | 12GB | $0 |
| HF Inference API (Cloud) | Vision models | ~8-12s | N/A | Free tier |

**Cloud API (for comparison):**

| Environment | Latency/Response | Cost |
|-------------|------------------|------|
| GPT-4o (Cloud) | ~2-3s | $0.0025/response |
| Claude 3.5 Sonnet (Cloud) | ~2-3s | $0.003/response |

*Latency varies based on task complexity and hardware.*

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

1. **Try Ollama with text-only models first** - Easiest and fastest
   - `ollama pull llama3.1:8b-instruct-q4_K_M` (RECOMMENDED for 4GB GPU)
   - `ollama pull deepseek-r1:7b` (Reasoning model)
2. **Test with simple tasks** - "List all open windows" or "Click the submit button"
3. **Start with text-only models** - 2-3x faster, lower VRAM (4GB vs 12GB)
4. **Only use vision models if needed** - Advanced use cases where LLM needs raw screenshots
5. **Compare quality** - Text-only vs vision models for your use case

For questions and issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
