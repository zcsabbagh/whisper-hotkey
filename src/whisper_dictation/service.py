"""Whisper dictation service — the main runtime loop."""

import sys
import os
import threading
import subprocess
import tempfile
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from pynput import keyboard

from whisper_dictation.config import get_model_id

# ── Config ──────────────────────────────────────────────────────────────
SAMPLE_RATE = 16000
DOUBLE_TAP_INTERVAL = 0.35  # seconds — max gap between two Control taps
SOUND_START = "/System/Library/Sounds/Pop.aiff"
SOUND_STOP = "/System/Library/Sounds/Pop.aiff"
# ────────────────────────────────────────────────────────────────────────

recording = False
audio_frames = []
stream = None
lock = threading.Lock()


def play_sound(sound_path):
    """Play a macOS system sound without blocking using NSSound."""
    try:
        from AppKit import NSSound
        sound = NSSound.alloc().initWithContentsOfFile_byReference_(sound_path, True)
        if sound:
            sound.play()
    except Exception:
        # Fallback to afplay
        subprocess.Popen(["afplay", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def notify(title, message):
    """Send a macOS notification."""
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}"'
    ], capture_output=True)


def paste_text(text):
    """Copy text to clipboard and simulate Cmd+V paste."""
    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    process.communicate(text.encode("utf-8"))

    time.sleep(0.05)
    subprocess.run([
        "osascript", "-e",
        'tell application "System Events" to keystroke "v" using command down'
    ], capture_output=True)


def audio_callback(indata, frames, time_info, status):
    """Called for each audio block during recording."""
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    audio_frames.append(indata.copy())


def start_recording():
    """Start recording audio from the microphone."""
    global recording, audio_frames, stream
    audio_frames = []
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=audio_callback,
    )
    stream.start()
    recording = True
    play_sound(SOUND_START)
    print("Recording... (double-tap Control to stop)")
    notify("Whisper Dictation", "Recording started...")


def stop_recording_and_transcribe(model):
    """Stop recording, transcribe, and paste the result."""
    global recording, stream
    recording = False
    play_sound(SOUND_STOP)
    if stream is not None:
        stream.stop()
        stream.close()
        stream = None

    if not audio_frames:
        print("No audio recorded.")
        notify("Whisper Dictation", "No audio recorded.")
        return

    print("Transcribing...")
    notify("Whisper Dictation", "Transcribing...")

    audio_data = np.concatenate(audio_frames, axis=0).flatten()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
        sf.write(tmp_path, audio_data, SAMPLE_RATE)

    try:
        segments, _info = model.transcribe(
            tmp_path,
            beam_size=1,
            language="en",
            vad_filter=False,
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
    finally:
        os.unlink(tmp_path)

    if text:
        print(f"Transcription: {text}")
        paste_text(text)
        notify("Whisper Dictation", f"Pasted: {text[:80]}")
    else:
        print("No speech detected.")
        notify("Whisper Dictation", "No speech detected.")


def run():
    """Main entry point for the dictation service."""
    model_id = get_model_id()
    print(f"Loading faster-whisper model ({model_id}, CTranslate2 int8)...")

    model = WhisperModel(model_id, device="cpu", compute_type="int8")

    print("Model loaded!")
    print("Double-tap Control to start/stop recording.")
    print("Press Ctrl+C to quit.\n")

    def on_toggle():
        with lock:
            if recording:
                stop_recording_and_transcribe(model)
            else:
                start_recording()

    last_ctrl_release = 0.0
    other_key_pressed = False

    def on_press(key):
        nonlocal other_key_pressed
        ctrl_keys = (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)
        if key not in ctrl_keys:
            other_key_pressed = True

    def on_release(key):
        nonlocal last_ctrl_release, other_key_pressed
        ctrl_keys = (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)
        if key in ctrl_keys:
            now = time.monotonic()
            if not other_key_pressed and (now - last_ctrl_release) < DOUBLE_TAP_INTERVAL:
                last_ctrl_release = 0.0
                threading.Thread(target=on_toggle, daemon=True).start()
            else:
                last_ctrl_release = now
            other_key_pressed = False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nExiting.")
