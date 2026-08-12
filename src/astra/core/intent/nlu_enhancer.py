import os
import re
from typing import Optional

from astra.core.intent.models import IntentResult
from astra.core.intent.intents import (
    OPEN_APP,
    SAVE_MEMORY,
    RECALL_MEMORY,
    GET_TIME,
    HELP,
    LIST_MEMORY,
    ASK_KNOWLEDGE,
)


class NaturalLanguageEnhancer:
    """
    Local NLU layer for natural phrasing rule classifier misses.
    No external API required.
    """

    PATTERNS = (
        (r"^(?:can you|could you|please|i want to|i need to) open (.+)$", OPEN_APP, "app"),
        (r"^(?:can you|could you|please) launch (.+)$", OPEN_APP, "app"),
        (r"^(?:can you|could you|please) start (.+)$", OPEN_APP, "app"),
        (r"^(?:can you|could you|please) run (.+)$", OPEN_APP, "app"),
        (r"^(?:please )?remember (?:that )?(.+)$", SAVE_MEMORY, "memory"),
        (r"^(?:please )?save (?:that )?(.+)$", SAVE_MEMORY, "memory"),
        (r"^what(?:'s| is) my (.+)$", RECALL_MEMORY, "query"),
        (r"^do you remember (.+)$", RECALL_MEMORY, "query"),
        (r"^(?:i need|tell me|what is) the time$", GET_TIME, "none"),
        (r"^(?:show|list) (?:my )?memory$", LIST_MEMORY, "none"),
        (r"^(?:what can you do|show help)$", HELP, "none"),
        (r"^what do you know(?: about me)?$", LIST_MEMORY, "none"),
        (r"^help me (?:to |with )?(.+)$", ASK_KNOWLEDGE, "query"),
        (r"^(?:can you|could you|please) help me (?:to |with )?(.+)$", ASK_KNOWLEDGE, "query"),
        (r"^(?:hey|hi|hello)(?: astra)?$", ASK_KNOWLEDGE, "static_greeting"),
        (r"^good (?:morning|afternoon|evening)(?: astra)?$", ASK_KNOWLEDGE, "static_greeting"),
        (r"^(?:can you|could you) (.+)$", ASK_KNOWLEDGE, "query"),
    )

    def enhance(self, text: str) -> Optional[IntentResult]:
        for pattern, intent, entity_type in self.PATTERNS:
            match = re.match(pattern, text)

            if not match:
                continue

            entities = self._build_entities(intent, entity_type, match)
            return IntentResult(intent=intent, entities=entities, confidence=0.85)

        return None

    def _build_entities(self, intent: str, entity_type: str, match) -> dict:
        if entity_type == "app":
            return {"application": match.group(1).strip()}

        if entity_type == "memory":
            return {"text": match.group(1).strip()}

        if entity_type == "query":
            query = re.sub(r"[^\w\s]", "", match.group(1).strip())
            return {"query": query}

        if entity_type == "static_greeting":
            return {"query": "greeting"}

        return {}
