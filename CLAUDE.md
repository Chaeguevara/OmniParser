# CLAUDE.md - OmniParser AI Assistant Guide

**OmniParser** converts GUI screenshots into structured elements for VLMs (GPT-4V, Claude). Enables vision-based GUI agents.

## Key Paths

| Path | Purpose |
|------|---------|
| `util/omniparser.py` | Main API class |
| `util/utils.py` | Core detection/OCR/captioning (600+ lines) |
| `omnitool/backend/` | **FastAPI backend (REST + WebSocket)** |
| `omnitool/frontend/` | **React frontend (Vite + WebSocket)** |
| `omnitool/omniparserserver/` | Legacy parser REST server |
| `omnitool/gradio/app.py` | Legacy Gradio UI (development only) |
| `omnitool/gradio/loop.py` | Agent orchestration loop |
| `omnitool/gradio/agent/` | LLM agents (Claude, GPT, etc.) |
| `omnitool/gradio/tools/computer.py` | Mouse/keyboard control |
| `omnitool/omnibox/` | Windows 11 VM (Docker) |
| `weights/` | Model checkpoints (**never commit**) |
| `gradio_demo.py` | Simple standalone demo |

## Quick Start

```bash
# Install (creates venv, downloads models)
./install.sh
source venv/bin/activate

# Simple demo
python gradio_demo.py

# Full stack - Option 1: React UI (RECOMMENDED for production/secured environments)
# Automatic startup (single command):
./start_ui.sh  # Starts both backend and frontend
# Press Ctrl+C to stop, or run: ./stop_ui.sh

# Manual startup (separate terminals):
# Terminal 1: Backend API
cd omnitool/backend
uvicorn main:app --host 0.0.0.0 --port 8888 --reload

# Terminal 2: Frontend (requires Node.js)
cd omnitool/frontend
npm install
npm run dev  # http://localhost:5173

# Full stack - Option 2: Gradio UI (legacy, development only)
# Terminal 1: Parser server
cd omnitool/omniparserserver && python -m omniparserserver

# Terminal 2: Windows VM (optional, for UI automation)
cd omnitool/omnibox/scripts && ./manage_vm.sh start

# Terminal 3: Gradio UI
cd omnitool/gradio && python app.py
```

## Data Flow

```
Screenshot → YOLO Detection → OCR (EasyOCR/Paddle) → Florence-2 Caption → Dedupe → Output
```

## Output Format

```python
[{"type": "text|icon", "bbox": [x1,y1,x2,y2], "content": str, "interactivity": bool}, ...]
```

Coordinates: normalized [0-1] in API, pixels internally.

## Critical Rules

1. **Never commit `weights/`** - model files too large
2. **Read files before modifying** - code is interconnected
3. **YOLO is AGPL** - requires attribution and open source
4. **Test with `gradio_demo.py` first** - before full stack
5. **API keys** - never hardcode, use env vars or UI input
6. **Security: Gradio tunneling disabled by default** - `share=False` to prevent public exposure
7. **OS limitation: Windows-only currently** - VM requires Windows 11 Docker container

## Environment

- Python 3.10+ (3.12 recommended)
- venv-based setup via `./install.sh`
- GPU optional:
  - **CUDA** (NVIDIA GPUs) - auto-detected, best performance
  - **MPS** (Apple Silicon M1/M2/M3) - auto-detected, native NPU acceleration
  - **CPU** - fallback, slower
- Docker required for OmniBox VM

## Security & Platform Limitations

### Security Considerations

- **Gradio limitations in secured environments**
  - Gradio makes external calls to gradio.app servers (version checking)
  - Cannot be fully disabled, creates issues in air-gapped/corporate networks
  - **For secured environments**: See [`docs/FRONTEND_BACKEND_ARCHITECTURE.md`](docs/FRONTEND_BACKEND_ARCHITECTURE.md) for Node.js-based frontend migration plan

- **Gradio public tunneling disabled by default** (`share=False`)
  - Only enable `share=True` in controlled development environments
  - Public tunnels expose your local service to the internet
  - Use authentication if sharing is required

- **VM security**
  - Windows 11 VM runs with full GUI automation access
  - Limit network exposure of Flask server (port 5000)
  - Use only for testing/development, not production

- **API key protection**
  - Never commit API keys to git
  - Use environment variables or UI input only
  - Keys stored in `~/.anthropic/` with 600 permissions

### Platform Support

**Current status: Windows-only**

- **Full support:** Windows 11 VM (Docker-based OmniBox)
- **Partial support:** Core parsing works cross-platform, but UI automation requires Windows VM
- **Not supported:** Native Linux/macOS UI automation

**For multi-program interaction**, see [`docs/WINDOW_MANAGEMENT.md`](docs/WINDOW_MANAGEMENT.md) for cross-platform roadmap.

## Detailed Documentation

| Topic | File |
|-------|------|
| Environment setup, model download | [`docs/SETUP.md`](docs/SETUP.md) |
| Platform-specific PyTorch installation (CUDA/MPS/CPU) | [`docs/PLATFORM_REQUIREMENTS.md`](docs/PLATFORM_REQUIREMENTS.md) |
| REST & Python API reference | [`docs/API.md`](docs/API.md) |
| Design patterns, conventions | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Adding providers, tools, models | [`docs/EXTENDING.md`](docs/EXTENDING.md) |
| Common errors & solutions | [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) |
| Window management & multi-app automation | [`docs/WINDOW_MANAGEMENT.md`](docs/WINDOW_MANAGEMENT.md) |
| Local LLM setup (Ollama, Hugging Face) | [`docs/LOCAL_LLM.md`](docs/LOCAL_LLM.md) |
| Frontend/backend separation (Node.js migration) | [`docs/FRONTEND_BACKEND_ARCHITECTURE.md`](docs/FRONTEND_BACKEND_ARCHITECTURE.md) |

## Commit Convention

```
<type>(<scope>): <subject>
# Types: feat, fix, docs, refactor, test, chore
# Example: feat(agent): Add DeepSeek R1 support
```
