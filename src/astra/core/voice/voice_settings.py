"""User-configurable voice identity and wake phrases (Alexa-style)."""

import json
import re
from pathlib import Path
from typing import Dict, List


WAKE_TEMPLATES = {
    "launch": ["wake up {name}", "hey {name}"],
    "chat": ["hello {name}", "{name} listen"],
    "sleep": ["goodnight {name}", "sleep {name}"],
}


class VoiceSettingsStore:
    """Persists assistant name and wake phrases in data/voice_settings.json."""

    def __init__(self, project_root: Path):
        self.path = Path(project_root) / "data" / "voice_settings.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as file:
                    return {**self.defaults(), **json.load(file)}
            except (json.JSONDecodeError, OSError):
                pass
        data = self.defaults()
        self._save(data)
        return data

    def defaults(self) -> dict:
        return {
            "assistant_name": "Astra",
            "wake_enabled": True,
            "voice_style": "female",
            "wake_phrases": self._build_phrases("Astra"),
            "extra_phrases": [],
        }

    def _build_phrases(self, name: str) -> Dict[str, List[str]]:
        clean = name.strip() or "Astra"
        lowered = clean.lower()
        phrases = {}
        for mode, templates in WAKE_TEMPLATES.items():
            phrases[mode] = [t.format(name=lowered) for t in templates]
        return phrases

    def _save(self, data: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    @property
    def assistant_name(self) -> str:
        return self._data.get("assistant_name", "Astra")

    @property
    def wake_enabled(self) -> bool:
        return bool(self._data.get("wake_enabled", True))

    def all_wake_phrases(self) -> List[str]:
        phrases = []
        for group in self._data.get("wake_phrases", {}).values():
            phrases.extend(group)
        phrases.extend(self._data.get("extra_phrases", []))
        return [p.lower().strip() for p in phrases if p.strip()]

    def launch_phrases(self) -> List[str]:
        return [p.lower() for p in self._data.get("wake_phrases", {}).get("launch", [])]

    def chat_phrases(self) -> List[str]:
        return [p.lower() for p in self._data.get("wake_phrases", {}).get("chat", [])]

    def sleep_phrases(self) -> List[str]:
        return [p.lower() for p in self._data.get("wake_phrases", {}).get("sleep", [])]

    def set_assistant_name(self, name: str) -> dict:
        clean = re.sub(r"[^\w\s\-]", "", (name or "").strip())[:32]
        if not clean:
            return {"success": False, "message": "Assistant name cannot be empty."}

        self._data["assistant_name"] = clean
        self._data["wake_phrases"] = self._build_phrases(clean)
        self._save(self._data)
        return {
            "success": True,
            "message": (
                f"Assistant renamed to {clean}. Wake phrases updated:\n"
                f"  Launch: {', '.join(self.launch_phrases())}\n"
                f"  Chat: {', '.join(self.chat_phrases())}\n"
                f"  Sleep: {', '.join(self.sleep_phrases())}"
            ),
        }

    def add_wake_phrase(self, phrase: str, mode: str = "chat") -> dict:
        phrase = phrase.lower().strip()
        if not phrase or len(phrase) < 3:
            return {"success": False, "message": "Wake phrase must be at least 3 characters."}

        if mode not in WAKE_TEMPLATES:
            mode = "chat"

        group = self._data.setdefault("wake_phrases", self._build_phrases(self.assistant_name))
        group.setdefault(mode, [])
        if phrase not in group[mode]:
            group[mode].append(phrase)
        self._save(self._data)
        return {"success": True, "message": f"Wake phrase added ({mode}): \"{phrase}\""}

    def set_wake_enabled(self, enabled: bool) -> dict:
        self._data["wake_enabled"] = enabled
        self._save(self._data)
        state = "ON" if enabled else "OFF"
        return {"success": True, "message": f"Wake-word listening {state}."}

    def snapshot(self) -> dict:
        return {
            "assistant_name": self.assistant_name,
            "wake_enabled": self.wake_enabled,
            "voice_style": self._data.get("voice_style", "female"),
            "wake_phrases": self._data.get("wake_phrases", {}),
            "extra_phrases": self._data.get("extra_phrases", []),
            "all_phrases": self.all_wake_phrases(),
            "launch_phrases": self.launch_phrases(),
            "chat_phrases": self.chat_phrases(),
            "sleep_phrases": self.sleep_phrases(),
        }

    def format_status(self) -> str:
        snap = self.snapshot()
        lines = [
            f"Assistant name: {snap['assistant_name']}",
            f"Wake listening: {'ON' if snap['wake_enabled'] else 'OFF'}",
            "",
            "Launch (full activate):",
            "  " + " | ".join(snap["launch_phrases"]),
            "Chat (command mode):",
            "  " + " | ".join(snap["chat_phrases"]),
            "Sleep:",
            "  " + " | ".join(snap["sleep_phrases"]),
            "",
            "Change name: set assistant name to Nova",
            "Add phrase: set wake phrase to hey nova",
            "Toggle: turn wake word on | turn wake word off",
        ]
        return "\n".join(lines)

    def match_wake(self, text: str) -> str | None:
        """Return launch | chat | sleep if text contains a wake phrase."""
        if not self.wake_enabled:
            return None

        lowered = text.lower().strip()
        for phrase in self.sleep_phrases():
            if phrase in lowered:
                return "sleep"
        for phrase in self.launch_phrases():
            if phrase in lowered:
                return "launch"
        for phrase in self.chat_phrases():
            if phrase in lowered:
                return "chat"
        for phrase in self._data.get("extra_phrases", []):
            if phrase.lower() in lowered:
                return "chat"
        return None

    def strip_wake_prefix(self, text: str) -> str:
        lowered = text.lower()
        for phrase in sorted(self.all_wake_phrases(), key=len, reverse=True):
            if phrase in lowered:
                idx = lowered.find(phrase)
                return text[idx + len(phrase):].strip(" ,.!")
        return text.strip()
