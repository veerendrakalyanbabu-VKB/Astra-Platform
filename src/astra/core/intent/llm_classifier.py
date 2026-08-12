from typing import Optional

from astra.core.intent.models import IntentResult
from astra.core.intent.intents import UNKNOWN
from astra.core.llm.llm_client import LLMClient


INTENT_SCHEMA = """
Return JSON only with keys: intent, entities, confidence.
Valid intents: OPEN_APP, SAVE_MEMORY, RECALL_MEMORY, LIST_MEMORY,
GET_TIME, ASK_KNOWLEDGE, CALCULATE, HELP, DELETE_FILE, SHUTDOWN_PC,
FORMAT_DISK, UNKNOWN.

Entity keys by intent:
- OPEN_APP: application
- SAVE_MEMORY: text
- RECALL_MEMORY: query
- ASK_KNOWLEDGE: query
- CALCULATE: expression
- DELETE_FILE: target
- FORMAT_DISK: drive
"""


class LLMClassifier:
    """
    Optional LLM intent classifier.
    Falls back gracefully when no API key or network failure.
    """

    def __init__(self, enabled: bool = None):
        self.client = LLMClient(enabled=enabled)
        self.enabled = self.client.enabled

    def classify(self, text: str) -> Optional[IntentResult]:
        if not self.enabled:
            return None

        prompt = (
            f"Classify this user command for an OS assistant.\n"
            f"Command: {text}\n"
            f"{INTENT_SCHEMA}"
        )

        parsed = self.client.chat_json(
            "You classify user intent into structured JSON.",
            prompt,
            temperature=0,
            max_tokens=200,
            timeout=8,
        )

        if not parsed:
            return None

        intent = parsed.get("intent", UNKNOWN)
        entities = parsed.get("entities", {})
        confidence = float(parsed.get("confidence", 0.75))

        if intent == UNKNOWN:
            return None

        return IntentResult(
            intent=intent,
            entities=entities,
            confidence=confidence,
        )
