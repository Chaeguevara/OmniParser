# CLAUDE.md - AI Assistant Guide for OmniParser

This document provides comprehensive guidance for AI assistants working with the OmniParser codebase. It explains the project structure, development workflows, and key conventions to follow.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Key Files and Their Roles](#key-files-and-their-roles)
4. [Development Environment Setup](#development-environment-setup)
5. [Code Architecture and Patterns](#code-architecture-and-patterns)
6. [Testing Conventions](#testing-conventions)
7. [Common Development Tasks](#common-development-tasks)
8. [API Reference](#api-reference)
9. [Security Considerations](#security-considerations)
10. [Git Workflow](#git-workflow)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

**OmniParser** is a screen parsing tool that converts GUI screenshots into structured, actionable elements for vision language models (VLMs) like GPT-4V and Claude. It enables pure vision-based GUI agents to understand and interact with computer interfaces.

### Key Capabilities
- Parses UI screenshots into detected interactive regions and icons
- Provides functional descriptions of UI elements via vision models
- Supports OCR for text detection and icon detection/captioning
- Enables computer control through vision-based agents
- Available in V1, V1.5, and V2 versions (V2 is 60% faster)

### Project Components
1. **OmniParser Core** (`util/`) - Screen parsing and element detection
2. **OmniParser Server** (`omnitool/omniparserserver/`) - FastAPI REST service
3. **OmniBox** (`omnitool/omnibox/`) - Windows 11 VM for agent testing
4. **OmniTool** (`omnitool/gradio/`) - Web UI and agent orchestration

### Technical Stack
- **ML Frameworks**: PyTorch, Transformers, Ultralytics YOLO
- **Vision Models**: Florence-2 (caption), YOLO (detection), EasyOCR/PaddleOCR
- **LLM Integration**: Anthropic Claude, OpenAI GPT-4o, DeepSeek R1, Qwen 2.5 VL
- **Web Frameworks**: FastAPI (server), Gradio (UI), Streamlit (alternative UI)
- **Virtualization**: Docker, QEMU/KVM for Windows 11 VM

### Performance Metrics
- Achieves 39.5% on ScreenSpot Pro grounding benchmark (V2)
- Best performance on Windows Agent Arena
- V2 is 60% faster than V1

---

## Repository Structure

```
OmniParser/
├── util/                          # Core OmniParser library
│   ├── omniparser.py             # Main API class
│   ├── utils.py                   # Core processing functions (600+ lines)
│   ├── box_annotator.py           # Bounding box visualization
│   └── __init__.py
│
├── omnitool/                       # Complete agent system (V2)
│   ├── omniparserserver/          # FastAPI server
│   │   └── omniparserserver.py    # REST API endpoints
│   │
│   ├── gradio/                    # Web UI and orchestration
│   │   ├── app.py                 # Main Gradio application
│   │   ├── app_new.py             # Alternative app version
│   │   ├── app_streamlit.py       # Streamlit interface
│   │   ├── loop.py                # Agent sampling loop
│   │   ├── agent/                 # LLM agent implementations
│   │   │   ├── anthropic_agent.py         # Claude agent
│   │   │   ├── vlm_agent.py               # Multi-model VLM agent
│   │   │   ├── vlm_agent_with_orchestrator.py  # Orchestrated agent
│   │   │   └── llm_utils/         # API clients and utilities
│   │   │       ├── omniparserclient.py
│   │   │       ├── oaiclient.py
│   │   │       ├── groqclient.py
│   │   │       └── utils.py
│   │   ├── tools/                 # Computer use tools
│   │   │   ├── computer.py        # Mouse/keyboard control
│   │   │   ├── screen_capture.py  # Screenshot capture
│   │   │   ├── base.py            # Tool base classes
│   │   │   └── collection.py      # Tool management
│   │   └── executor/              # Tool execution
│   │       └── anthropic_executor.py
│   │
│   └── omnibox/                   # Windows 11 VM infrastructure
│       ├── Dockerfile             # Container definition
│       ├── compose.yml            # Docker Compose config
│       ├── scripts/               # VM management scripts
│       └── vm/                    # VM setup and storage
│
├── eval/                          # Evaluation scripts
│   ├── ss_pro_gpt4o_omniv2.py    # ScreenSpot Pro evaluation
│   └── logs_sspro_omniv2.json    # Results
│
├── weights/                       # Model checkpoints (not in git)
│   ├── icon_detect/              # YOLO model (AGPL)
│   ├── icon_caption_florence/    # Florence-2 model (MIT)
│   └── icon_caption_blip2/       # BLIP2 model (deprecated, MIT)
│
├── docs/                          # Documentation
│   └── Evaluation.md             # Evaluation methodology
│
├── requirements.txt               # Python dependencies
├── gradio_demo.py                # Simple Gradio demo
├── demo.ipynb                    # Jupyter examples
├── README.md                     # Main documentation
└── SECURITY.md                   # Security guidelines
```

### Directory Purposes

| Directory | Purpose | When to Modify |
|-----------|---------|----------------|
| `util/` | Core parsing logic | ML model changes, detection/caption improvements |
| `omnitool/gradio/` | Web UI and agent orchestration | UI changes, agent behavior, new LLM support |
| `omnitool/omniparserserver/` | REST API server | API endpoints, server configuration |
| `omnitool/omnibox/` | Windows VM setup | VM configuration, Docker setup |
| `eval/` | Benchmarking code | Adding new benchmarks, evaluation metrics |
| `weights/` | Model checkpoints | NEVER commit (in .gitignore) |

---

## Key Files and Their Roles

### Core Parsing Engine

#### `util/omniparser.py` (API Entry Point)
Main API wrapper class for OmniParser.

**Key Components:**
```python
class Omniparser:
    def __init__(self, config: dict)
    def parse(self, base64_image: str) -> tuple[str, list[dict]]
```

**When to modify:**
- Adding new model versions
- Changing default parameters
- Adding new parsing modes

#### `util/utils.py` (Core Processing - 600+ lines)
Contains all the heavy lifting for detection, OCR, and captioning.

**Critical Functions:**
- `get_yolo_model()` - Loads YOLO detection model
- `get_caption_model_processor()` - Loads Florence-2 or BLIP2
- `get_som_labeled_img()` - Main pipeline combining OCR + detection + captioning
- `check_ocr_box()` - Performs OCR on image regions
- `remove_overlap()` / `remove_overlap_new()` - Deduplicates bounding boxes
- `get_parsed_content_icon()` - Generates icon captions

**When to modify:**
- Improving detection/OCR algorithms
- Changing IoU thresholds
- Adding new vision models
- Performance optimizations

#### `util/box_annotator.py` (Visualization)
Custom bounding box annotation for visualization.

**When to modify:**
- Changing annotation style
- Adding new visualization features

### Server & API

#### `omnitool/omniparserserver/omniparserserver.py` (FastAPI Server)
REST API exposing OmniParser as a service.

**Key Endpoints:**
- `POST /parse/` - Parse base64 image, return annotated image + elements
- `GET /probe/` - Health check

**Command-line arguments:**
- `--som_model_path` - Path to YOLO detection model
- `--caption_model_name` - 'florence2' or 'blip2'
- `--caption_model_path` - Path to caption model
- `--device` - 'cuda' or 'cpu'
- `--BOX_TRESHOLD` - Detection confidence threshold (default: 0.05)
- `--host` / `--port` - Server binding

**When to modify:**
- Adding new endpoints
- Changing request/response formats
- Adding authentication

### Agent System

#### `omnitool/gradio/loop.py` (Main Orchestration)
Core agentic sampling loop that orchestrates agent-tool interaction.

**Key Function:**
```python
def sampling_loop_sync(
    model: str,
    provider: APIProvider,
    messages: list[dict],
    output_callback: Callable,
    tool_output_callback: Callable,
    api_response_callback: Callable,
    api_key: str,
    omniparser_url: str
) -> Generator
```

**When to modify:**
- Changing agent loop logic
- Adding new providers
- Modifying message flow

#### `omnitool/gradio/agent/anthropic_agent.py` (Claude Agent)
Anthropic Claude 3.5 Sonnet agent with Computer Use capabilities.

**Key Features:**
- Supports Anthropic, Bedrock, and Vertex deployment
- Token usage tracking and cost calculation
- Tool definition management

**When to modify:**
- Updating to new Claude models
- Changing tool configurations
- Adding prompt engineering

#### `omnitool/gradio/agent/vlm_agent.py` (Multi-Model Agent)
Vision Language Model agent supporting multiple providers.

**Supported Models:**
- OpenAI: GPT-4o, o1, o3-mini
- DeepSeek: R1
- Qwen: 2.5 VL

**When to modify:**
- Adding new VLM providers
- Changing prompt templates
- Modifying reasoning logic

#### `omnitool/gradio/tools/computer.py` (Computer Control)
Implements Anthropic's computer use tool pattern.

**Supported Actions:**
- `mouse_move` - Move cursor to coordinates
- `left_click` / `right_click` - Mouse clicks
- `left_click_drag` - Click and drag
- `type` - Keyboard text input
- `key` - Special key presses
- `screenshot` - Capture screen

**When to modify:**
- Adding new tool actions
- Changing coordinate scaling
- Improving error handling

### UI Applications

#### `gradio_demo.py` (Simple Demo)
Standalone Gradio interface for OmniParser without VM/server dependencies.

**When to use:**
- Quick testing of parsing
- Demonstrating core functionality
- Local development without Docker

#### `omnitool/gradio/app.py` (Full OmniTool UI)
Complete Gradio application integrating all components.

**Features:**
- Windows VM connection
- Multi-agent support
- Real-time reasoning display
- Action execution visualization

**Command-line args:**
- `--windows_host_url` - OmniBox VM address (default: localhost:8006)
- `--omniparser_server_url` - Parser server address (default: localhost:8000)

**When to modify:**
- UI/UX improvements
- Adding new agent options
- Changing display formats

---

## Development Environment Setup

### Prerequisites
- **Python**: 3.12 (recommended)
- **Conda**: For environment management
- **GPU**: CUDA-compatible (optional but recommended for speed)
- **Docker Desktop**: Required for OmniBox VM
- **Disk Space**: 30GB for OmniBox (5GB ISO + 20GB storage + 400MB container)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/microsoft/OmniParser.git
cd OmniParser

# Create conda environment
conda create -n "omni" python==3.12
conda activate omni

# Install dependencies
pip install -r requirements.txt

# Download model weights (V2)
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} \
         icon_caption/{config.json,generation_config.json,model.safetensors}; do
  huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
done
mv weights/icon_caption weights/icon_caption_florence
```

### Component Setup

#### 1. OmniParser Server (for production use)
```bash
cd omnitool/omniparserserver
python -m omniparserserver \
  --som_model_path ../../weights/icon_detect/model.pt \
  --caption_model_name florence2 \
  --caption_model_path ../../weights/icon_caption_florence \
  --device cuda \
  --BOX_TRESHOLD 0.05 \
  --host 127.0.0.1 \
  --port 8000
```

#### 2. OmniBox VM (for agent testing)
```bash
# Download Windows 11 Enterprise Evaluation ISO
# Rename to custom.iso and place in omnitool/omnibox/vm/win11iso/

cd omnitool/omnibox/scripts
./manage_vm.sh create    # First time setup (20-90 mins)
./manage_vm.sh start     # Start VM
./manage_vm.sh stop      # Stop VM
./manage_vm.sh delete    # Clean up
```

**VM Access:**
- NoVNC viewer: http://localhost:8006/vnc.html
- VM control API: http://localhost:5000/

#### 3. Gradio UI
```bash
cd omnitool/gradio
python app.py \
  --windows_host_url localhost:8006 \
  --omniparser_server_url localhost:8000
```

### Environment Variables

No environment file is required, but you'll need API keys for LLM providers:
- `ANTHROPIC_API_KEY` - For Claude models
- `OPENAI_API_KEY` - For GPT models
- `GROQ_API_KEY` - For Groq inference
- `DASHSCOPE_API_KEY` - For Qwen models

These are typically entered in the Gradio UI rather than as environment variables.

---

## Code Architecture and Patterns

### Design Patterns

#### 1. Modular ML Pipeline
The parsing pipeline is decomposed into independent, swappable components:
```
Screenshot → YOLO Detection → OCR (EasyOCR/Paddle) → Icon Captioning (Florence2/BLIP2) → Deduplication → Output
```

**Benefits:**
- Easy to swap detection/caption models
- Can run components on different machines
- Clear separation of concerns

#### 2. Client-Server Architecture
```
[Gradio UI] ← HTTP → [OmniParser Server] ← HTTP → [Windows VM]
```

**Benefits:**
- OmniParser can run on GPU server
- OmniBox can run on CPU machine
- Multiple clients can share one parser

#### 3. Tool-Based Agent System
Follows Anthropic's Computer Use pattern:
```python
class BaseAnthropicTool:
    def to_params(self) -> dict: ...
    async def __call__(self, **kwargs) -> ToolResult: ...
```

**Benefits:**
- Standardized tool interface
- Easy to add new tools
- Compatible with Anthropic API

#### 4. Message Loop Pattern
```python
while not done:
    # 1. Send messages to LLM
    response = agent.call(messages)

    # 2. Extract tool calls
    tool_results = executor.execute(response)

    # 3. Append results to messages
    messages.append(tool_results)
```

**Benefits:**
- Synchronous control flow
- Easy to debug
- Handles streaming responses

### Code Conventions

#### Configuration Pattern
```python
# Configuration passed as dictionaries, not config files
config = {
    'som_model_path': 'weights/icon_detect/model.pt',
    'caption_model_name': 'florence2',
    'caption_model_path': 'weights/icon_caption_florence',
    'BOX_TRESHOLD': 0.05,
    'device': 'cuda'
}
parser = Omniparser(config)
```

#### Image Encoding
All images are transmitted as base64 strings:
```python
import base64

# Encoding
with open('screenshot.png', 'rb') as f:
    base64_image = base64.b64encode(f.read()).decode('utf-8')

# Decoding
image_data = base64.b64decode(base64_image)
```

#### Coordinate Systems
Two coordinate formats are used:
```python
# 1. Normalized [0-1] coordinates (preferred for API)
bbox = [x_min/width, y_min/height, x_max/width, y_max/height]

# 2. Pixel coordinates (used internally)
bbox = [x_min_px, y_min_px, x_max_px, y_max_px]
```

#### Output Format
```python
parsed_content_list = [
    {
        'type': 'text' or 'icon',
        'bbox': [x1, y1, x2, y2],
        'content': str,  # OCR text or icon description
        'interactivity': bool  # Whether element is clickable
    },
    ...
]
```

#### Type Hints
Extensive use of Python type annotations:
```python
from typing import Optional, Callable, Generator

def sampling_loop_sync(
    model: str,
    provider: APIProvider,
    messages: list[dict],
    output_callback: Callable[[str], None],
    tool_output_callback: Callable[[dict], None],
    api_key: str,
    omniparser_url: Optional[str] = None
) -> Generator[dict, None, None]:
    ...
```

### Important Architectural Decisions

#### Why FastAPI for Server?
- Async support for concurrent requests
- Automatic OpenAPI documentation
- Easy integration with ML pipelines

#### Why Gradio for UI?
- Rapid prototyping
- Built-in components for file upload, chat interface
- Easy deployment

#### Why Florence-2 over BLIP2?
- Better performance on UI elements
- Faster inference
- MIT license (more permissive than AGPL)

#### Why YOLO for Detection?
- State-of-the-art object detection
- Fast inference
- Easy to fine-tune on custom datasets

---

## Testing Conventions

### Current Testing State
**No formal test suite** - The project does not have a `tests/` directory or comprehensive test coverage.

### Available Testing Tools
From `requirements.txt`:
- `pytest==8.3.3` - Testing framework (installed but not used)
- `pytest-asyncio==0.23.6` - Async test support
- `ruff==0.6.7` - Linter/formatter
- `pre-commit==3.8.0` - Git hooks (no config file present)

### Current Testing Approach

#### 1. Manual Testing via Demos
```bash
# Simple parsing test
python gradio_demo.py

# Full agent test
cd omnitool/gradio
python app.py
```

#### 2. Jupyter Notebook Examples
`demo.ipynb` contains example usage:
```python
from util.omniparser import Omniparser

parser = Omniparser(config)
result = parser.parse(base64_image)
```

#### 3. Benchmark Evaluation
```bash
cd eval
python ss_pro_gpt4o_omniv2.py
```

Evaluates against ScreenSpot Pro benchmark.

### Testing Best Practices for Development

When modifying code, manually verify:

#### For Core Parsing (`util/`)
1. Run `gradio_demo.py` with test images
2. Check bounding box accuracy
3. Verify OCR text extraction
4. Validate icon descriptions

#### For Server (`omnitool/omniparserserver/`)
1. Start server and check `/probe/` endpoint
2. Send POST request to `/parse/` with test image
3. Verify response format
4. Check latency metrics

```bash
# Health check
curl http://localhost:8000/probe/

# Parse test
curl -X POST http://localhost:8000/parse/ \
  -H "Content-Type: application/json" \
  -d '{"base64_image": "..."}'
```

#### For Agent System (`omnitool/gradio/`)
1. Start full stack (parser + VM + gradio)
2. Test simple tasks (e.g., "Click the Start button")
3. Verify tool execution
4. Check message flow in UI

#### For OmniBox VM (`omnitool/omnibox/`)
1. Verify VM boots successfully
2. Check NoVNC viewer access
3. Test control API: `curl http://localhost:5000/probe`
4. Verify mouse/keyboard actions work

### Adding Tests (Future Work)
If you're adding tests, follow this structure:

```
tests/
├── test_utils.py          # Test core parsing functions
├── test_omniparser.py     # Test Omniparser class
├── test_server.py         # Test FastAPI endpoints
├── test_agent.py          # Test agent logic
├── test_tools.py          # Test computer tools
└── fixtures/              # Test images and data
    └── test_screenshot.png
```

Example test structure:
```python
import pytest
from util.omniparser import Omniparser

@pytest.fixture
def parser():
    config = {
        'som_model_path': 'weights/icon_detect/model.pt',
        'caption_model_name': 'florence2',
        'caption_model_path': 'weights/icon_caption_florence',
    }
    return Omniparser(config)

def test_parse_returns_valid_format(parser):
    base64_image = load_test_image()
    labeled_img, parsed_content = parser.parse(base64_image)

    assert isinstance(parsed_content, list)
    for item in parsed_content:
        assert 'type' in item
        assert 'bbox' in item
        assert 'content' in item
```

---

## Common Development Tasks

### Adding a New LLM Provider

1. Create agent class in `omnitool/gradio/agent/`:
```python
# new_provider_agent.py
class NewProviderAgent:
    def __init__(self, api_key: str, model: str):
        self.client = NewProviderClient(api_key)
        self.model = model

    def __call__(self, messages: list[dict]) -> dict:
        response = self.client.chat(
            model=self.model,
            messages=messages
        )
        return response
```

2. Add provider to `loop.py`:
```python
from enum import Enum

class APIProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    NEW_PROVIDER = "new_provider"  # Add here
```

3. Update `sampling_loop_sync()` in `loop.py`:
```python
if provider == APIProvider.NEW_PROVIDER:
    actor = NewProviderAgent(api_key, model)
```

4. Add UI option in `app.py`:
```python
provider_dropdown = gr.Dropdown(
    choices=["Anthropic", "OpenAI", "NewProvider"],  # Add here
    value="Anthropic",
    label="Provider"
)
```

### Adding a New Tool

1. Create tool class in `omnitool/gradio/tools/`:
```python
# new_tool.py
from .base import BaseAnthropicTool, ToolResult

class NewTool(BaseAnthropicTool):
    name: str = "new_tool"

    def to_params(self) -> dict:
        return {
            "type": "function",
            "name": self.name,
            "description": "Description of what this tool does",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "..."},
                },
                "required": ["param1"]
            }
        }

    async def __call__(self, param1: str, **kwargs) -> ToolResult:
        # Implement tool logic
        result = do_something(param1)
        return ToolResult(output=result)
```

2. Register tool in `collection.py`:
```python
from .new_tool import NewTool

tool_collection = ToolCollection(
    ComputerTool(),
    NewTool(),  # Add here
    # ... other tools
)
```

### Modifying Detection Model

1. Train/fine-tune new YOLO model on your dataset
2. Save weights to `weights/icon_detect_custom/model.pt`
3. Update server launch:
```bash
python -m omniparserserver \
  --som_model_path ../../weights/icon_detect_custom/model.pt
```

4. Or modify default in `omniparser.py`:
```python
DEFAULT_CONFIG = {
    'som_model_path': 'weights/icon_detect_custom/model.pt',
    # ...
}
```

### Changing OCR Backend

Modify `util/utils.py`:
```python
def check_ocr_box(image, bbox, ocr_method='paddle'):  # Change default
    if ocr_method == 'easyocr':
        # EasyOCR logic
    elif ocr_method == 'paddle':
        # PaddleOCR logic
    elif ocr_method == 'custom':  # Add custom OCR
        # Your OCR logic
```

### Adding New Evaluation Benchmark

1. Create evaluation script in `eval/`:
```python
# eval/new_benchmark.py
from util.omniparser import Omniparser

def evaluate_on_benchmark():
    parser = Omniparser(config)

    # Load benchmark dataset
    dataset = load_benchmark()

    results = []
    for item in dataset:
        prediction = parser.parse(item['image'])
        score = compute_metric(prediction, item['ground_truth'])
        results.append(score)

    print(f"Average score: {sum(results) / len(results)}")

if __name__ == '__main__':
    evaluate_on_benchmark()
```

2. Document in `docs/`:
```markdown
# docs/NewBenchmark.md

## Benchmark Description
...

## Results
OmniParser V2: XX%
```

### Improving Icon Caption Model

1. Fine-tune Florence-2 on your icon dataset:
```python
from transformers import AutoModelForCausalLM, AutoProcessor

model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-base",
    trust_remote_code=True
)

# Fine-tuning code...
model.save_pretrained("weights/icon_caption_custom")
```

2. Update server configuration:
```bash
python -m omniparserserver \
  --caption_model_path ../../weights/icon_caption_custom
```

---

## API Reference

### REST API (OmniParser Server)

#### Base URL
Default: `http://localhost:8000`

#### Endpoints

**POST /parse/**

Parses a screenshot and returns annotated image with detected elements.

Request:
```json
{
  "base64_image": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

Response:
```json
{
  "som_image_base64": "iVBORw0KGgoAAAA...",  // Annotated image
  "parsed_content_list": [
    {
      "type": "text",
      "bbox": [0.1, 0.2, 0.3, 0.25],  // Normalized coordinates
      "content": "Start Button",
      "interactivity": true
    },
    {
      "type": "icon",
      "bbox": [0.5, 0.5, 0.6, 0.6],
      "content": "Search icon showing magnifying glass",
      "interactivity": true
    }
  ],
  "latency": 0.523  // Processing time in seconds
}
```

**GET /probe/**

Health check endpoint.

Response:
```json
{
  "message": "Omniparser API ready"
}
```

### Python API

#### Omniparser Class

```python
from util.omniparser import Omniparser

# Initialize
config = {
    'som_model_path': 'weights/icon_detect/model.pt',
    'caption_model_name': 'florence2',  # or 'blip2'
    'caption_model_path': 'weights/icon_caption_florence',
    'BOX_TRESHOLD': 0.05,  # Detection confidence threshold
    'device': 'cuda',  # or 'cpu'
    'ocr_method': 'easyocr',  # or 'paddle'
    'ICON_DETECT_IMAGE_SIZE': 1920,  # Input image size for detection
    'IOU_THRESHOLD': 0.8  # IoU threshold for deduplication
}

parser = Omniparser(config)

# Parse image
import base64
with open('screenshot.png', 'rb') as f:
    base64_image = base64.b64encode(f.read()).decode('utf-8')

labeled_img_base64, parsed_content_list = parser.parse(base64_image)

# Save annotated image
import base64
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(labeled_img_base64))

# Access parsed elements
for element in parsed_content_list:
    print(f"{element['type']}: {element['content']} at {element['bbox']}")
```

#### Agent Loop

```python
from omnitool.gradio.loop import sampling_loop_sync, APIProvider

def output_callback(text: str):
    print(f"Output: {text}")

def tool_callback(tool_result: dict):
    print(f"Tool: {tool_result}")

def api_callback(response: dict):
    print(f"API: {response}")

# Run agent loop
for message in sampling_loop_sync(
    model="claude-3-5-sonnet-20241022",
    provider=APIProvider.ANTHROPIC,
    messages=[
        {"role": "user", "content": "Open Chrome and search for OmniParser"}
    ],
    output_callback=output_callback,
    tool_output_callback=tool_callback,
    api_response_callback=api_callback,
    api_key="your-anthropic-api-key",
    omniparser_url="http://localhost:8000"
):
    # Process streaming messages
    pass
```

#### OmniParser Client (for agent use)

```python
from omnitool.gradio.agent.llm_utils.omniparserclient import OmniParserClient

client = OmniParserClient(
    omniparser_url="http://localhost:8000",
    windows_host_url="http://localhost:8006"
)

# Capture and parse current screen
som_image, parsed_elements = client.get_parsed_content_with_screenshot()

# Access parsed data
for element in parsed_elements:
    print(element['content'])
```

---

## Security Considerations

### From SECURITY.md

**Report vulnerabilities to Microsoft Security Response Center:**
- Web: https://msrc.microsoft.com/create-report
- Email: secure@microsoft.com
- PGP Key: https://aka.ms/security.md/msrc/pgp

**Do NOT report security issues via public GitHub issues.**

### Responsible AI Considerations

From the project documentation:

1. **Icon Caption Model Training**: Trained with Responsible AI data to avoid inferring sensitive attributes (race, religion, etc.) from individuals in icon images.

2. **Content Guidelines**: Users should only apply OmniParser to screenshots without harmful/violent content.

3. **Human-in-the-Loop**: For OmniTool agent system, humans should stay in the loop to minimize risks.

4. **Threat Modeling**: OmniTool has been analyzed using Microsoft Threat Modeling Tool.

### Security Best Practices for Development

#### 1. API Key Management
```python
# NEVER hardcode API keys
# BAD:
api_key = "sk-ant-..."

# GOOD:
import os
api_key = os.environ.get('ANTHROPIC_API_KEY')

# Or use user input in UI:
api_key = gr.Textbox(label="API Key", type="password")
```

#### 2. Input Validation
```python
# Validate base64 images
def validate_base64_image(base64_str: str) -> bool:
    try:
        image_data = base64.b64decode(base64_str)
        # Check size limits
        if len(image_data) > 10_000_000:  # 10MB
            raise ValueError("Image too large")
        return True
    except Exception as e:
        return False
```

#### 3. VM Isolation
- OmniBox VM is isolated via Docker
- No direct network access from VM to host
- Use HTTP API for controlled interaction

#### 4. Model Weights
- Verify model checksums after download
- Use official HuggingFace repositories only
- Check licenses before use (YOLO is AGPL, others MIT)

#### 5. Code Execution
- Be cautious with `pyautogui` and `uiautomation` - they control the real system
- Always validate tool inputs before execution
- Implement action throttling to prevent abuse

---

## Git Workflow

### Branch Strategy

Development follows a feature branch workflow:
```
main (protected) ← Pull Requests ← feature/your-feature
```

### Typical Workflow

```bash
# 1. Create feature branch
git checkout -b feature/add-new-tool

# 2. Make changes
# ... edit files ...

# 3. Stage and commit
git add omnitool/gradio/tools/new_tool.py
git commit -m "Add new tool for file operations"

# 4. Push to remote
git push -u origin feature/add-new-tool

# 5. Create Pull Request on GitHub
# ... use GitHub UI ...

# 6. After review and merge, cleanup
git checkout main
git pull origin main
git branch -d feature/add-new-tool
```

### Commit Message Conventions

Follow conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

Examples:
```bash
git commit -m "feat(agent): Add DeepSeek R1 support"
git commit -m "fix(server): Handle missing caption model gracefully"
git commit -m "docs: Update CLAUDE.md with API reference"
git commit -m "refactor(utils): Optimize bounding box deduplication"
```

### Files to Never Commit

From `.gitignore`:
```
weights/                    # Model checkpoints (too large)
__pycache__/               # Python cache
.gradio/                   # Gradio cache
debug.ipynb                # Personal debug notebooks
omnitool/gradio/uploads/   # User uploads
```

### Pre-commit Hooks

Currently no pre-commit configuration, but `pre-commit` package is installed.

To set up (recommended):
```bash
# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.7
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
EOF

# Install hooks
pre-commit install
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Model Weights Not Found

**Error:**
```
FileNotFoundError: weights/icon_detect/model.pt not found
```

**Solution:**
```bash
cd OmniParser
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} \
         icon_caption/{config.json,generation_config.json,model.safetensors}; do
  huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
done
mv weights/icon_caption weights/icon_caption_florence
```

#### 2. CUDA Out of Memory

**Error:**
```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**Solutions:**
```python
# Option 1: Reduce image size
config = {
    'ICON_DETECT_IMAGE_SIZE': 1280,  # Default is 1920
    ...
}

# Option 2: Use CPU
config = {
    'device': 'cpu',
    ...
}

# Option 3: Run server on separate GPU machine
python -m omniparserserver --device cuda
# Connect from gradio with --omniparser_server_url <remote-ip>:8000
```

#### 3. OmniBox VM Not Starting

**Error:**
```
Validation errors: Windows Host is not responding
```

**Solutions:**
```bash
# Check VM is fully set up (terminal should be closed)
# View at: http://localhost:8006/vnc.html

# Option 1: Wait 10 minutes for full setup

# Option 2: Restart VM
cd omnitool/omnibox/scripts
./manage_vm.sh stop
./manage_vm.sh start

# Option 3: Recreate VM (uses existing storage)
./manage_vm.sh delete
./manage_vm.sh create

# Option 4: Factory reset
./manage_vm.sh delete
rm -rf ../vm/win11storage
./manage_vm.sh create
```

#### 4. PaddleOCR Module Not Found (Windows)

**Error:**
```
libpaddle: The specified module could not be found
```

**Solution:**
Install Visual C++ Redistributable:
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart
- Reinstall requirements: `pip install -r requirements.txt`

#### 5. Icon Captions Are Poor Quality

**Possible Causes:**
1. Wrong model loaded (BLIP2 instead of Florence-2)
2. Model path incorrect
3. Detection threshold too high

**Solutions:**
```bash
# Verify caption model
ls weights/icon_caption_florence/
# Should contain: config.json, generation_config.json, model.safetensors

# Lower detection threshold
python -m omniparserserver --BOX_TRESHOLD 0.03

# Use Florence-2 (not BLIP2)
python -m omniparserserver \
  --caption_model_name florence2 \
  --caption_model_path ../../weights/icon_caption_florence
```

#### 6. Agent Not Taking Actions

**Possible Causes:**
1. OmniParser server not running
2. VM not accessible
3. API key invalid
4. Tool execution failing

**Debug Steps:**
```bash
# 1. Check OmniParser server
curl http://localhost:8000/probe/
# Should return: {"message": "Omniparser API ready"}

# 2. Check VM server
docker exec -it omni-windows bash -c "curl http://localhost:5000/probe"
# Should return: {"message": "Server ready"}

# 3. Check Gradio logs
# Look for error messages in terminal running app.py

# 4. Enable debug mode in loop.py
# Add print statements to see tool calls and responses
```

#### 7. Slow Inference

**Performance Optimization:**
```python
# Use GPU
config = {'device': 'cuda', ...}

# Reduce image size
config = {'ICON_DETECT_IMAGE_SIZE': 1280, ...}

# Use faster caption model (Florence-2 vs BLIP2)
config = {'caption_model_name': 'florence2', ...}

# Use V2 models (60% faster than V1)
# Ensure using OmniParser-v2.0 weights
```

#### 8. Bounding Boxes Overlap Too Much

**Solution:**
```python
# Adjust IoU threshold (higher = more aggressive deduplication)
config = {
    'IOU_THRESHOLD': 0.9,  # Default is 0.8
    ...
}

# Or modify in gradio_demo.py
iou_threshold = gr.Slider(0, 1, value=0.9, label='IOU Threshold')
```

---

## Additional Resources

### Documentation
- **Main README**: `/README.md`
- **OmniTool README**: `/omnitool/readme.md`
- **Evaluation Guide**: `/docs/Evaluation.md`
- **Security**: `/SECURITY.md`

### External Links
- **Project Page**: https://microsoft.github.io/OmniParser/
- **V2 Blog Post**: https://www.microsoft.com/en-us/research/articles/omniparser-v2-turning-any-llm-into-a-computer-use-agent/
- **HuggingFace Models V2**: https://huggingface.co/microsoft/OmniParser-v2.0
- **HuggingFace Models V1.5**: https://huggingface.co/microsoft/OmniParser
- **HuggingFace Demo**: https://huggingface.co/spaces/microsoft/OmniParser-v2
- **Paper (arXiv)**: https://arxiv.org/abs/2408.00203

### Related Projects
- **Claude Computer Use**: https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo
- **OS World**: https://github.com/xlang-ai/OSWorld
- **Windows Agent Arena**: https://github.com/microsoft/WindowsAgentArena
- **Computer Use OOTB**: https://github.com/showlab/computer_use_ootb
- **ScreenSpot Pro**: https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding

### Model Licenses
- **YOLO Detection Model**: AGPL-3.0 (due to Ultralytics YOLO license)
- **Florence-2 Caption Model**: MIT License
- **BLIP2 Caption Model**: MIT License
- **Repository Code**: MIT License

---

## Quick Reference Commands

### Daily Development

```bash
# Start OmniParser server
cd omnitool/omniparserserver
python -m omniparserserver

# Start OmniBox VM
cd omnitool/omnibox/scripts
./manage_vm.sh start

# Start Gradio UI
cd omnitool/gradio
python app.py

# Run simple demo
python gradio_demo.py

# Run evaluation
cd eval
python ss_pro_gpt4o_omniv2.py

# Format code
ruff check . --fix
ruff format .
```

### Model Management

```bash
# Download V2 models
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} \
         icon_caption/{config.json,generation_config.json,model.safetensors}; do
  huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
done
mv weights/icon_caption weights/icon_caption_florence

# Clean model cache
rm -rf weights/icon_caption_blip2
rm -rf weights/icon_caption_florence
rm -rf weights/icon_detect
```

### VM Management

```bash
cd omnitool/omnibox/scripts

# Create (first time)
./manage_vm.sh create

# Start/Stop
./manage_vm.sh start
./manage_vm.sh stop

# Delete
./manage_vm.sh delete

# Factory reset
./manage_vm.sh delete
rm -rf ../vm/win11storage
./manage_vm.sh create
```

---

## Version Information

- **Current Version**: V2.0
- **Python**: 3.12
- **PyTorch**: Latest compatible
- **Gradio**: Latest
- **Anthropic SDK**: ≥0.37.1
- **OpenAI SDK**: 1.3.5

**Last Updated**: 2026-01-06

---

## Contributing Guidelines

When contributing to OmniParser:

1. **Before Starting**:
   - Check existing issues and PRs
   - Discuss major changes in issues first
   - Read this CLAUDE.md thoroughly

2. **Code Standards**:
   - Follow existing code style
   - Add type hints to new functions
   - Keep functions focused and small
   - Document complex logic with comments

3. **Testing**:
   - Test your changes with `gradio_demo.py`
   - Verify full stack with OmniBox + Gradio
   - Run on both CPU and GPU if possible
   - Test with multiple LLM providers

4. **Documentation**:
   - Update README.md if adding features
   - Update this CLAUDE.md if changing architecture
   - Add docstrings to new classes/functions
   - Include usage examples

5. **Pull Requests**:
   - Use descriptive PR titles
   - Reference related issues
   - Describe what changed and why
   - Include screenshots/videos for UI changes

---

## Notes for AI Assistants

### When Working with This Codebase

1. **Always read files before modifying** - The code is complex and interconnected
2. **Check model weights exist** - Many errors stem from missing weights
3. **Understand the data flow** - Screenshot → Parser → Agent → Tools → VM
4. **Test incrementally** - Start with `gradio_demo.py` before full stack
5. **Respect licenses** - YOLO is AGPL, requires attribution and open source

### Common Pitfalls to Avoid

1. **Don't commit model weights** - They're in `.gitignore` for a reason (too large)
2. **Don't hardcode paths** - Use relative paths from project root
3. **Don't assume GPU** - Code should work on CPU (albeit slower)
4. **Don't modify tool definitions without updating executor** - They must stay in sync
5. **Don't skip VM setup** - Full agent testing requires OmniBox

### Helpful Context

- This is a research project from Microsoft
- Focus is on GUI understanding and agent control
- Performance is critical (real-time agent actions)
- Multi-modal: vision + language + action
- Active development (V2 just released Feb 2025)

### When in Doubt

1. Check `demo.ipynb` for usage examples
2. Read function docstrings (where available)
3. Look at existing agent implementations for patterns
4. Test with simple cases first
5. Ask user for clarification on ambiguous requirements

---

**End of CLAUDE.md**
