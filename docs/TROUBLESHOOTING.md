# Troubleshooting

## Model Weights Not Found

```
FileNotFoundError: weights/icon_detect/model.pt not found
```

**Fix:**
```bash
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} \
         icon_caption/{config.json,generation_config.json,model.safetensors}; do
  huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
done
mv weights/icon_caption weights/icon_caption_florence
```

## CUDA Out of Memory

```
torch.cuda.OutOfMemoryError
```

**Fix:** Reduce image size, use CPU, or run server remotely:
```python
config = {'ICON_DETECT_IMAGE_SIZE': 1280, 'device': 'cpu'}
```

## OmniBox VM Not Starting

```
Windows Host is not responding
```

**Fix:**
```bash
cd omnitool/omnibox/scripts
./manage_vm.sh stop && ./manage_vm.sh start  # Restart
# Or factory reset:
./manage_vm.sh delete && rm -rf ../vm/win11storage && ./manage_vm.sh create
```

Check: http://localhost:8006/vnc.html (wait 10 mins for full setup)

## PaddleOCR Not Found (Windows)

```
libpaddle: The specified module could not be found
```

**Fix:** Install [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe), restart, reinstall requirements.

## Poor Icon Captions

**Fix:** Verify Florence-2 model and lower threshold:
```bash
ls weights/icon_caption_florence/  # Should have config.json, model.safetensors
python -m omniparserserver --caption_model_name florence2 --BOX_TRESHOLD 0.03
```

## Agent Not Taking Actions

**Debug:**
```bash
curl http://localhost:8000/probe/  # Should return "Omniparser API ready"
docker exec -it omni-windows bash -c "curl http://localhost:5000/probe"
```

Check Gradio terminal logs for errors.

## Slow Inference

**Fix:**
```python
config = {
    'device': 'cuda',
    'ICON_DETECT_IMAGE_SIZE': 1280,
    'caption_model_name': 'florence2'  # Faster than blip2
}
```

## Overlapping Bounding Boxes

**Fix:** Increase IoU threshold:
```python
config = {'IOU_THRESHOLD': 0.9}  # Default 0.8
```

## Health Check Commands

```bash
curl http://localhost:8000/probe/                                    # OmniParser
docker exec -it omni-windows bash -c "curl http://localhost:5000/probe"  # VM
```
