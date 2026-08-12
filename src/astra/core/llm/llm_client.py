"""Unified LLM client — OpenAI and Anthropic Claude with local-first privacy."""

import json
import os
import re
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple


OPENAI_DEFAULT = "gpt-4o-mini"
ANTHROPIC_DEFAULT = "claude-3-5-haiku-20241022"


def resolve_llm_config() -> Dict:
    """Pick provider from env: anthropic | openai | auto (prefers Claude when both set)."""
    provider = (os.environ.get("ASTRA_LLM_PROVIDER") or "auto").strip().lower()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()

    if provider == "anthropic":
        active = "anthropic" if anthropic_key else None
    elif provider == "openai":
        active = "openai" if openai_key else None
    else:
        if anthropic_key:
            active = "anthropic"
        elif openai_key:
            active = "openai"
        else:
            active = None

    model = os.environ.get("ASTRA_LLM_MODEL", "").strip()
    if not model:
        model = ANTHROPIC_DEFAULT if active == "anthropic" else OPENAI_DEFAULT

    label = "Standby"
    if active == "anthropic":
        label = "Claude Active"
    elif active == "openai":
        label = "GPT Active"

    return {
        "provider": active,
        "model": model,
        "openai_key_set": bool(openai_key),
        "anthropic_key_set": bool(anthropic_key),
        "llm_active": active is not None,
        "llm_label": label,
    }


class LLMClient:
    """Provider-agnostic chat completion with graceful offline fallback."""

    def __init__(self, enabled: bool = None):
        cfg = resolve_llm_config()
        self.provider = cfg["provider"]
        self.model = cfg["model"]
        self.openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()

        if enabled is None:
            enabled = cfg["llm_active"]
        self.enabled = enabled and self.provider is not None

    def chat_turns(
        self,
        system: str,
        turns: List[Dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 300,
        timeout: int = 12,
    ) -> Optional[str]:
        """Multi-turn chat — rolling session memory like JARVIS."""
        if not self.enabled or not turns:
            return None

        messages = [{"role": "system", "content": system.strip()}]
        for turn in turns[-20:]:
            role = turn.get("role", "user")
            content = (turn.get("content") or "").strip()
            if not content:
                continue
            if role not in ("user", "assistant"):
                role = "user"
            messages.append({"role": role, "content": content})

        if len(messages) < 2:
            return None

        try:
            if self.provider == "anthropic":
                return self._anthropic(messages, temperature, max_tokens, timeout)
            return self._openai(messages, temperature, max_tokens, False, timeout)
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            KeyError,
            json.JSONDecodeError,
            TimeoutError,
            ValueError,
        ):
            return None

    def chat(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 300,
        json_mode: bool = False,
        timeout: int = 12,
    ) -> Optional[str]:
        if not self.enabled or not user.strip():
            return None

        messages = [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": user.strip()},
        ]

        try:
            if self.provider == "anthropic":
                return self._anthropic(messages, temperature, max_tokens, timeout)
            return self._openai(messages, temperature, max_tokens, json_mode, timeout)
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            KeyError,
            json.JSONDecodeError,
            TimeoutError,
            ValueError,
        ):
            return None

    def chat_json(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0,
        max_tokens: int = 400,
        timeout: int = 10,
    ) -> Optional[dict]:
        if self.provider == "anthropic":
            raw = self.chat(
                system + "\nReturn valid JSON only — no markdown fences.",
                user,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            if not raw:
                return None
            return self._parse_json(raw)

        raw = self.chat(
            system,
            user,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
            timeout=timeout,
        )
        if not raw:
            return None
        return self._parse_json(raw)

    def _openai(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
        json_mode: bool,
        timeout: int,
    ) -> Optional[str]:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        return content.strip() if content else None

    def _anthropic(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> Optional[str]:
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        chat_messages = []
        for m in messages:
            if m["role"] == "system":
                continue
            role = "assistant" if m["role"] == "assistant" else "user"
            chat_messages.append({"role": role, "content": m["content"]})

        if not chat_messages:
            return None

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": "\n\n".join(system_parts),
            "messages": chat_messages,
        }
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": self.anthropic_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        blocks = body.get("content") or []
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        return text.strip() if text else None

    @staticmethod
    def _parse_json(raw: str) -> Optional[dict]:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
