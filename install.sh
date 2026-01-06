#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  OmniParser Installation Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# -----------------------------------------------------------------------------
# 1. Check Prerequisites
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}Error: Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "  Python version: ${GREEN}$PYTHON_VERSION${NC}"

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git not found. Please install git.${NC}"
    exit 1
fi
echo -e "  Git: ${GREEN}found${NC}"

# -----------------------------------------------------------------------------
# 2. Create Virtual Environment
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[2/6] Setting up virtual environment...${NC}"

VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    echo -e "  ${YELLOW}Warning: $VENV_DIR already exists.${NC}"
    read -p "  Delete and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        echo -e "  Removed existing venv."
    else
        echo -e "  Using existing venv."
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "  Created virtual environment: ${GREEN}$VENV_DIR${NC}"
fi

# Activate venv
source "$VENV_DIR/bin/activate"
echo -e "  Activated: ${GREEN}$(which python)${NC}"

# Upgrade pip
pip install --upgrade pip --quiet

# -----------------------------------------------------------------------------
# 3. Detect CUDA and Install PyTorch
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[3/6] Detecting GPU and installing PyTorch...${NC}"

CUDA_AVAILABLE=false
CUDA_VERSION=""

if command -v nvidia-smi &> /dev/null; then
    CUDA_AVAILABLE=true
    # Extract CUDA version from nvidia-smi
    CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n1 || echo "")

    if [ -n "$CUDA_VERSION" ]; then
        echo -e "  NVIDIA GPU detected: ${GREEN}yes${NC}"

        # Check nvcc for CUDA toolkit version
        if command -v nvcc &> /dev/null; then
            NVCC_VERSION=$(nvcc --version | grep "release" | sed -n 's/.*release \([0-9]*\.[0-9]*\).*/\1/p')
            echo -e "  CUDA Toolkit: ${GREEN}$NVCC_VERSION${NC}"
        fi
    fi
fi

if [ "$CUDA_AVAILABLE" = true ]; then
    echo -e "  Installing PyTorch with ${GREEN}CUDA support${NC}..."
    # Install PyTorch with CUDA 12.1 (widely compatible)
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
else
    echo -e "  No NVIDIA GPU detected. Installing ${YELLOW}CPU-only${NC} PyTorch..."
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
fi

# Verify PyTorch installation
TORCH_VERSION=$(python -c "import torch; print(torch.__version__)")
CUDA_TORCH=$(python -c "import torch; print('CUDA' if torch.cuda.is_available() else 'CPU')")
echo -e "  PyTorch version: ${GREEN}$TORCH_VERSION${NC} ($CUDA_TORCH)"

# -----------------------------------------------------------------------------
# 4. Install Requirements
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[4/6] Installing dependencies...${NC}"

# Install remaining requirements (excluding torch/torchvision which we already installed)
pip install \
    easyocr \
    "supervision==0.18.0" \
    "openai==1.3.5" \
    transformers \
    "ultralytics==8.3.70" \
    azure-identity \
    "numpy==1.26.4" \
    opencv-python \
    opencv-python-headless \
    gradio \
    dill \
    accelerate \
    timm \
    "einops==0.8.0" \
    "ruff==0.6.7" \
    "pre-commit==3.8.0" \
    "pytest==8.3.3" \
    "pytest-asyncio==0.23.6" \
    "pyautogui==0.9.54" \
    "streamlit>=1.38.0" \
    "anthropic[bedrock,vertex]>=0.37.1" \
    "jsonschema==4.22.0" \
    "boto3>=1.28.57" \
    "google-auth<3,>=2" \
    screeninfo \
    dashscope \
    groq \
    huggingface_hub \
    --quiet

# Install PaddleOCR (may fail on some systems)
echo -e "  Installing PaddleOCR (optional, may fail on Windows)..."
pip install paddlepaddle paddleocr --quiet 2>/dev/null || {
    echo -e "  ${YELLOW}Warning: PaddleOCR installation failed. EasyOCR will be used instead.${NC}"
}

# uiautomation is Windows-only
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    pip install uiautomation --quiet 2>/dev/null || true
fi

echo -e "  Dependencies: ${GREEN}installed${NC}"

# -----------------------------------------------------------------------------
# 5. Download Model Weights
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[5/6] Downloading model weights...${NC}"

WEIGHTS_DIR="weights"

if [ -d "$WEIGHTS_DIR/icon_detect" ] && [ -d "$WEIGHTS_DIR/icon_caption_florence" ]; then
    echo -e "  ${YELLOW}Weights already exist. Skipping download.${NC}"
else
    echo -e "  Downloading from HuggingFace (microsoft/OmniParser-v2.0)..."

    # Download icon_detect model
    huggingface-cli download microsoft/OmniParser-v2.0 \
        icon_detect/train_args.yaml \
        icon_detect/model.pt \
        icon_detect/model.yaml \
        --local-dir "$WEIGHTS_DIR" \
        --quiet

    # Download icon_caption model
    huggingface-cli download microsoft/OmniParser-v2.0 \
        icon_caption/config.json \
        icon_caption/generation_config.json \
        icon_caption/model.safetensors \
        --local-dir "$WEIGHTS_DIR" \
        --quiet

    # Rename icon_caption to icon_caption_florence
    if [ -d "$WEIGHTS_DIR/icon_caption" ]; then
        mv "$WEIGHTS_DIR/icon_caption" "$WEIGHTS_DIR/icon_caption_florence"
    fi

    echo -e "  Model weights: ${GREEN}downloaded${NC}"
fi

# -----------------------------------------------------------------------------
# 6. Verify Installation
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[6/6] Verifying installation...${NC}"

# Check critical imports
python -c "
import torch
import transformers
import ultralytics
import gradio
import easyocr
print('  Core imports: OK')
" 2>/dev/null && echo -e "  Core imports: ${GREEN}OK${NC}" || echo -e "  Core imports: ${RED}FAILED${NC}"

# Check model weights
if [ -f "$WEIGHTS_DIR/icon_detect/model.pt" ] && [ -f "$WEIGHTS_DIR/icon_caption_florence/model.safetensors" ]; then
    echo -e "  Model weights: ${GREEN}OK${NC}"
else
    echo -e "  Model weights: ${RED}MISSING${NC}"
fi

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "To activate the environment:"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo -e "Quick test:"
echo -e "  ${YELLOW}python gradio_demo.py${NC}"
echo ""
echo -e "Full stack:"
echo -e "  ${YELLOW}cd omnitool/omniparserserver && python -m omniparserserver${NC}"
echo -e "  ${YELLOW}cd omnitool/gradio && python app.py${NC}"
echo ""
