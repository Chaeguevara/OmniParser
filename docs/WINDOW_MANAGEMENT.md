# Cross-Platform Window Management Design

## Current State

**OmniParser is currently Windows-only** due to:
- Windows 11 Docker VM (`omnitool/omnibox/`)
- `uiautomation` library (Windows-specific, in requirements.txt)
- System prompts reference Windows environment

## Problem: Multi-Program Interaction

Current limitations for automating interaction between two programs:
1. ❌ Cannot detect which application is active
2. ❌ Cannot list open windows programmatically
3. ❌ Cannot focus/switch to specific windows by name or process
4. ❌ No application-specific context in UI element parsing
5. ❌ Must manually click taskbar to switch programs

## Proposed Solution: Cross-Platform Window Management API

### Platform-Specific Libraries

| Platform | Library | Capabilities |
|----------|---------|--------------|
| **Windows** | `pygetwindow` | List windows, get titles, activate, minimize, maximize |
| **Windows** | `win32gui` (pywin32) | Advanced window control, enumeration |
| **Linux X11** | `python-xlib` | Window management on X11 systems |
| **Linux Wayland** | `wlr-foreign-toplevel` | Limited support (Wayland restrictions) |
| **macOS** | `pyobjc-framework-Quartz` | Window enumeration via Accessibility API |
| **Cross-platform** | `pyautogui` | Already used! Has `getWindowsWithTitle()` |

### Recommended Approach: Tiered Implementation

```python
# Tier 1: Use pyautogui (already in requirements)
import pyautogui

# Works on Windows, macOS, Linux (X11)
windows = pyautogui.getWindowsWithTitle('Chrome')
if windows:
    windows[0].activate()  # Bring to front

# Tier 2: Platform-specific enhancements
if platform.system() == 'Windows':
    import pygetwindow as gw
    all_windows = gw.getAllWindows()
elif platform.system() == 'Linux':
    # Use wmctrl or xdotool via subprocess
    pass
elif platform.system() == 'Darwin':  # macOS
    # Use AppleScript or Quartz
    pass
```

## API Design

### New Window Management Actions

Add to `omnitool/gradio/tools/computer.py`:

```python
class WindowManagementActions:
    """Cross-platform window management"""

    # Core actions
    list_windows() -> List[Dict]
        # Returns: [{"pid": int, "title": str, "app": str, "active": bool}]

    get_active_window() -> Dict
        # Returns: {"title": str, "app": str, "pid": int}

    focus_window(title: str) -> bool
        # Bring window to front by partial title match

    focus_window_by_app(app_name: str) -> bool
        # Focus by application name (e.g., "Chrome", "Excel")

    switch_to_next_window() -> None
        # Programmatic Alt+Tab

    minimize_window(title: str) -> None
    maximize_window(title: str) -> None
    close_window(title: str) -> None
```

### Enhanced Screen Parsing

Modify `util/utils.py` to tag elements with window context:

```python
# Current output
{
    "type": "text",
    "bbox": [x1, y1, x2, y2],
    "content": "Submit",
    "interactivity": true
}

# Enhanced output
{
    "type": "text",
    "bbox": [x1, y1, x2, y2],
    "content": "Submit",
    "interactivity": true,
    "window": {  # NEW
        "title": "Microsoft Excel",
        "app": "EXCEL.EXE",
        "pid": 1234
    }
}
```

## Implementation Plan

### Phase 1: Basic Window Detection (Minimal Changes)

1. **Add `pygetwindow` to requirements.txt**
   ```
   pygetwindow>=0.0.9  # Windows/Linux/macOS support
   ```

2. **Add window management endpoints to VM server**

   File: `omnitool/omnibox/vm/win11setup/setupscripts/server/main.py`

   ```python
   @app.route('/windows/list', methods=['GET'])
   def list_windows():
       try:
           import pyautogui
           windows = pyautogui.getAllWindows()
           return jsonify([{
               'title': w.title,
               'left': w.left, 'top': w.top,
               'width': w.width, 'height': w.height,
               'active': w.isActive
           } for w in windows])
       except:
           return jsonify({'error': 'Window management not supported'}), 501

   @app.route('/windows/focus', methods=['POST'])
   def focus_window():
       title_query = request.json.get('title')
       windows = pyautogui.getWindowsWithTitle(title_query)
       if windows:
           windows[0].activate()
           return jsonify({'status': 'success'})
       return jsonify({'error': 'Window not found'}), 404
   ```

3. **Add actions to ComputerTool**

   File: `omnitool/gradio/tools/computer.py`

   ```python
   # Add new action types
   WINDOW_ACTIONS = ["list_windows", "focus_window", "get_active_window"]

   def list_windows(self) -> ToolResult:
       response = requests.get(f"{self.windows_host_url}/windows/list")
       return ToolResult(output=response.json())

   def focus_window(self, title: str) -> ToolResult:
       response = requests.post(
           f"{self.windows_host_url}/windows/focus",
           json={'title': title}
       )
       return ToolResult(output=f"Focused window: {title}")
   ```

### Phase 2: Application Context in UI Elements

1. **Detect window boundaries in screenshots**
   - Use window positions from `list_windows()`
   - Map bounding boxes to window regions
   - Tag each parsed element with source window

2. **Update agent system prompts**
   ```
   Available windows:
   - [1] Microsoft Excel (active)
   - [2] Google Chrome
   - [3] Visual Studio Code

   When referencing UI elements, I will specify which window they belong to.

   New actions:
   - focus_window(title="Excel") - Bring window to front
   - list_windows() - See all open applications
   ```

### Phase 3: Full Cross-Platform Support

1. **Platform detection and abstraction**
   ```python
   class WindowManager:
       def __init__(self):
           self.platform = platform.system()
           self.backend = self._get_backend()

       def _get_backend(self):
           if self.platform == 'Windows':
               return WindowsBackend()  # pygetwindow
           elif self.platform == 'Linux':
               return LinuxBackend()    # wmctrl/xdotool
           elif self.platform == 'Darwin':
               return MacOSBackend()    # AppleScript
   ```

2. **Test on multiple platforms**
   - Windows 10/11
   - Ubuntu 22.04+ (X11 and Wayland)
   - macOS 12+

## Security Considerations

### Risks
- Window enumeration reveals running applications (privacy concern)
- Automated window switching could confuse users
- Malicious agents could spy on other applications

### Mitigations
1. **Require explicit permission** for window management actions
2. **Log all window operations** to audit trail
3. **Limit to same user's windows** (no cross-user access)
4. **Add confirmation prompts** for sensitive windows (banking apps, etc.)

## Platform Limitations

| Platform | Limitation | Workaround |
|----------|------------|------------|
| **Wayland (Linux)** | Restricted window management for security | Use X11 compatibility mode or XWayland |
| **macOS** | Requires Accessibility permissions | Prompt user to grant in System Preferences |
| **Windows 11** | Snap Layouts interfere with positioning | Disable Snap Assist programmatically |
| **All** | Fullscreen apps hide other windows | Check if window is fullscreen before actions |

## Testing Strategy

### Unit Tests
```python
def test_list_windows():
    # Open known apps
    subprocess.Popen(['notepad.exe'])
    sleep(1)
    windows = list_windows()
    assert any('Notepad' in w['title'] for w in windows)

def test_focus_window():
    # Open two windows
    # Focus second window
    # Verify it's now active
```

### Integration Tests
```python
def test_multi_app_workflow():
    """Test: Copy from Excel, paste to Word"""
    # 1. Open Excel with data
    # 2. Open Word document
    # 3. focus_window("Excel")
    # 4. Select cell, Ctrl+C
    # 5. focus_window("Word")
    # 6. Ctrl+V
    # 7. Verify paste succeeded
```

## Migration Path

For existing Windows VM users:
1. **No breaking changes** - window management is opt-in
2. **Gradual adoption** - agents can use new actions if available
3. **Fallback behavior** - if window management fails, fall back to clicking taskbar
4. **Feature detection** - agents check if `list_windows` is available before using

## Example Agent Prompt Enhancement

```
You are controlling a computer with these applications open:
1. Google Chrome (PID 1234) - Active
2. Microsoft Excel (PID 5678)
3. Notepad (PID 9012)

To switch between applications, use:
- focus_window("Chrome") - Bring Chrome to front
- focus_window("Excel") - Bring Excel to front

Multi-app workflow example:
1. "Copy data from Excel to Chrome"
   Step 1: focus_window("Excel")
   Step 2: mouse_move to cell, left_click, key("Ctrl+C")
   Step 3: focus_window("Chrome")
   Step 4: mouse_move to input field, left_click, key("Ctrl+V")
```

## Performance Impact

- **Window enumeration**: ~10-50ms (acceptable overhead)
- **Window focus**: ~100-300ms (includes OS animation)
- **No impact on screenshot parsing** (optional feature)

## Future Enhancements

1. **Window geometry tracking** - Remember window positions for consistent automation
2. **Virtual desktops support** - Switch between desktops (Win+Ctrl+Left/Right)
3. **Multi-monitor awareness** - Detect which monitor has which windows
4. **Window grouping** - Group related windows (e.g., all Chrome tabs)
5. **Application lifecycle** - Launch apps if not running, close when done
6. **Smart window selection** - Use ML to predict which window user wants

---

## Quick Start

To enable window management in your OmniParser setup:

```bash
# 1. Add dependency (already done if using current requirements.txt)
pip install pygetwindow

# 2. Test window detection
python -c "import pyautogui; print(pyautogui.getAllWindows())"

# 3. Update VM server with window endpoints (see Phase 1)

# 4. Use in agent prompts
# "List all open windows, then focus Excel and copy the highlighted text"
```
