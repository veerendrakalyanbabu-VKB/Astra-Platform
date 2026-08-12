"""Optional ElevenLabs TTS — production voice with pyttsx3 fallback."""

import os
from typing import Optional


class ElevenLabsTTS:
    """Speaks text via ElevenLabs API when configured."""

    def __init__(self):
        self.api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        self.voice = os.environ.get("ELEVENLABS_VOICE", "Adam").strip() or "Adam"
        self.model = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
        self.enabled = bool(self.api_key)

    def speak(self, text: str) -> bool:
        if not self.enabled or not text.strip():
            return False

        try:
            from elevenlabs.client import ElevenLabs
            from elevenlabs import play

            client = ElevenLabs(api_key=self.api_key)
            audio = client.generate(text=text.strip(), voice=self.voice, model=self.model)
            play(audio)
            return True
        except ImportError:
            return self._speak_http(text)
        except Exception:
            return False

    def _speak_http(self, text: str) -> bool:
        """Fallback when SDK missing — raw REST + system player."""
        import json
        import tempfile
        import urllib.error
        import urllib.request
        import subprocess
        import sys

        voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
        if not voice_id:
            voice_id = self._resolve_voice_id()
        if not voice_id:
            return False

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        payload = {
            "text": text.strip(),
            "model_id": self.model,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                audio_bytes = response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            return False

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(audio_bytes)
            path = tmp.name

        try:
            if sys.platform == "win32":
                import winsound
                winsound.PlaySound(path, winsound.SND_FILENAME)
            else:
                subprocess.run(["afplay", path], check=False)
            return True
        except Exception:
            return False
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def _resolve_voice_id(self) -> Optional[str]:
        import json
        import urllib.error
        import urllib.request

        request = urllib.request.Request(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": self.api_key},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                body = json.loads(response.read().decode("utf-8"))
            for voice in body.get("voices", []):
                if voice.get("name", "").lower() == self.voice.lower():
                    return voice.get("voice_id")
            voices = body.get("voices") or []
            return voices[0]["voice_id"] if voices else None
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError):
            return None
