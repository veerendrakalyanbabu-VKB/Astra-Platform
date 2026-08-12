#!/usr/bin/env python3
"""
Astra Voice Quick Start — hear your assistant say your name in under 60 minutes.
Brain: Claude · Voice: ElevenLabs (with offline fallback)

Run: python astra_hello.py
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from astra.core.config.config_manager import ConfigManager
from astra.core.llm.llm_client import LLMClient
from astra.core.voice.elevenlabs_tts import ElevenLabsTTS
from astra.core.voice.voice_settings import VoiceSettingsStore


def main() -> int:
    ConfigManager(PROJECT_ROOT).load()
    settings = VoiceSettingsStore(PROJECT_ROOT)
    name = settings.assistant_name
    your_name = os.environ.get("ASTRA_USER_NAME", "Commander").strip() or "Commander"

    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        print("Missing ANTHROPIC_API_KEY in .env")
        print("Get one at https://console.anthropic.com")
        return 1

    os.environ.setdefault("ASTRA_LLM_PROVIDER", "anthropic")
    client = LLMClient()
    if not client.enabled:
        print("Claude client could not start — check your API key.")
        return 1

    prompt = f"Say a short, direct greeting to {your_name}. You are {name}, their personal Astra command OS."
    text = client.chat(
        f"You are {name} — a precise, warm Astra-class assistant.",
        prompt,
        max_tokens=80,
        temperature=0.6,
    )

    if not text:
        print("Claude did not return a response.")
        return 1

    print(f"{name.upper()}: {text}")

    if os.environ.get("ELEVENLABS_API_KEY", "").strip():
        voice = ElevenLabsTTS()
        if voice.speak(text):
            print("[voice] ElevenLabs OK")
        else:
            _pyttsx3_fallback(text)
    else:
        print("[voice] Add ELEVENLABS_API_KEY for natural voice — using offline TTS")
        _pyttsx3_fallback(text)

    print()
    print("Next: python main.py --desktop  or  python main.py --wake")
    return 0


def _pyttsx3_fallback(text: str) -> None:
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        print(f"[voice] Offline TTS unavailable: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
