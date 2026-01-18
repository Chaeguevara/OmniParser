"""
Cross-platform window management utilities.

Provides window listing, focusing, and management across Windows, macOS, and Linux.
"""

import platform
import subprocess
from typing import List, Dict, Optional


class WindowManager:
    """Cross-platform window management."""

    def __init__(self):
        self.platform = platform.system()

    def list_windows(self) -> List[Dict]:
        """List all open windows with their titles and info.

        Returns:
            List of dicts with keys: title, app, pid, active (bool)
        """
        if self.platform == "Darwin":  # macOS
            return self._list_windows_macos()
        elif self.platform == "Windows":
            return self._list_windows_windows()
        elif self.platform == "Linux":
            return self._list_windows_linux()
        else:
            raise NotImplementedError(f"Platform {self.platform} not supported")

    def get_active_window(self) -> Optional[Dict]:
        """Get the currently active (focused) window.

        Returns:
            Dict with keys: title, app, pid, or None if no window active
        """
        if self.platform == "Darwin":
            return self._get_active_window_macos()
        elif self.platform == "Windows":
            return self._get_active_window_windows()
        elif self.platform == "Linux":
            return self._get_active_window_linux()
        else:
            raise NotImplementedError(f"Platform {self.platform} not supported")

    def focus_window(self, title: str) -> bool:
        """Focus a window by partial title match.

        Args:
            title: Partial window title to match (case-insensitive)

        Returns:
            True if window was found and focused, False otherwise
        """
        if self.platform == "Darwin":
            return self._focus_window_macos(title)
        elif self.platform == "Windows":
            return self._focus_window_windows(title)
        elif self.platform == "Linux":
            return self._focus_window_linux(title)
        else:
            raise NotImplementedError(f"Platform {self.platform} not supported")

    # macOS implementations
    def _list_windows_macos(self) -> List[Dict]:
        """List windows on macOS using AppleScript."""
        try:
            # AppleScript to get all visible windows
            script = '''
            tell application "System Events"
                set windowList to {}
                repeat with theProcess in (every process whose visible is true)
                    try
                        set processName to name of theProcess
                        set processID to unix id of theProcess
                        set isFrontmost to frontmost of theProcess
                        repeat with theWindow in (every window of theProcess)
                            set windowTitle to name of theWindow
                            set end of windowList to {processName, windowTitle, processID, isFrontmost}
                        end repeat
                    end try
                end repeat
                return windowList
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse AppleScript output (format: "app, title, pid, frontmost")
            windows = []
            output = result.stdout.strip()
            if output:
                # Split by newlines and parse each window
                for line in output.split(', '):
                    parts = line.strip().split(', ')
                    if len(parts) >= 3:
                        windows.append({
                            'app': parts[0],
                            'title': parts[1],
                            'pid': int(parts[2]) if parts[2].isdigit() else 0,
                            'active': parts[3] == 'true' if len(parts) > 3 else False
                        })

            return windows
        except (subprocess.CalledProcessError, Exception) as e:
            print(f"Error listing windows on macOS: {e}")
            return []

    def _get_active_window_macos(self) -> Optional[Dict]:
        """Get active window on macOS using AppleScript."""
        try:
            script = '''
            tell application "System Events"
                set frontApp to name of first process whose frontmost is true
                set frontWindow to name of front window of process frontApp
                set frontPID to unix id of process frontApp
                return {frontApp, frontWindow, frontPID}
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )

            output = result.stdout.strip()
            parts = output.split(', ')
            if len(parts) >= 3:
                return {
                    'app': parts[0],
                    'title': parts[1],
                    'pid': int(parts[2]) if parts[2].isdigit() else 0,
                    'active': True
                }
            return None
        except (subprocess.CalledProcessError, Exception) as e:
            print(f"Error getting active window on macOS: {e}")
            return None

    def _focus_window_macos(self, title: str) -> bool:
        """Focus window on macOS using AppleScript."""
        try:
            # AppleScript to find and activate window by partial title match
            script = f'''
            tell application "System Events"
                repeat with theProcess in (every process whose visible is true)
                    try
                        set processName to name of theProcess
                        repeat with theWindow in (every window of theProcess)
                            set windowTitle to name of theWindow
                            if windowTitle contains "{title}" then
                                set frontmost of theProcess to true
                                perform action "AXRaise" of theWindow
                                return true
                            end if
                        end repeat
                    end try
                end repeat
                return false
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout.strip().lower() == 'true'
        except (subprocess.CalledProcessError, Exception) as e:
            print(f"Error focusing window on macOS: {e}")
            return False

    # Windows implementations (using pyautogui)
    def _list_windows_windows(self) -> List[Dict]:
        """List windows on Windows using pyautogui."""
        try:
            import pyautogui
            windows = []
            for w in pyautogui.getAllWindows():
                try:
                    windows.append({
                        'title': w.title,
                        'app': w.title.split(' - ')[-1] if ' - ' in w.title else 'Unknown',
                        'pid': 0,  # pyautogui doesn't provide PID
                        'active': w.isActive
                    })
                except:
                    continue
            return windows
        except ImportError:
            print("pyautogui not available on Windows")
            return []

    def _get_active_window_windows(self) -> Optional[Dict]:
        """Get active window on Windows using pyautogui."""
        try:
            import pyautogui
            active = pyautogui.getActiveWindow()
            if active:
                return {
                    'title': active.title,
                    'app': active.title.split(' - ')[-1] if ' - ' in active.title else 'Unknown',
                    'pid': 0,
                    'active': True
                }
            return None
        except ImportError:
            print("pyautogui not available on Windows")
            return None

    def _focus_window_windows(self, title: str) -> bool:
        """Focus window on Windows using pyautogui."""
        try:
            import pyautogui
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                windows[0].activate()
                return True
            return False
        except ImportError:
            print("pyautogui not available on Windows")
            return False

    # Linux implementations
    def _list_windows_linux(self) -> List[Dict]:
        """List windows on Linux using wmctrl."""
        try:
            result = subprocess.run(
                ['wmctrl', '-lp'],
                capture_output=True,
                text=True,
                check=True
            )

            windows = []
            for line in result.stdout.strip().split('\n'):
                parts = line.split(None, 4)
                if len(parts) >= 5:
                    windows.append({
                        'title': parts[4],
                        'app': parts[4].split(' - ')[-1] if ' - ' in parts[4] else 'Unknown',
                        'pid': int(parts[2]) if parts[2].isdigit() else 0,
                        'active': False  # wmctrl doesn't easily provide active status
                    })
            return windows
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error listing windows on Linux: {e}. Install wmctrl: sudo apt-get install wmctrl")
            return []

    def _get_active_window_linux(self) -> Optional[Dict]:
        """Get active window on Linux using xdotool."""
        try:
            # Get active window ID
            result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True,
                check=True
            )
            window_id = result.stdout.strip()

            # Get window name
            result = subprocess.run(
                ['xdotool', 'getwindowname', window_id],
                capture_output=True,
                text=True,
                check=True
            )
            title = result.stdout.strip()

            # Get window PID
            result = subprocess.run(
                ['xdotool', 'getwindowpid', window_id],
                capture_output=True,
                text=True,
                check=True
            )
            pid = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0

            return {
                'title': title,
                'app': title.split(' - ')[-1] if ' - ' in title else 'Unknown',
                'pid': pid,
                'active': True
            }
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error getting active window on Linux: {e}. Install xdotool: sudo apt-get install xdotool")
            return None

    def _focus_window_linux(self, title: str) -> bool:
        """Focus window on Linux using wmctrl."""
        try:
            # Use wmctrl to activate window by partial title match
            result = subprocess.run(
                ['wmctrl', '-a', title],
                capture_output=True,
                text=True,
                check=False  # Don't raise on non-zero exit
            )
            return result.returncode == 0
        except FileNotFoundError:
            print("wmctrl not found. Install: sudo apt-get install wmctrl")
            return False


# Global instance
_window_manager = None

def get_window_manager() -> WindowManager:
    """Get singleton WindowManager instance."""
    global _window_manager
    if _window_manager is None:
        _window_manager = WindowManager()
    return _window_manager
