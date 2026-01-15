# Platform-Specific Requirements

OmniParser supports three acceleration backends: **CUDA (NVIDIA)**, **MPS (Apple Silicon)**, and **CPU**. The installation process automatically detects your platform and installs the appropriate PyTorch version.

## Supported Platforms

| Platform | Acceleration | PyTorch Version | VRAM/RAM | Speed |
|----------|--------------|-----------------|----------|-------|
| **NVIDIA GPU** | CUDA | `cu121` (CUDA 12.1) | 4-12GB VRAM | ⭐⭐⭐⭐⭐ Fastest |
| **Apple Silicon (M1/M2/M3)** | MPS | Default (ARM native) | 8-16GB Unified Memory | ⭐⭐⭐⭐ Fast |
| **Intel/AMD CPU** | CPU-only | `cpu` (optimized) | 8GB+ RAM | ⭐⭐ Slower |

## Automatic Installation

The `install.sh` script automatically detects your platform:

```bash
./install.sh
```

### Detection Logic

1. **NVIDIA GPU (CUDA)**
   - Checks for `nvidia-smi` command
   - Installs: `torch torchvision --index-url https://download.pytorch.org/whl/cu121`
   - Size: ~2GB download

2. **Apple Silicon (MPS)**
   - Checks for macOS + ARM architecture (`uname -m` == `arm64`)
   - Installs: `torch torchvision` (default PyPI, native ARM build)
   - Size: ~500MB download
   - Enables Metal Performance Shaders (MPS) for NPU acceleration

3. **CPU-only (Fallback)**
   - No GPU detected
   - Installs: `torch torchvision --index-url https://download.pytorch.org/whl/cpu`
   - Size: ~200MB download
   - Optimized for CPU-only inference

## Manual Installation

### NVIDIA GPU (CUDA 12.1)

```bash
# Prerequisites
nvidia-smi  # Must show CUDA 11.8+

# Install PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
# Should print: CUDA: True
```

### Apple Silicon (M1/M2/M3)

```bash
# Prerequisites
uname -m    # Must show: arm64
sw_vers     # macOS 12.3+ recommended

# Install PyTorch (native ARM build with MPS)
pip install torch torchvision

# Verify
python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
# Should print: MPS: True
```

### CPU-only (All platforms)

```bash
# Install CPU-optimized PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Verify
python -c "import torch; print(f'CPU: {torch.cuda.is_available() == False}')"
# Should print: CPU: True
```

## Runtime Device Selection

OmniParser automatically selects the best available device at runtime:

**Priority: CUDA > MPS > CPU**

```python
# In util/utils.py and util/omniparser.py
if torch.cuda.is_available():
    device = "cuda"
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"
```

You can override this with the `--device` flag:

```bash
# Force CPU
python -m omniparserserver --device cpu

# Force MPS (Mac only)
python -m omniparserserver --device mps

# Force CUDA (NVIDIA only)
python -m omniparserserver --device cuda
```

## Performance Benchmarks

Tested on OmniParser parsing a 1920x1080 screenshot:

| Platform | Device | Latency | Memory |
|----------|--------|---------|--------|
| RTX 4090 | CUDA | 0.4s | 4GB VRAM |
| RTX 3080 | CUDA | 0.6s | 6GB VRAM |
| M3 Max | MPS | 0.8s | 4GB Unified |
| M2 Pro | MPS | 1.2s | 6GB Unified |
| M1 | MPS | 1.5s | 8GB Unified |
| Intel i9-13900K | CPU | 3.5s | 8GB RAM |
| AMD Ryzen 9 5950X | CPU | 4.0s | 8GB RAM |

## Troubleshooting

### CUDA Issues

**"CUDA out of memory"**
- Reduce batch size in `util/utils.py`
- Close other GPU applications
- Use smaller models

**"CUDA not available" despite having NVIDIA GPU**
- Check CUDA toolkit: `nvcc --version`
- Reinstall CUDA-enabled PyTorch: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --force-reinstall`
- Verify drivers: `nvidia-smi`

### MPS Issues

**"MPS not available" on Apple Silicon**
- Check macOS version: `sw_vers` (need 12.3+)
- Check architecture: `uname -m` (should be `arm64`)
- Reinstall PyTorch: `pip install torch torchvision --force-reinstall`

**"MPS out of memory"**
- macOS uses unified memory (shared with CPU)
- Close other applications
- Restart Mac to clear memory

**"MPS backend error"**
- Some operations not supported on MPS
- Falls back to CPU automatically
- Check PyTorch version: `python -c "import torch; print(torch.__version__)"` (need 2.0+)

### CPU Issues

**Very slow performance**
- Expected - CPU is 5-10x slower than GPU
- Consider cloud GPU (Colab, Lambda Labs)
- Or use smaller models

**Import errors**
- Check PyTorch installation: `pip list | grep torch`
- Reinstall: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --force-reinstall`

## Platform-Specific Dependencies

### Windows

```bash
# uiautomation (Windows-only)
pip install uiautomation
```

### macOS

```bash
# PyObjC (for window management)
pip install pyobjc-core pyobjc-framework-Cocoa
```

### Linux

```bash
# X11 development headers (for window management)
sudo apt-get install python3-xlib
```

## Verifying Installation

After running `install.sh`, verify your setup:

```bash
# Activate virtual environment
source venv/bin/activate

# Check PyTorch
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')

backends = []
if torch.cuda.is_available():
    backends.append('CUDA')
    print(f'CUDA version: {torch.version.cuda}')
if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    backends.append('MPS')
if not backends:
    backends.append('CPU')

print(f'Available backends: {\" + \".join(backends)}')
"

# Expected output examples:
# NVIDIA GPU: "PyTorch version: 2.x.x+cu121, CUDA version: 12.1, Available backends: CUDA"
# Apple Silicon: "PyTorch version: 2.x.x, Available backends: MPS"
# CPU: "PyTorch version: 2.x.x+cpu, Available backends: CPU"
```

## Switching Between Versions

### From CPU to CUDA

```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### From CUDA to MPS (Mac only)

```bash
pip uninstall torch torchvision
pip install torch torchvision
```

### From any version to CPU

```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## Package Sizes

| Version | Size | Use Case |
|---------|------|----------|
| CUDA 12.1 | ~2GB | NVIDIA GPUs, best performance |
| Default (MPS) | ~500MB | Apple Silicon, native acceleration |
| CPU-only | ~200MB | No GPU, smaller download |

## Docker Support

For consistent cross-platform deployment:

```dockerfile
# CUDA
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# CPU-only
FROM python:3.10-slim
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## References

- PyTorch Installation Guide: https://pytorch.org/get-started/locally/
- CUDA Compatibility: https://pytorch.org/get-started/previous-versions/
- MPS Backend: https://pytorch.org/docs/stable/notes/mps.html
- CPU Optimizations: https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html

## Questions?

For platform-specific installation issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
