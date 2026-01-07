import os
import logging
import argparse
import shlex
import subprocess
from flask import Flask, request, jsonify, send_file
import threading
import traceback
import pyautogui
from PIL import Image
from io import BytesIO


def execute_anything(data):
    """Execute any command received in the JSON request.
    WARNING: This function executes commands without any safety checks."""
    # The 'command' key in the JSON request should contain the command to be executed.
    shell = data.get('shell', False)
    command = data.get('command', "" if shell else [])

    if isinstance(command, str) and not shell:
        command = shlex.split(command)

    # Expand user directory
    for i, arg in enumerate(command):
        if arg.startswith("~/"):
            command[i] = os.path.expanduser(arg)

    # Execute the command without any safety checks.
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, text=True, timeout=120)
        return jsonify({
            'status': 'success',
            'output': result.stdout,
            'error': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        logger.error("\n" + traceback.format_exc() + "\n")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    

def execute(data):
    """Action space aware implementation. Should not use arbitrary code execution."""
    return jsonify({
        'status': 'error',
        'message': 'Not implemented. Please add your implementation to omnitool/omnibox/vm/win11setup/setupscripts/server/main.py.'
    }), 500


execute_impl = execute   # switch to execute_anything to allow any command. Please use with caution only for testing purposes.


parser = argparse.ArgumentParser()
parser.add_argument("--log_file", help="log file path", type=str,
                    default=os.path.join(os.path.dirname(__file__), "server.log"))
parser.add_argument("--port", help="port", type=int, default=5000)
args = parser.parse_args()

logging.basicConfig(filename=args.log_file,level=logging.DEBUG, filemode='w' )
logger = logging.getLogger('werkzeug')

app = Flask(__name__)

computer_control_lock = threading.Lock()

@app.route('/probe', methods=['GET'])
def probe_endpoint():
    return jsonify({"status": "Probe successful", "message": "Service is operational"}), 200

@app.route('/execute', methods=['POST'])
def execute_command():
    # Only execute one command at a time
    with computer_control_lock:
        data = request.json
        return execute_impl(data)

@app.route('/screenshot', methods=['GET'])
def capture_screen_with_cursor():
    cursor_path = os.path.join(os.path.dirname(__file__), "cursor.png")
    screenshot = pyautogui.screenshot()
    cursor_x, cursor_y = pyautogui.position()
    cursor = Image.open(cursor_path)
    # make the cursor smaller
    cursor = cursor.resize((int(cursor.width / 1.5), int(cursor.height / 1.5)))
    screenshot.paste(cursor, (cursor_x, cursor_y), cursor)

    # Convert PIL Image to bytes and send
    img_io = BytesIO()
    screenshot.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/windows/list', methods=['GET'])
def list_windows():
    """List all open windows with their titles and positions."""
    try:
        import pyautogui
        windows = pyautogui.getAllWindows()
        window_list = []
        for w in windows:
            try:
                window_list.append({
                    'title': w.title,
                    'left': w.left,
                    'top': w.top,
                    'width': w.width,
                    'height': w.height,
                    'active': w.isActive
                })
            except Exception as e:
                # Skip windows that can't be accessed
                logger.debug(f"Skipping window due to error: {e}")
                continue
        return jsonify({'windows': window_list})
    except Exception as e:
        logger.error("\n" + traceback.format_exc() + "\n")
        return jsonify({'error': 'Window management not supported', 'message': str(e)}), 501

@app.route('/windows/active', methods=['GET'])
def get_active_window():
    """Get the currently active (focused) window."""
    try:
        import pyautogui
        active_window = pyautogui.getActiveWindow()
        if active_window:
            return jsonify({
                'title': active_window.title,
                'left': active_window.left,
                'top': active_window.top,
                'width': active_window.width,
                'height': active_window.height
            })
        else:
            return jsonify({'error': 'No active window found'}), 404
    except Exception as e:
        logger.error("\n" + traceback.format_exc() + "\n")
        return jsonify({'error': 'Could not get active window', 'message': str(e)}), 500

@app.route('/windows/focus', methods=['POST'])
def focus_window():
    """Focus (activate) a window by partial title match."""
    try:
        import pyautogui
        data = request.json
        title_query = data.get('title', '')

        if not title_query:
            return jsonify({'error': 'Title parameter is required'}), 400

        # Try to find window by partial title match
        windows = pyautogui.getWindowsWithTitle(title_query)

        if windows:
            # Focus the first matching window
            windows[0].activate()
            return jsonify({
                'status': 'success',
                'message': f'Focused window: {windows[0].title}',
                'title': windows[0].title
            })
        else:
            # If no exact match, try case-insensitive partial match
            all_windows = pyautogui.getAllWindows()
            for w in all_windows:
                if title_query.lower() in w.title.lower():
                    w.activate()
                    return jsonify({
                        'status': 'success',
                        'message': f'Focused window: {w.title}',
                        'title': w.title
                    })

            return jsonify({'error': f'No window found matching: {title_query}'}), 404
    except Exception as e:
        logger.error("\n" + traceback.format_exc() + "\n")
        return jsonify({'error': 'Could not focus window', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host="10.0.2.15", port=args.port)