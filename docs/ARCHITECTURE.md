# Architecture & Patterns

## System Architecture

```
[Gradio UI] ←HTTP→ [OmniParser Server] ←HTTP→ [Windows VM]
                          ↓
              [YOLO → OCR → Florence-2]
```

## Design Patterns

### 1. Modular ML Pipeline
Components are swappable: Detection (YOLO) → OCR (EasyOCR/Paddle) → Caption (Florence-2/BLIP2) → Dedupe

### 2. Tool-Based Agent
Follows Anthropic's Computer Use pattern:
```python
class BaseAnthropicTool:
    def to_params(self) -> dict: ...
    async def __call__(self, **kwargs) -> ToolResult: ...
```

### 3. Message Loop
```python
while not done:
    response = agent.call(messages)
    tool_results = executor.execute(response)
    messages.append(tool_results)
```

## Key Files

| File | Role |
|------|------|
| `util/utils.py` | `get_yolo_model()`, `get_som_labeled_img()`, `check_ocr_box()`, `remove_overlap()` |
| `omnitool/gradio/loop.py` | `sampling_loop_sync()` - main agent orchestration |
| `omnitool/gradio/tools/computer.py` | `mouse_move`, `left_click`, `type`, `key`, `screenshot` |

## Code Conventions

### Configuration
```python
config = {
    'som_model_path': 'weights/icon_detect/model.pt',
    'caption_model_name': 'florence2',
    'BOX_TRESHOLD': 0.05,
    'device': 'cuda'
}
parser = Omniparser(config)
```

### Image Encoding
All images as base64:
```python
base64_image = base64.b64encode(img_bytes).decode('utf-8')
```

### Coordinates
- API: normalized [0-1] `[x_min/w, y_min/h, x_max/w, y_max/h]`
- Internal: pixels `[x_min_px, y_min_px, x_max_px, y_max_px]`

### Type Hints
Use Python annotations throughout:
```python
def sampling_loop_sync(
    model: str,
    provider: APIProvider,
    messages: list[dict],
    api_key: str,
    omniparser_url: Optional[str] = None
) -> Generator[dict, None, None]: ...
```

## Architectural Decisions

| Choice | Reason |
|--------|--------|
| FastAPI | Async support, auto OpenAPI docs |
| Gradio | Rapid prototyping, built-in components |
| Florence-2 over BLIP2 | Better UI performance, faster, MIT license |
| YOLO | State-of-the-art detection, fast inference |

## Directory Purposes

| Directory | When to Modify |
|-----------|----------------|
| `util/` | ML model changes, detection/OCR improvements |
| `omnitool/gradio/` | UI changes, agent behavior, new LLM support |
| `omnitool/omniparserserver/` | API endpoints, server config |
| `omnitool/omnibox/` | VM config, Docker setup |
| `eval/` | New benchmarks, evaluation metrics |
