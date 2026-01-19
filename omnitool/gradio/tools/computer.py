import base64
import time
import platform
from enum import StrEnum
from typing import Literal, TypedDict
from pathlib import Path
from uuid import uuid4

from PIL import Image

from anthropic.types.beta import BetaToolComputerUse20241022Param

from .base import BaseAnthropicTool, ToolError, ToolResult
from .window_manager import get_window_manager
import requests
import re

OUTPUT_DIR = "./tmp/outputs"

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

# Detect platform
PLATFORM = platform.system()  # 'Darwin' (macOS), 'Windows', 'Linux'

Action = Literal[
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "screenshot",
    "cursor_position",
    "hover",
    "wait",
    "list_windows",
    "get_active_window",
    "focus_window"
]


class Resolution(TypedDict):
    width: int
    height: int


MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),  # 4:3
    "WXGA": Resolution(width=1280, height=800),  # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]

class ComputerTool(BaseAnthropicTool):
    """
    A tool that allows the agent to interact with the screen, keyboard, and mouse.
    Cross-platform: Works natively on macOS, Windows, Linux.
    Falls back to VM mode if Windows VM is available (optional).
    """

    name: Literal["computer"] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"
    width: int
    height: int
    display_num: int | None
    use_vm: bool = False  # Whether to use VM or native mode

    _screenshot_delay = 2.0
    _scaling_enabled = True

    @property
    def options(self) -> ComputerToolOptions:
        width, height = self.scale_coordinates(
            ScalingSource.COMPUTER, self.width, self.height
        )
        return {
            "display_width_px": width,
            "display_height_px": height,
            "display_number": self.display_num,
        }

    def to_params(self) -> BetaToolComputerUse20241022Param:
        return {"name": self.name, "type": self.api_type, **self.options}

    def __init__(self, is_scaling: bool = False):
        super().__init__()

        # Detect if Windows VM is available
        self.use_vm = self._check_vm_available()

        if self.use_vm:
            print(f"✓ Windows VM detected - using VM mode")
        else:
            print(f"✓ Running in native mode on {PLATFORM}")

        # Get screen width and height
        self.display_num = None
        self.offset_x = 0
        self.offset_y = 0
        self.is_scaling = is_scaling
        self.width, self.height = self.get_screen_size()
        print(f"  Screen size: {self.width}x{self.height}")

        # Platform-specific key conversions
        self.key_conversion = {
            "Page_Down": "pagedown",
            "Page_Up": "pageup",
            "Super_L": "command" if PLATFORM == "Darwin" else "win",
            "Escape": "esc"
        }

    def _check_vm_available(self) -> bool:
        """Check if Windows VM is available on localhost:5000"""
        try:
            response = requests.get("http://localhost:5000/probe", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _execute_action(self, action: str, parse_output: bool = False):
        """Execute pyautogui action either via VM or natively"""
        if self.use_vm:
            return self._execute_via_vm(action, parse_output)
        else:
            return self._execute_native(action, parse_output)

    def _execute_via_vm(self, action: str, parse_output: bool = False):
        """Execute action via Windows VM HTTP endpoint"""
        prefix = "import pyautogui; pyautogui.FAILSAFE = False;"
        command_list = ["python", "-c", f"{prefix} {action}"]

        if parse_output:
            command_list[-1] = f"{prefix} print({action})"

        try:
            response = requests.post(
                "http://localhost:5000/execute",
                headers={'Content-Type': 'application/json'},
                json={"command": command_list},
                timeout=90
            )
            time.sleep(0.7)  # Avoid async errors

            if response.status_code != 200:
                raise ToolError(f"VM command failed: HTTP {response.status_code}")

            if parse_output:
                output = response.json()['output'].strip()
                match = re.search(r'Point\(x=(\d+),\s*y=(\d+)\)', output)
                if match:
                    return tuple(map(int, match.groups()))
                raise ToolError(f"Could not parse output: {output}")

        except requests.exceptions.RequestException as e:
            raise ToolError(f"VM communication error: {str(e)}")

    def _execute_native(self, action: str, parse_output: bool = False):
        """Execute action natively using pyautogui"""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False

            # Execute the action
            result = eval(action)

            if parse_output:
                # Return tuple for position queries
                return (result.x, result.y) if hasattr(result, 'x') else result

            return result

        except Exception as e:
            raise ToolError(f"Native execution error: {str(e)}")

    async def __call__(
        self,
        *,
        action: Action,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        **kwargs,
    ):
        print(f"action: {action}, text: {text}, coordinate: {coordinate}, is_scaling: {self.is_scaling}")

        # Mouse movement actions
        if action in ("mouse_move", "left_click_drag"):
            if coordinate is None:
                raise ToolError(f"coordinate is required for {action}")
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
                raise ToolError(f"{coordinate} must be a tuple of length 2")
            if not all(isinstance(i, int) for i in coordinate):
                raise ToolError(f"{coordinate} must be a tuple of ints")

            if self.is_scaling:
                x, y = self.scale_coordinates(
                    ScalingSource.API, coordinate[0], coordinate[1]
                )
            else:
                x, y = coordinate

            print(f"mouse move to {x}, {y}")

            if action == "mouse_move":
                self._execute_action(f"pyautogui.moveTo({x}, {y})")
                return ToolResult(output=f"Moved mouse to ({x}, {y})")
            elif action == "left_click_drag":
                current_x, current_y = self._execute_action("pyautogui.position()", parse_output=True)
                self._execute_action(f"pyautogui.dragTo({x}, {y}, duration=0.5)")
                return ToolResult(output=f"Dragged mouse from ({current_x}, {current_y}) to ({x}, {y})")

        # Keyboard actions
        if action in ("key", "type"):
            if text is None:
                raise ToolError(f"text is required for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")
            if not isinstance(text, str):
                raise ToolError(output=f"{text} must be a string")

            if action == "key":
                # Handle key combinations
                keys = text.split('+')
                for key in keys:
                    key = self.key_conversion.get(key.strip(), key.strip())
                    key = key.lower()
                    self._execute_action(f"pyautogui.keyDown('{key}')")
                for key in reversed(keys):
                    key = self.key_conversion.get(key.strip(), key.strip())
                    key = key.lower()
                    self._execute_action(f"pyautogui.keyUp('{key}')")
                return ToolResult(output=f"Pressed keys: {text}")

            elif action == "type":
                # Default click before type
                self._execute_action("pyautogui.click()")
                self._execute_action(f"pyautogui.typewrite('{text}', interval={TYPING_DELAY_MS / 1000})")
                self._execute_action("pyautogui.press('enter')")
                screenshot_base64 = (await self.screenshot()).base64_image
                return ToolResult(output=text, base64_image=screenshot_base64)

        # Click and screenshot actions
        if action in (
            "left_click",
            "right_click",
            "double_click",
            "middle_click",
            "screenshot",
            "cursor_position",
            "left_press",
        ):
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")

            if action == "screenshot":
                return await self.screenshot()
            elif action == "cursor_position":
                x, y = self._execute_action("pyautogui.position()", parse_output=True)
                x, y = self.scale_coordinates(ScalingSource.COMPUTER, x, y)
                return ToolResult(output=f"X={x},Y={y}")
            else:
                if action == "left_click":
                    self._execute_action("pyautogui.click()")
                elif action == "right_click":
                    self._execute_action("pyautogui.rightClick()")
                elif action == "middle_click":
                    self._execute_action("pyautogui.middleClick()")
                elif action == "double_click":
                    self._execute_action("pyautogui.doubleClick()")
                elif action == "left_press":
                    self._execute_action("pyautogui.mouseDown()")
                    time.sleep(1)
                    self._execute_action("pyautogui.mouseUp()")
                return ToolResult(output=f"Performed {action}")

        # Scroll actions
        if action in ("scroll_up", "scroll_down"):
            if action == "scroll_up":
                self._execute_action("pyautogui.scroll(100)")
            elif action == "scroll_down":
                self._execute_action("pyautogui.scroll(-100)")
            return ToolResult(output=f"Performed {action}")

        if action == "hover":
            return ToolResult(output=f"Performed {action}")

        if action == "wait":
            time.sleep(1)
            return ToolResult(output=f"Performed {action}")

        # Window management actions (cross-platform)
        if action == "list_windows":
            if text is not None or coordinate is not None:
                raise ToolError(f"list_windows does not accept text or coordinate parameters")
            return self.list_windows()

        if action == "get_active_window":
            if text is not None or coordinate is not None:
                raise ToolError(f"get_active_window does not accept text or coordinate parameters")
            return self.get_active_window()

        if action == "focus_window":
            if text is None:
                raise ToolError(f"text (window title) is required for focus_window")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for focus_window")
            if not isinstance(text, str):
                raise ToolError(f"{text} must be a string")
            return self.focus_window(text)

        raise ToolError(f"Invalid action: {action}")

    async def screenshot(self):
        """Capture screenshot (cross-platform)"""
        if not hasattr(self, 'target_dimension'):
            self.target_dimension = MAX_SCALING_TARGETS["WXGA"]

        width, height = self.target_dimension["width"], self.target_dimension["height"]

        # Create output directory
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"screenshot_{uuid4().hex}.png"

        try:
            if self.use_vm:
                # Get screenshot from VM
                response = requests.get('http://localhost:5000/screenshot', timeout=10)
                if response.status_code != 200:
                    raise ToolError(f"Failed to capture screenshot: HTTP {response.status_code}")
                from io import BytesIO
                screenshot = Image.open(BytesIO(response.content))
            else:
                # Native screenshot using pyautogui
                import pyautogui
                screenshot = pyautogui.screenshot()

            # Resize if needed
            if screenshot.size != (width, height):
                screenshot = screenshot.resize((width, height))

            screenshot.save(path)
            time.sleep(0.7)  # Avoid async errors

            return ToolResult(base64_image=base64.b64encode(path.read_bytes()).decode())

        except Exception as e:
            raise ToolError(f"Failed to capture screenshot: {str(e)}")

    def padding_image(self, screenshot):
        """Pad the screenshot to 16:10 aspect ratio"""
        _, height = screenshot.size
        new_width = height * 16 // 10

        padding_image = Image.new("RGB", (new_width, height), (255, 255, 255))
        padding_image.paste(screenshot, (0, 0))
        return padding_image

    def scale_coordinates(self, source: ScalingSource, x: int, y: int):
        """Scale coordinates to a target maximum resolution"""
        if not self._scaling_enabled:
            return x, y

        ratio = self.width / self.height
        target_dimension = None

        for target_name, dimension in MAX_SCALING_TARGETS.items():
            if abs(dimension["width"] / dimension["height"] - ratio) < 0.02:
                if dimension["width"] < self.width:
                    target_dimension = dimension
                    self.target_dimension = target_dimension
                break

        if target_dimension is None:
            target_dimension = MAX_SCALING_TARGETS["WXGA"]
            self.target_dimension = MAX_SCALING_TARGETS["WXGA"]

        x_scaling_factor = target_dimension["width"] / self.width
        y_scaling_factor = target_dimension["height"] / self.height

        if source == ScalingSource.API:
            if x > self.width or y > self.height:
                raise ToolError(f"Coordinates {x}, {y} are out of bounds")
            return round(x / x_scaling_factor), round(y / y_scaling_factor)

        return round(x * x_scaling_factor), round(y * y_scaling_factor)

    def get_screen_size(self):
        """Return width and height of the screen (cross-platform)"""
        try:
            if self.use_vm:
                # Get screen size from VM
                response = requests.post(
                    "http://localhost:5000/execute",
                    headers={'Content-Type': 'application/json'},
                    json={"command": ["python", "-c", "import pyautogui; print(pyautogui.size())"]},
                    timeout=10
                )
                if response.status_code != 200:
                    raise ToolError(f"Failed to get screen size: HTTP {response.status_code}")

                output = response.json()['output'].strip()
                match = re.search(r'Size\(width=(\d+),\s*height=(\d+)\)', output)
                if not match:
                    raise ToolError(f"Could not parse screen size: {output}")
                return tuple(map(int, match.groups()))
            else:
                # Native screen size detection
                import pyautogui
                size = pyautogui.size()
                return size.width, size.height

        except Exception as e:
            raise ToolError(f"Failed to get screen size: {str(e)}")

    def list_windows(self) -> ToolResult:
        """List all open windows (cross-platform)"""
        try:
            wm = get_window_manager()
            windows = wm.list_windows()

            if not windows:
                return ToolResult(output="No windows found")

            output_lines = ["Open windows:"]
            for i, w in enumerate(windows, 1):
                active_marker = " [ACTIVE]" if w.get('active', False) else ""
                title = w.get('title', 'Unknown')
                app = w.get('app', 'Unknown')
                output_lines.append(f"{i}. {title} ({app}){active_marker}")

            return ToolResult(output="\n".join(output_lines))
        except Exception as e:
            raise ToolError(f"Failed to list windows: {str(e)}")

    def get_active_window(self) -> ToolResult:
        """Get the currently active window (cross-platform)"""
        try:
            wm = get_window_manager()
            window = wm.get_active_window()

            if not window:
                return ToolResult(output="No active window found")

            title = window.get('title', 'Unknown')
            app = window.get('app', 'Unknown')
            return ToolResult(output=f"Active window: {title} ({app})")
        except Exception as e:
            raise ToolError(f"Failed to get active window: {str(e)}")

    def focus_window(self, title: str) -> ToolResult:
        """Focus a window by partial title match (cross-platform)"""
        try:
            wm = get_window_manager()
            success = wm.focus_window(title)

            if not success:
                return ToolResult(error=f"No window found matching: {title}")

            return ToolResult(output=f"Focused window matching: {title}")
        except Exception as e:
            raise ToolError(f"Failed to focus window: {str(e)}")
