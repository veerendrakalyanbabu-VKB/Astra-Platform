"""Offline conversational replies when LLM is unavailable."""

import re
from typing import Optional


LOCAL_REPLIES = (
    (r"^(?:help me )?(?:to )?cook\b", (
        "Happy to help in the kitchen. Quick starts: scrambled eggs, "
        "garlic butter pasta, or a simple stir-fry with whatever veg you have. "
        "Tell me your ingredients and I'll suggest a recipe."
    )),
    (r"\b(recipe|ingredients|meal plan)\b", (
        "Share what's in your fridge — protein, carbs, and one vegetable — "
        "and I'll outline a fast meal. Example: 'chicken, rice, broccoli'."
    )),
    (r"^(?:thanks|thank you|ty)\b", (
        "You're welcome. I'm here whenever you need me."
    )),
)


def local_conversational_reply(text: str) -> Optional[str]:
    normalized = re.sub(r"\s+", " ", (text or "").lower().strip())
    if not normalized:
        return None

    for pattern, reply in LOCAL_REPLIES:
        if re.search(pattern, normalized):
            return reply

    return None
