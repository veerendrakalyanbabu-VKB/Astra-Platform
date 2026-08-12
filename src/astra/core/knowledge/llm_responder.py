"""Optional LLM conversational fallback when rules and local knowledge miss."""

from typing import Dict, List, Optional

from astra.core.llm.llm_client import LLMClient


SYSTEM_PROMPT = """You are Astra — a personal command OS running locally on the user's device.
You are warm, direct, and capable. Keep replies concise (under 120 words) unless the user asks for detail.
Remember the conversation in this session — refer back when helpful.
You can open apps, save/recall memory, run routines, morning briefs, and agent protocols on-device.
Do not claim you executed an action unless the user explicitly asked for one.
Privacy: user data stays local unless they opt into sync; never ask for passwords or secrets."""


def conversation_to_turns(conversation: list) -> List[Dict[str, str]]:
    turns = []
    for msg in conversation or []:
        speaker = (msg.get("speaker") or "").lower()
        text = (msg.get("text") or "").strip()
        if not text:
            continue
        role = "assistant" if speaker in ("astra", "assistant") else "user"
        turns.append({"role": role, "content": text})
    return turns[-18:]


class LLMResponder:
    """Generates natural-language answers when structured handlers cannot."""

    def __init__(self, enabled: bool = None):
        self.client = LLMClient(enabled=enabled)
        self.enabled = self.client.enabled

    def respond(
        self,
        user_input: str,
        memory_entries: Dict[str, str] = None,
        conversation: list = None,
    ) -> Optional[str]:
        if not self.enabled or not user_input.strip():
            return None

        memory_context = ""
        if memory_entries:
            lines = [f"- {key}: {value}" for key, value in list(memory_entries.items())[:8]]
            memory_context = "\nKnown facts about the user:\n" + "\n".join(lines)

        turns = conversation_to_turns(conversation)
        turns.append({"role": "user", "content": user_input.strip()})

        return self.client.chat_turns(
            SYSTEM_PROMPT + memory_context,
            turns,
            temperature=0.7,
            max_tokens=300,
        )
