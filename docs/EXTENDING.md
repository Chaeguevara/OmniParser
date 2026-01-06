# Extending OmniParser

## Adding a New LLM Provider

### 1. Create agent class (`omnitool/gradio/agent/new_provider_agent.py`)

```python
class NewProviderAgent:
    def __init__(self, api_key: str, model: str):
        self.client = NewProviderClient(api_key)
        self.model = model

    def __call__(self, messages: list[dict]) -> dict:
        return self.client.chat(model=self.model, messages=messages)
```

### 2. Add to `loop.py`

```python
class APIProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    NEW_PROVIDER = "new_provider"  # Add

# In sampling_loop_sync():
if provider == APIProvider.NEW_PROVIDER:
    actor = NewProviderAgent(api_key, model)
```

### 3. Add UI option in `app.py`

```python
provider_dropdown = gr.Dropdown(
    choices=["Anthropic", "OpenAI", "NewProvider"],  # Add
    ...
)
```

## Adding a New Tool

### 1. Create tool class (`omnitool/gradio/tools/new_tool.py`)

```python
from .base import BaseAnthropicTool, ToolResult

class NewTool(BaseAnthropicTool):
    name: str = "new_tool"

    def to_params(self) -> dict:
        return {
            "type": "function",
            "name": self.name,
            "description": "Tool description",
            "input_schema": {
                "type": "object",
                "properties": {"param1": {"type": "string"}},
                "required": ["param1"]
            }
        }

    async def __call__(self, param1: str, **kwargs) -> ToolResult:
        result = do_something(param1)
        return ToolResult(output=result)
```

### 2. Register in `collection.py`

```python
from .new_tool import NewTool

tool_collection = ToolCollection(
    ComputerTool(),
    NewTool(),  # Add
)
```

## Modifying Detection Model

1. Train/fine-tune YOLO on your dataset
2. Save to `weights/icon_detect_custom/model.pt`
3. Launch: `python -m omniparserserver --som_model_path ../../weights/icon_detect_custom/model.pt`

## Changing OCR Backend

Modify `util/utils.py`:
```python
def check_ocr_box(image, bbox, ocr_method='paddle'):
    if ocr_method == 'easyocr': ...
    elif ocr_method == 'paddle': ...
    elif ocr_method == 'custom': ...  # Add
```

## Improving Icon Caption Model

1. Fine-tune Florence-2:
```python
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
# Fine-tune...
model.save_pretrained("weights/icon_caption_custom")
```

2. Launch: `python -m omniparserserver --caption_model_path ../../weights/icon_caption_custom`

## Adding Evaluation Benchmark

Create `eval/new_benchmark.py`:
```python
from util.omniparser import Omniparser

def evaluate():
    parser = Omniparser(config)
    dataset = load_benchmark()
    scores = [compute_metric(parser.parse(item['image']), item['ground_truth']) for item in dataset]
    print(f"Score: {sum(scores)/len(scores)}")

if __name__ == '__main__':
    evaluate()
```
