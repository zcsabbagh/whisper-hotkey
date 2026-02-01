"""macOS permission requests for microphone, input monitoring, and accessibility."""

import subprocess
import sys
import os
from pathlib import Path


def get_python_path():
    """Return the resolved Python interpreter path."""
    return os.path.realpath(sys.executable)


def open_system_settings(pane):
    """Open a specific Privacy & Security pane in System Settings."""
    subprocess.run(
        ["open", f"x-apple.systempreferences:com.apple.preference.security?{pane}"],
        capture_output=True,
    )


def reveal_in_finder(path):
    """Reveal a file in Finder so the user can drag or select it."""
    subprocess.run(["open", "-R", path], capture_output=True)


def request_microphone_access():
    """Trigger the macOS microphone permission dialog."""
    print("  [1/3] Microphone")
    print("  Requesting microphone access...")
    print("  If prompted, click 'Allow' in the macOS dialog.\n")
    try:
        import sounddevice as sd
        sd.rec(int(0.1 * 16000), samplerate=16000, channels=1, dtype="float32")
        sd.wait()
        print("  ✓ Microphone access granted.\n")
    except Exception as e:
        print(f"  ✗ Microphone access may have been denied: {e}")
        print("  Go to System Settings > Privacy & Security > Microphone")
        print(f"  and enable access for: {get_python_path()}\n")


def request_input_monitoring():
    """Guide the user to grant Input Monitoring permission.

    pynput requires Input Monitoring to detect global keyboard events.
    macOS only shows .app bundles in the Input Monitoring list by default,
    so we reveal the Python binary in Finder and open the settings pane
    to let the user add it manually.
    """
    python_path = get_python_path()

    print("  [2/3] Input Monitoring")
    print("  This is required for the double-tap Control hotkey to work.")
    print()
    print("  Opening System Settings > Input Monitoring and revealing")
    print(f"  the Python binary in Finder so you can add it.\n")
    print(f"    Python binary: {python_path}\n")
    print("  Steps:")
    print("    1. In the System Settings window that opens, click the '+' button")
    print("    2. In the file dialog, press Cmd+Shift+G and paste this path:")
    print(f"       {Path(python_path).parent}")
    print(f"    3. Select '{Path(python_path).name}' and click Open")
    print("    4. Make sure the toggle is ON\n")

    open_system_settings("Privacy_ListenEvent")
    reveal_in_finder(python_path)

    input("  Press Enter after granting Input Monitoring access...")
    print()


def request_accessibility_access():
    """Trigger the macOS accessibility permission prompt."""
    python_path = get_python_path()

    print("  [3/3] Accessibility")
    print("  This is needed to paste transcribed text via Cmd+V.\n")

    subprocess.run(
        ["osascript", "-e",
         'tell application "System Events" to keystroke ""'],
        capture_output=True,
    )

    terminal = os.environ.get("TERM_PROGRAM", "Terminal")
    print("  If pasting doesn't work after install, add BOTH of these")
    print("  in System Settings > Privacy & Security > Accessibility:\n")
    print(f"    1. Your terminal: {terminal}")
    print(f"    2. Python: {python_path}\n")


def request_permissions():
    """Run all permission requests."""
    python_path = get_python_path()

    print("=" * 60)
    print("  whisper-dictation: Permission Setup")
    print("=" * 60)
    print()
    print(f"  Python interpreter: {python_path}")
    print()
    print("  This tool requires three macOS permissions:")
    print("    1. Microphone — to record audio")
    print("    2. Input Monitoring — to detect the hotkey")
    print("    3. Accessibility — to paste transcribed text")
    print()

    request_microphone_access()
    request_input_monitoring()
    request_accessibility_access()

    print("=" * 60)
    print("  Setup complete! After granting all permissions,")
    print("  restart your terminal for changes to take effect.")
    print("=" * 60)
    print()
