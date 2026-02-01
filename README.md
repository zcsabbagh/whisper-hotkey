# whisper-hotkey

Double-tap Control to dictate with Whisper on macOS. Transcribes your speech and pastes it into whatever text field is focused.

Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2) with int8 quantization for fast local inference. No cloud APIs, everything runs on your machine.

## Install

```bash
uvx whisper-hotkey install
```

This will:
1. Ask you to choose a model (tiny.en for speed, or distil-large-v3 for accuracy)
2. Download the model
3. Request microphone and accessibility permissions
4. Install a LaunchAgent so it starts automatically on login

## Usage

After install, just **double-tap the Control key** to start recording. Double-tap again to stop — your speech is transcribed and pasted into the active text field.

That's it. It works across all apps, survives reboots, and runs in the background.

## Commands

```bash
whisper-hotkey install    # Interactive setup (model, permissions, auto-start)
whisper-hotkey uninstall  # Remove auto-start
whisper-hotkey status     # Check if the service is running
whisper-hotkey             # Run the service directly (not needed after install)
```

## Requirements

- macOS (Apple Silicon or Intel)
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny.en (default) | ~75MB | Fastest | Good for clear English |
| distil-large-v3 | ~1.5GB | Slower | Better with accents/noise |

## Permissions

The app needs two macOS permissions:
- **Microphone** — to record your voice
- **Accessibility** — to detect the keyboard shortcut and paste text

The `install` command will prompt for these. If the shortcut doesn't work, check System Settings > Privacy & Security and make sure both your terminal and Python have Accessibility access.

## Logs

```bash
tail -f ~/Library/Logs/whisper-hotkey/stdout.log
tail -f ~/Library/Logs/whisper-hotkey/stderr.log
```

## License

MIT
