#!/usr/bin/env python3
"""
Astra Voice Quick Start — hear your assistant say your name in under 60 minutes.
Brain: Claude · Voice: ElevenLabs (with offline fallback)

Run: python Astra_hello.py
"""

import os
import sys
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from astra.core.config.config_manager import ConfigManager
from astra.core.llm.llm_client import LLMClient, resolve_llm_config
from astra.core.voice.elevenlabs_tts import ElevenLabsTTS
from astra.core.voice.voice_settings import VoiceSettingsStore

OFFLINE_GREETINGS = [
    "Astra online. Ready for command.",
    "Command channel open. What do you need?",
    "Systems nominal. Astra standing by.",
]


def _offline_greeting(name: str, your_name: str) -> str:
    import random

    base = random.choice(OFFLINE_GREETINGS)
    return f"Hello {your_name}. {base}"


def _llm_greeting(client: LLMClient, name: str, your_name: str) -> tuple:
    """Return (text, error_hint)."""
    prompt = f"Say a short, direct greeting to {your_name}. You are {name}, their personal Astra command OS."
    system = f"You are {name} — a precise, warm Astra-class assistant."
    try:
        text = client.chat(system, prompt, temperature=0.6, max_tokens=80, timeout=20)
        if not text:
            return None, "Empty response from LLM."
        return text, None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:200]
        return None, f"API error {exc.code}: {detail}"
    except Exception as exc:
        return None, str(exc)


def main() -> int:
    ConfigManager(PROJECT_ROOT).load()
    settings = VoiceSettingsStore(PROJECT_ROOT)
    name = settings.assistant_name
    your_name = os.environ.get("ASTRA_USER_NAME", "Commander").strip() or "Commander"
    llm_cfg = resolve_llm_config()

    client = LLMClient()
    text = None

    if client.enabled:
        text, err = _llm_greeting(client, name, your_name)
        if err:
            print(f"LLM call failed: {err}")
            print("Using offline greeting instead.")
            text = _offline_greeting(name, your_name)
    else:
        print("No LLM API key in .env — using offline greeting.")
        print("Add GROQ_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY to .env.")
        print("  Groq:      https://console.groq.com/keys")
        print("  Anthropic: https://console.anthropic.com")
        print("  OpenAI:    https://platform.openai.com/api-keys")
        text = _offline_greeting(name, your_name)

    if not text:
        text = _offline_greeting(name, your_name)

    provider_label = llm_cfg.get("llm_label") or "Offline"
    print(f"[brain] {provider_label}")
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
