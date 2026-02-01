"""macOS LaunchAgent management for whisper-dictation."""

import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

AGENT_LABEL = "com.whisper-hotkey.service"
PLIST_FILENAME = f"{AGENT_LABEL}.plist"


def get_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / PLIST_FILENAME


def get_log_dir() -> Path:
    log_dir = Path.home() / "Library" / "Logs" / "whisper-hotkey"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def find_binary() -> str:
    """Find the whisper-dictation binary."""
    # uv tool install location
    uv_path = Path.home() / ".local" / "bin" / "whisper-hotkey"
    if uv_path.exists():
        return str(uv_path)

    which = shutil.which("whisper-hotkey")
    if which:
        return which

    return sys.executable


def build_plist() -> dict:
    binary = find_binary()
    log_dir = get_log_dir()

    if binary == sys.executable:
        program_args = [binary, "-m", "whisper_dictation"]
    else:
        program_args = [binary]

    return {
        "Label": AGENT_LABEL,
        "ProgramArguments": program_args,
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(log_dir / "stdout.log"),
        "StandardErrorPath": str(log_dir / "stderr.log"),
        "EnvironmentVariables": {
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
            "HOME": str(Path.home()),
        },
        "ProcessType": "Interactive",
        "ThrottleInterval": 5,
    }


def install_agent():
    """Write the LaunchAgent plist and load it."""
    plist_path = get_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    # Unload existing if present
    if plist_path.exists():
        subprocess.run(
            ["launchctl", "unload", str(plist_path)],
            capture_output=True,
        )

    plist_data = build_plist()
    with open(plist_path, "wb") as f:
        plistlib.dump(plist_data, f)

    subprocess.run(["launchctl", "load", str(plist_path)], check=True)

    print(f"  LaunchAgent installed: {plist_path}")
    print(f"  Logs: {get_log_dir()}")
    print(f"  Binary: {' '.join(plist_data['ProgramArguments'])}")
    print()
    print("  The service is now running and will auto-start on login.")
    print("  Use 'whisper-hotkey uninstall' to remove.")
    print()


def uninstall_agent():
    """Unload and remove the LaunchAgent plist."""
    plist_path = get_plist_path()
    if not plist_path.exists():
        print("LaunchAgent not found. Nothing to uninstall.")
        return

    subprocess.run(
        ["launchctl", "unload", str(plist_path)],
        capture_output=True,
    )
    plist_path.unlink()
    print(f"LaunchAgent removed: {plist_path}")


def check_status():
    """Check if the service is currently loaded."""
    result = subprocess.run(
        ["launchctl", "list", AGENT_LABEL],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"Service is running.\n{result.stdout}")
    else:
        print("Service is not running.")
