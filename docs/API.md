# API Reference

## REST API (OmniParser Server)

Base URL: `http://localhost:8000`

### POST /parse/

Parse screenshot, return annotated image + detected elements.

**Request:**
```json
{"base64_image": "iVBORw0KGgoAAAANSUhEUgAA..."}
```

**Response:**
```json
{
  "som_image_base64": "...",
  "parsed_content_list": [
    {"type": "text", "bbox": [0.1, 0.2, 0.3, 0.25], "content": "Start Button", "interactivity": true},
    {"type": "icon", "bbox": [0.5, 0.5, 0.6, 0.6], "content": "Search magnifying glass", "interactivity": true}
  ],
  "latency": 0.523
}
```

### GET /probe/

Health check. Returns: `{"message": "Omniparser API ready"}`

## Python API

### Omniparser Class

```python
from util.omniparser import Omniparser
import base64

config = {
    'som_model_path': 'weights/icon_detect/model.pt',
    'caption_model_name': 'florence2',  # or 'blip2'
    'caption_model_path': 'weights/icon_caption_florence',
    'BOX_TRESHOLD': 0.05,
    'device': 'cuda',  # or 'cpu'
    'ocr_method': 'easyocr',  # or 'paddle'
    'ICON_DETECT_IMAGE_SIZE': 1920,
    'IOU_THRESHOLD': 0.8
}

parser = Omniparser(config)

with open('screenshot.png', 'rb') as f:
    base64_image = base64.b64encode(f.read()).decode('utf-8')

labeled_img_base64, parsed_content_list = parser.parse(base64_image)
```

### Agent Loop

```python
from omnitool.gradio.loop import sampling_loop_sync, APIProvider

for message in sampling_loop_sync(
    model="claude-3-5-sonnet-20241022",
    provider=APIProvider.ANTHROPIC,
    messages=[{"role": "user", "content": "Click the Start button"}],
    output_callback=lambda x: print(f"Output: {x}"),
    tool_output_callback=lambda x: print(f"Tool: {x}"),
    api_response_callback=lambda x: None,
    api_key="your-api-key",
    omniparser_url="http://localhost:8000"
):
    pass
```

### OmniParser Client

```python
from omnitool.gradio.agent.llm_utils.omniparserclient import OmniParserClient

client = OmniParserClient(
    omniparser_url="http://localhost:8000",
    windows_host_url="http://localhost:8006"
)
som_image, parsed_elements = client.get_parsed_content_with_screenshot()
```

## Server CLI Arguments

| Arg | Description | Default |
|-----|-------------|---------|
| `--som_model_path` | YOLO model path | - |
| `--caption_model_name` | 'florence2' or 'blip2' | - |
| `--caption_model_path` | Caption model path | - |
| `--device` | 'cuda' or 'cpu' | - |
| `--BOX_TRESHOLD` | Detection confidence | 0.05 |
| `--host` | Server host | 127.0.0.1 |
| `--port` | Server port | 8000 |
