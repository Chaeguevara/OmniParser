# macOS Quick Start Guide

Welcome macOS users! OmniParser now runs **natively on Mac** with full support for:
- ✅ Apple Silicon (M1/M2/M3) with MPS acceleration
- ✅ Intel Macs with CPU fallback
- ✅ Native AppleScript window management (zero dependencies)
- ✅ Native mouse/keyboard/screenshot control (no VM required)

## Installation

### 1. Install Dependencies

```bash
# Clone the repository
cd OmniParser

# Run the installation script
./install.sh
```

The install script will:
- Create a Python virtual environment
- Auto-detect your Mac (Apple Silicon or Intel)
- Install the correct PyTorch version (MPS or CPU)
- Download AI models (YOLO, Florence-2, etc.)

### 2. Activate the Environment

```bash
source venv/bin/activate
```

## Quick Test

### Test 1: Simple Demo (Screenshot Parsing)

```bash
python gradio_demo.py
```

This will:
- Start a local Gradio UI at http://127.0.0.1:7860
- Upload a screenshot and see OmniParser detect all UI elements
- No Windows VM required!

### Test 2: React UI (Full Stack)

```bash
# One command to start everything
./start_ui.sh
```

This will:
- Check for Node.js (install if needed: `brew install node`)
- Start FastAPI backend on port 8888
- Start React frontend on port 5173
- Open http://localhost:5173 in your browser

**Stop**: Press `Ctrl+C` or run `./stop_ui.sh`

## What Works on Mac

### ✅ Fully Supported

| Feature | Implementation | Notes |
|---------|----------------|-------|
| **Screenshot parsing** | OmniParser + Florence-2 + YOLO | Native MPS acceleration on M1/M2/M3 |
| **Window management** | AppleScript | List, focus, get active window |
| **Mouse control** | pyautogui | Move, click, drag, scroll |
| **Keyboard control** | pyautogui | Type, key combinations |
| **Screenshot capture** | pyautogui | Native screenshot API |
| **React UI** | Node.js + FastAPI | Air-gapped compatible |

### ⚠️ Optional

| Feature | Status | Notes |
|---------|--------|-------|
| **Windows VM** | Not needed | Only for advanced Windows-specific automation |
| **Docker** | Not needed | Native macOS tools work out of the box |

## Example: List Open Windows

```python
from omnitool.gradio.tools.window_manager import get_window_manager

wm = get_window_manager()  # Auto-detects macOS

# List all open windows
windows = wm.list_windows()
for w in windows:
    print(f"{w['title']} ({w['app']})")

# Get active window
active = wm.get_active_window()
print(f"Active: {active['title']}")

# Focus a window
wm.focus_window("Chrome")  # Brings Chrome to front
```

## Example: Mouse/Keyboard Automation

```python
from omnitool.gradio.tools.computer import ComputerTool
import asyncio

async def main():
    tool = ComputerTool()

    # Take screenshot
    result = await tool(action="screenshot")
    print(f"Screenshot saved: {result.base64_image[:50]}...")

    # List windows
    result = await tool(action="list_windows")
    print(result.output)

    # Focus Safari
    result = await tool(action="focus_window", text="Safari")
    print(result.output)

    # Move mouse
    result = await tool(action="mouse_move", coordinate=(500, 500))
    print(result.output)

    # Click
    result = await tool(action="left_click")
    print(result.output)

asyncio.run(main())
```

## GPU Acceleration (Apple Silicon)

On M1/M2/M3 Macs, OmniParser automatically uses **MPS (Metal Performance Shaders)** for 2-3x faster inference:

```bash
source venv/bin/activate
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
# Output: MPS available: True
```

**Performance** (1920x1080 screenshot):
- M3 Max: ~0.8s (MPS)
- M2 Pro: ~1.2s (MPS)
- Intel i9: ~3.5s (CPU)

## Troubleshooting

### "Permission denied: ./start_ui.sh"

```bash
chmod +x start_ui.sh stop_ui.sh
./start_ui.sh
```

### "Node.js not found"

```bash
# Install Node.js via Homebrew
brew install node

# Or download from https://nodejs.org/
```

### "MPS dtype mismatch error"

Already fixed! The latest code uses `float32` for MPS (instead of `float16`).

### "Window management not working"

Window management uses AppleScript, which requires:
- **Accessibility permissions** for your terminal app
- Go to: System Settings → Privacy & Security → Accessibility
- Add Terminal.app or your terminal emulator

## Next Steps

1. **Run the simple demo**: `python gradio_demo.py`
2. **Try the React UI**: `./start_ui.sh`
3. **Read the docs**: `docs/WINDOW_MANAGEMENT.md`, `docs/PLATFORM_REQUIREMENTS.md`
4. **Integrate local LLM**: `docs/LOCAL_LLM.md` (Ollama, Hugging Face)

## macOS-Specific Features

### Command Key Support

The `Super_L` key is automatically mapped to `command` on Mac (instead of `win` on Windows):

```python
# Press Command+C
await tool(action="key", text="Super_L+c")  # Works on Mac!
```

### Native AppleScript Window Management

No external dependencies needed! Uses built-in macOS APIs:

```bash
# List windows via AppleScript
osascript -e 'tell application "System Events" to get name of every window of every process'
```

### MPS Device Detection

PyTorch automatically detects and uses your Mac's Neural Processing Unit:

```python
import torch

if torch.backends.mps.is_available():
    device = "mps"
    print("Using Apple Silicon NPU!")
```

## Support

- **GitHub Issues**: https://github.com/Chaeguevara/OmniParser/issues
- **Documentation**: `docs/` folder
- **Discord/Community**: [Add your community link here]

---

**Welcome to OmniParser on macOS!** 🎉
