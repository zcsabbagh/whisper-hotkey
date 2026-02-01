"""CLI entry point for whisper-dictation."""

import argparse
import sys

from whisper_dictation.config import MODELS, DEFAULT_MODEL, get_model_id, set_model_id


def prompt_model_choice():
    """Interactively ask the user which model to use."""
    print("Select a Whisper model:\n")
    options = list(MODELS.items())
    for i, (model_id, info) in enumerate(options, 1):
        print(f"  {i}) {info['label']}")
        print(f"     {info['description']}\n")

    while True:
        choice = input(f"Enter choice [1]: ").strip()
        if choice == "" or choice == "1":
            return options[0][0]
        if choice == "2":
            return options[1][0]
        print("  Please enter 1 or 2.")


def do_install():
    """Interactive install: model choice, permissions, LaunchAgent."""
    from whisper_dictation.permissions import request_permissions
    from whisper_dictation.launchagent import install_agent

    print()
    print("=" * 60)
    print("  whisper-dictation: Install")
    print("=" * 60)
    print()

    # 1. Model choice
    model_id = prompt_model_choice()
    set_model_id(model_id)
    print(f"\n  Selected model: {model_id}\n")

    # 2. Pre-download model
    print("  Downloading model (this may take a moment)...")
    from faster_whisper import WhisperModel
    WhisperModel(model_id, device="cpu", compute_type="int8")
    print("  Model ready.\n")

    # 3. Permissions
    request_permissions()

    # 4. LaunchAgent
    print("Installing LaunchAgent...\n")
    install_agent()

    print("=" * 60)
    print("  Done! Double-tap Control to dictate.")
    print()
    print("  If the hotkey doesn't work, make sure these are all granted")
    print("  in System Settings > Privacy & Security:")
    print("    - Microphone")
    print("    - Input Monitoring")
    print("    - Accessibility")
    print()
    print("  Then restart your terminal or log out and back in.")
    print("=" * 60)
    print()


def do_uninstall():
    from whisper_dictation.launchagent import uninstall_agent
    uninstall_agent()


def do_status():
    from whisper_dictation.launchagent import check_status
    print(f"Configured model: {get_model_id()}")
    check_status()


def do_run():
    from whisper_dictation.service import run
    run()


def main():
    parser = argparse.ArgumentParser(
        prog="whisper-hotkey",
        description="Whisper dictation service for macOS. "
                    "Double-tap Control to start/stop recording.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help="Run the dictation service (default)")
    sub.add_parser("install", help="Set up model, permissions, and auto-start")
    sub.add_parser("uninstall", help="Remove the auto-start LaunchAgent")
    sub.add_parser("status", help="Check if the service is running")

    args = parser.parse_args()

    if args.command == "install":
        do_install()
    elif args.command == "uninstall":
        do_uninstall()
    elif args.command == "status":
        do_status()
    else:
        do_run()
