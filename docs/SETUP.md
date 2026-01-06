# Setup Guide

## Prerequisites

- Python 3.10+ (3.12 recommended)
- Git
- Docker Desktop (for OmniBox VM)
- GPU with CUDA (optional, recommended)
- 30GB disk (OmniBox: 5GB ISO + 20GB storage)

## Quick Install (Recommended)

```bash
git clone https://github.com/microsoft/OmniParser.git
cd OmniParser
./install.sh
```

The script will:
1. Check prerequisites (Python 3.10+, git)
2. Create virtual environment (`venv/`)
3. Auto-detect CUDA and install appropriate PyTorch
4. Install all dependencies
5. Download model weights from HuggingFace
6. Verify installation

## Manual Setup

If you prefer manual setup:

```bash
# Create and activate venv
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install PyTorch (choose one)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121  # CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu    # CPU

# Install dependencies
pip install -r requirements.txt

# Download model weights
huggingface-cli download microsoft/OmniParser-v2.0 \
    icon_detect/train_args.yaml icon_detect/model.pt icon_detect/model.yaml \
    icon_caption/config.json icon_caption/generation_config.json icon_caption/model.safetensors \
    --local-dir weights
mv weights/icon_caption weights/icon_caption_florence
```

## Activate Environment

```bash
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

## Component Setup

### 1. OmniParser Server

```bash
cd omnitool/omniparserserver
python -m omniparserserver \
  --som_model_path ../../weights/icon_detect/model.pt \
  --caption_model_name florence2 \
  --caption_model_path ../../weights/icon_caption_florence \
  --device cuda \
  --BOX_TRESHOLD 0.05 \
  --host 127.0.0.1 --port 8000
```

### 2. OmniBox VM

```bash
# Place Windows 11 ISO as omnitool/omnibox/vm/win11iso/custom.iso
cd omnitool/omnibox/scripts
./manage_vm.sh create    # First time (20-90 mins)
./manage_vm.sh start     # Start VM
./manage_vm.sh stop      # Stop VM
```

**Access:**
- NoVNC: http://localhost:8006/vnc.html
- API: http://localhost:5000/

### 3. Gradio UI

```bash
cd omnitool/gradio
python app.py \
  --windows_host_url localhost:8006 \
  --omniparser_server_url localhost:8000
```

## API Keys

Set via environment or Gradio UI:
- `ANTHROPIC_API_KEY` - Claude
- `OPENAI_API_KEY` - GPT models
- `GROQ_API_KEY` - Groq inference
- `DASHSCOPE_API_KEY` - Qwen models

## Verify Installation

```bash
source venv/bin/activate
python gradio_demo.py

# Health checks
curl http://localhost:8000/probe/   # OmniParser server
```

## Windows Notes

The `install.sh` script is for Linux/macOS. On Windows:
1. Use WSL2 (recommended), or
2. Run manual setup commands in PowerShell/CMD
3. PaddleOCR may require [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
