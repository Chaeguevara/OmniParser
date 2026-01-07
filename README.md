# OmniParser: Screen Parsing tool for Pure Vision Based GUI Agent

<p align="center">
  <img src="imgs/logo.png" alt="Logo">
</p>
<!-- <a href="https://trendshift.io/repositories/12975" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12975" alt="microsoft%2FOmniParser | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a> -->

[![arXiv](https://img.shields.io/badge/Paper-green)](https://arxiv.org/abs/2408.00203)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

📢 [[Project Page](https://microsoft.github.io/OmniParser/)] [[V2 Blog Post](https://www.microsoft.com/en-us/research/articles/omniparser-v2-turning-any-llm-into-a-computer-use-agent/)] [[Models V2](https://huggingface.co/microsoft/OmniParser-v2.0)] [[Models V1.5](https://huggingface.co/microsoft/OmniParser)] [[HuggingFace Space Demo](https://huggingface.co/spaces/microsoft/OmniParser-v2)]

**OmniParser** is a comprehensive method for parsing user interface screenshots into structured and easy-to-understand elements, which significantly enhances the ability of GPT-4V to generate actions that can be accurately grounded in the corresponding regions of the interface.

## News
- [2025/1] **Korean OCR support** added with EasyOCR and PaddleOCR. Fixed compatibility with PaddleOCR 3.x and latest transformers.
- [2025/3] We support local logging of trajecotry so that you can use OmniParser+OmniTool to build training data pipeline for your favorate agent in your domain. [Documentation WIP]
- [2025/3] We are gradually adding multi agents orchstration and improving user interface in OmniTool for better experience.
- [2025/2] We release OmniParser V2 [checkpoints](https://huggingface.co/microsoft/OmniParser-v2.0). [Watch Video](https://1drv.ms/v/c/650b027c18d5a573/EWXbVESKWo9Buu6OYCwg06wBeoM97C6EOTG6RjvWLEN1Qg?e=alnHGC)
- [2025/2] We introduce OmniTool: Control a Windows 11 VM with OmniParser + your vision model of choice. OmniTool supports out of the box the following large language models - OpenAI (4o/o1/o3-mini), DeepSeek (R1), Qwen (2.5VL) or Anthropic Computer Use. [Watch Video](https://1drv.ms/v/c/650b027c18d5a573/EehZ7RzY69ZHn-MeQHrnnR4BCj3by-cLLpUVlxMjF4O65Q?e=8LxMgX)
- [2025/1] V2 is coming. We achieve new state of the art results 39.5% on the new grounding benchmark [Screen Spot Pro](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/tree/main) with OmniParser v2 (will be released soon)! Read more details [here](https://github.com/microsoft/OmniParser/tree/master/docs/Evaluation.md).
- [2024/11] We release an updated version, OmniParser V1.5 which features 1) more fine grained/small icon detection, 2) prediction of whether each screen element is interactable or not. Examples in the demo.ipynb.
- [2024/10] OmniParser was the #1 trending model on huggingface model hub (starting 10/29/2024).
- [2024/10] Feel free to checkout our demo on [huggingface space](https://huggingface.co/spaces/microsoft/OmniParser)! (stay tuned for OmniParser + Claude Computer Use)
- [2024/10] Both Interactive Region Detection Model and Icon functional description model are released! [Hugginface models](https://huggingface.co/microsoft/OmniParser)
- [2024/09] OmniParser achieves the best performance on [Windows Agent Arena](https://microsoft.github.io/WindowsAgentArena/)!

## Quick Start

### Option 1: Automated Install (Recommended)

```bash
git clone https://github.com/microsoft/OmniParser.git
cd OmniParser
./install.sh
source venv/bin/activate
```

The script automatically:
- Creates a Python virtual environment
- Detects CUDA and installs appropriate PyTorch
- Installs all dependencies
- Downloads model weights from HuggingFace

### Option 2: Manual Install (Conda)

```bash
cd OmniParser
conda create -n "omni" python==3.12
conda activate omni
pip install -r requirements.txt
```

Download V2 weights:
```bash
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do
  huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
done
mv weights/icon_caption weights/icon_caption_florence
```

## Usage

### 1. Simple Demo (Screenshot Parsing Only)

Parse a screenshot to detect UI elements:

```bash
python gradio_demo.py
```

Open http://localhost:7861 in your browser, upload a screenshot, and see detected elements.

### 2. Full OmniTool Stack (GUI Agent)

OmniTool lets you control a Windows 11 VM using natural language with your choice of vision model.

**Prerequisites:**
- Docker Desktop installed and running
- Windows 11 ISO (place at `omnitool/omnibox/vm/win11iso/custom.iso`)
- API key for your chosen LLM provider

**Step 1: Start OmniParser Server**
```bash
cd omnitool/omniparserserver
python -m omniparserserver \
  --som_model_path ../../weights/icon_detect/model.pt \
  --caption_model_name florence2 \
  --caption_model_path ../../weights/icon_caption_florence \
  --device cuda \
  --BOX_TRESHOLD 0.05
```

**Step 2: Start Windows VM**
```bash
cd omnitool/omnibox/scripts
./manage_vm.sh create   # First time only (20-90 mins)
./manage_vm.sh start    # Start the VM
```

Access VM via browser: http://localhost:8006/vnc.html

**Step 3: Start Gradio UI**
```bash
cd omnitool/gradio
python app.py \
  --windows_host_url localhost:8006 \
  --omniparser_server_url localhost:8000
```

**Step 4: Use the Agent**

1. Open http://localhost:7860
2. Enter your API key (Anthropic, OpenAI, etc.)
3. Select your model (Claude, GPT-4V, Qwen, DeepSeek)
4. Type a task like "Open Chrome and search for weather"
5. Watch the agent control the VM!

### Supported LLM Providers

| Provider | Models | API Key Env Var |
|----------|--------|-----------------|
| Anthropic | Claude 3.5 Sonnet, Claude 3 Opus | `ANTHROPIC_API_KEY` |
| OpenAI | GPT-4o, GPT-4V, o1, o3-mini | `OPENAI_API_KEY` |
| DeepSeek | DeepSeek R1 | `DEEPSEEK_API_KEY` |
| Qwen | Qwen 2.5VL | `DASHSCOPE_API_KEY` |
| Groq | Various | `GROQ_API_KEY` |

## Python API

```python
from util.omniparser import Omniparser
import base64

config = {
    'som_model_path': 'weights/icon_detect/model.pt',
    'caption_model_name': 'florence2',
    'caption_model_path': 'weights/icon_caption_florence',
    'device': 'cuda',  # or 'cpu'
    'BOX_TRESHOLD': 0.05
}

parser = Omniparser(config)

with open('screenshot.png', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode()

labeled_image, elements = parser.parse(image_base64)
# elements: [{"type": "text|icon", "bbox": [x1,y1,x2,y2], "content": "...", "interactivity": bool}, ...]
```

## Examples

We put together a few simple examples in the `demo.ipynb`.

## Documentation

| Topic | File |
|-------|------|
| Environment setup | [docs/SETUP.md](docs/SETUP.md) |
| API reference | [docs/API.md](docs/API.md) |
| Architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Extending | [docs/EXTENDING.md](docs/EXTENDING.md) |
| Troubleshooting | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |

## Compatibility Notes

This fork includes fixes for latest package versions:

| Package | Issue Fixed |
|---------|-------------|
| **PaddleOCR 3.x** | Updated from deprecated `ocr()` to new `predict()` API |
| **transformers** | Added `attn_implementation="eager"` and `use_cache=False` for Florence-2 |
| **Korean OCR** | Added Korean language support (`['en', 'ko']` for EasyOCR, `korean_PP-OCRv5_mobile_rec` for PaddleOCR) |

If you encounter issues with older package versions, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Model Weights License

For the model checkpoints on huggingface model hub, please note that icon_detect model is under AGPL license since it is a license inherited from the original yolo model. And icon_caption_blip2 & icon_caption_florence is under MIT license. Please refer to the LICENSE file in the folder of each model: https://huggingface.co/microsoft/OmniParser.

## 📚 Citation

Our technical report can be found [here](https://arxiv.org/abs/2408.00203).
If you find our work useful, please consider citing our work:
```
@misc{lu2024omniparserpurevisionbased,
      title={OmniParser for Pure Vision Based GUI Agent},
      author={Yadong Lu and Jianwei Yang and Yelong Shen and Ahmed Awadallah},
      year={2024},
      eprint={2408.00203},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2408.00203},
}
```
