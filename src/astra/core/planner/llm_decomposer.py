"""LLM-powered goal decomposition into routine steps."""

from typing import List, Optional

from astra.core.planner.routine_parser import parse_steps
from astra.core.llm.llm_client import LLMClient


STEP_VOCABULARY = """
Valid step phrases (comma-separated):
get time, show memory, system info, open chrome, open notepad, open calc,
open code, open folder downloads, focus notepad, set volume 50,
minimize all, list windows, show clipboard
"""


class LLMGoalDecomposer:

    def __init__(self, enabled: bool = None):
        self.client = LLMClient(enabled=enabled)
        self.enabled = self.client.enabled

    def decompose(self, goal: str, memory_hints: dict = None) -> Optional[list]:
        if not self.enabled:
            return None

        memory_context = ""
        if memory_hints:
            hints = ", ".join(f"{key}={value}" for key, value in list(memory_hints.items())[:5])
            memory_context = f"\nUser memory hints: {hints}"

        prompt = (
            f"Break this goal into 2-5 executable steps for a desktop assistant.\n"
            f"Goal: {goal}\n"
            f"{memory_context}\n"
            f"{STEP_VOCABULARY}\n"
            f'Return JSON: {{"steps": ["get time", "open chrome"]}}'
        )

        parsed = self.client.chat_json(
            "You decompose user goals into step lists.",
            prompt,
            temperature=0,
            max_tokens=300,
            timeout=10,
        )

        if not parsed:
            return None

        step_strings = parsed.get("steps", [])
        if not step_strings:
            return None

        combined = ", ".join(step_strings)
        steps, errors = parse_steps(combined)

        if steps and not errors:
            return steps

        return None
