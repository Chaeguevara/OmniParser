from typing import Optional
import gradio as gr
import numpy as np
import torch
from PIL import Image, ImageGrab
import io
import base64
import os
import platform
import threading
import time

from util.utils import check_ocr_box, get_yolo_model, get_caption_model_processor, get_som_labeled_img

# Try to import mss for better cross-platform screen capture
try:
    import mss
    HAS_MSS = True
except ImportError:
    HAS_MSS = False

yolo_model = get_yolo_model(model_path='weights/icon_detect/model.pt')
caption_model_processor = get_caption_model_processor(model_name="florence2", model_name_or_path="weights/icon_caption_florence")

MARKDOWN = """
# OmniParser for Pure Vision Based General GUI Agent 🔥
<div>
    <a href="https://arxiv.org/pdf/2408.00203">
        <img src="https://img.shields.io/badge/arXiv-2408.00203-b31b1b.svg" alt="Arxiv" style="display:inline-block;">
    </a>
</div>

OmniParser is a screen parsing tool to convert general GUI screen to structured elements.

**Modes:**
- **Upload:** Manually upload a screenshot
- **Capture Screen:** Click to capture your current screen
- **Auto-Refresh:** Automatically capture and parse every N seconds
"""

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def capture_screen():
    """Capture the current screen and return as PIL Image."""
    try:
        if HAS_MSS:
            # Use mss for better cross-platform support
            with mss.mss() as sct:
                # Capture the primary monitor
                monitor = sct.monitors[1]  # Primary monitor (0 is all monitors)
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                return img
        else:
            # Fallback to PIL ImageGrab (works on Windows and macOS)
            screenshot = ImageGrab.grab()
            return screenshot
    except Exception as e:
        print(f"Screen capture error: {e}")
        # Return a placeholder image on error
        return Image.new('RGB', (800, 600), color='gray')


def process(
    image_input,
    box_threshold,
    iou_threshold,
    use_paddleocr,
    imgsz
) -> Optional[Image.Image]:
    if image_input is None:
        return None, "No image provided"

    box_overlay_ratio = image_input.size[0] / 3200
    draw_bbox_config = {
        'text_scale': 0.8 * box_overlay_ratio,
        'text_thickness': max(int(2 * box_overlay_ratio), 1),
        'text_padding': max(int(3 * box_overlay_ratio), 1),
        'thickness': max(int(3 * box_overlay_ratio), 1),
    }

    ocr_bbox_rslt, is_goal_filtered = check_ocr_box(
        image_input,
        display_img=False,
        output_bb_format='xyxy',
        goal_filtering=None,
        easyocr_args={'paragraph': False, 'text_threshold': 0.9},
        use_paddleocr=use_paddleocr
    )
    text, ocr_bbox = ocr_bbox_rslt
    dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
        image_input,
        yolo_model,
        BOX_TRESHOLD=box_threshold,
        output_coord_in_ratio=True,
        ocr_bbox=ocr_bbox,
        draw_bbox_config=draw_bbox_config,
        caption_model_processor=caption_model_processor,
        ocr_text=text,
        iou_threshold=iou_threshold,
        imgsz=imgsz
    )
    image = Image.open(io.BytesIO(base64.b64decode(dino_labled_img)))
    print('finish processing')
    parsed_content_list = '\n'.join([f'icon {i}: ' + str(v) for i, v in enumerate(parsed_content_list)])
    return image, str(parsed_content_list)


def capture_and_process(box_threshold, iou_threshold, use_paddleocr, imgsz):
    """Capture screen and process it."""
    screenshot = capture_screen()
    output_image, parsed_text = process(screenshot, box_threshold, iou_threshold, use_paddleocr, imgsz)
    return screenshot, output_image, parsed_text


# Auto-refresh state
auto_refresh_active = False


def toggle_auto_refresh(enabled, interval, box_threshold, iou_threshold, use_paddleocr, imgsz):
    """Toggle auto-refresh mode."""
    global auto_refresh_active
    auto_refresh_active = enabled
    if enabled:
        return capture_and_process(box_threshold, iou_threshold, use_paddleocr, imgsz)
    return None, None, ""


def auto_refresh_tick(enabled, interval, box_threshold, iou_threshold, use_paddleocr, imgsz):
    """Called periodically when auto-refresh is enabled."""
    if enabled:
        return capture_and_process(box_threshold, iou_threshold, use_paddleocr, imgsz)
    return gr.update(), gr.update(), gr.update()


with gr.Blocks() as demo:
    gr.Markdown(MARKDOWN)

    with gr.Row():
        with gr.Column():
            image_input_component = gr.Image(
                type='pil', label='Upload image or use Capture Screen')

            # Screen capture controls
            with gr.Row():
                capture_button = gr.Button(
                    value='📷 Capture Screen', variant='secondary')

            # Auto-refresh controls
            with gr.Row():
                auto_refresh_checkbox = gr.Checkbox(
                    label='🔄 Auto-Refresh', value=False)
                refresh_interval = gr.Slider(
                    label='Refresh Interval (seconds)',
                    minimum=1, maximum=30, step=1, value=5,
                    visible=True)

            gr.Markdown("---")

            # Detection settings
            box_threshold_component = gr.Slider(
                label='Box Threshold', minimum=0.01, maximum=1.0, step=0.01, value=0.05)
            iou_threshold_component = gr.Slider(
                label='IOU Threshold', minimum=0.01, maximum=1.0, step=0.01, value=0.1)
            use_paddleocr_component = gr.Checkbox(
                label='Use PaddleOCR', value=True)
            imgsz_component = gr.Slider(
                label='Icon Detect Image Size', minimum=640, maximum=1920, step=32, value=640)

            submit_button_component = gr.Button(
                value='🔍 Parse Image', variant='primary')

        with gr.Column():
            image_output_component = gr.Image(type='pil', label='Parsed Output')
            text_output_component = gr.Textbox(
                label='Parsed screen elements',
                placeholder='Text Output',
                lines=10)

    # Manual submit button
    submit_button_component.click(
        fn=process,
        inputs=[
            image_input_component,
            box_threshold_component,
            iou_threshold_component,
            use_paddleocr_component,
            imgsz_component
        ],
        outputs=[image_output_component, text_output_component]
    )

    # Capture screen button
    capture_button.click(
        fn=capture_and_process,
        inputs=[
            box_threshold_component,
            iou_threshold_component,
            use_paddleocr_component,
            imgsz_component
        ],
        outputs=[image_input_component, image_output_component, text_output_component]
    )

    # Auto-refresh timer
    timer = gr.Timer(value=5, active=False)

    # Toggle auto-refresh
    auto_refresh_checkbox.change(
        fn=lambda enabled, interval: gr.Timer(value=interval, active=enabled),
        inputs=[auto_refresh_checkbox, refresh_interval],
        outputs=[timer]
    )

    # Update timer interval when slider changes
    refresh_interval.change(
        fn=lambda enabled, interval: gr.Timer(value=interval, active=enabled),
        inputs=[auto_refresh_checkbox, refresh_interval],
        outputs=[timer]
    )

    # Timer tick - capture and process
    timer.tick(
        fn=auto_refresh_tick,
        inputs=[
            auto_refresh_checkbox,
            refresh_interval,
            box_threshold_component,
            iou_threshold_component,
            use_paddleocr_component,
            imgsz_component
        ],
        outputs=[image_input_component, image_output_component, text_output_component]
    )

# Security: share=False by default to prevent public tunnel exposure
demo.launch(share=False, server_port=7861, server_name='127.0.0.1')
