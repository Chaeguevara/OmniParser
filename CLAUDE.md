# CLAUDE.md - OmniParser AI Assistant Guide

**OmniParser** converts GUI screenshots into structured elements for VLMs (GPT-4V, Claude). Enables vision-based GUI agents.

## Key Paths

| Path | Purpose |
|------|---------|
| `util/omniparser.py` | Main API class |
| `util/utils.py` | Core detection/OCR/captioning (600+ lines) |
| `omnitool/omniparserserver/` | FastAPI REST server |
| `omnitool/gradio/app.py` | Full Gradio UI |
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

# Full stack (3 terminals)
cd omnitool/omniparserserver && python -m omniparserserver
cd omnitool/omnibox/scripts && ./manage_vm.sh start
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

## Environment

- Python 3.10+ (3.12 recommended)
- venv-based setup via `./install.sh`
- GPU optional (CUDA auto-detected), CPU works slower
- Docker required for OmniBox VM

## Detailed Documentation

| Topic | File |
|-------|------|
| Environment setup, model download | [`docs/SETUP.md`](docs/SETUP.md) |
| REST & Python API reference | [`docs/API.md`](docs/API.md) |
| Design patterns, conventions | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Adding providers, tools, models | [`docs/EXTENDING.md`](docs/EXTENDING.md) |
| Common errors & solutions | [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) |

## Commit Convention

```
<type>(<scope>): <subject>
# Types: feat, fix, docs, refactor, test, chore
# Example: feat(agent): Add DeepSeek R1 support
```
