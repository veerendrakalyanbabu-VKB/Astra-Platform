import json
from pathlib import Path


DEFAULT_KNOWLEDGE = {
    "entries": [
        {
            "topic": "astra",
            "keywords": ["astra", "platform", "what are you"],
            "content": (
                "Astra is the Industrial Revolution of computing — an intent-first Command OS "
                "where human goals flow through named agent factories (CORE, NOVA, PILOT, MENTOR, "
                "LAUNCH, LEDGER), not scattered apps. Say 'industrial revolution' to run the full protocol."
            ),
        },
        {
            "topic": "memory",
            "keywords": ["memory", "remember", "recall", "save facts"],
            "content": (
                "Say 'remember my favorite color is blue' to save a fact. "
                "Ask 'what is my favorite color' to recall it. "
                "Use 'show my memory' to list everything stored."
            ),
        },
        {
            "topic": "safety",
            "keywords": ["safety", "confirm", "block", "risk", "permission"],
            "content": (
                "Low-risk actions execute immediately. High-risk actions "
                "require confirmation. Critically dangerous actions are "
                "always blocked."
            ),
        },
        {
            "topic": "tools",
            "keywords": ["tools", "calculator", "compute", "calculate"],
            "content": (
                "Say 'calculate 15 * 7' or 'what is 100 divided by 4' "
                "to use the built-in calculator tool."
            ),
        },
        {
            "topic": "cooking",
            "keywords": [
                "cook", "cooking", "recipe", "meal", "food", "kitchen",
                "dinner", "lunch", "breakfast", "bake",
            ],
            "content": (
                "I can help you cook. Tell me what ingredients you have, "
                "or ask for a quick meal — e.g. 'easy pasta recipe' or "
                "'what can I make with eggs and rice'. "
                "With LLM active I can give step-by-step recipes; "
                "offline I can still suggest simple ideas like stir-fry, "
                "omelette, rice bowls, or sheet-pan meals."
            ),
        },
        {
            "topic": "greeting",
            "keywords": [
                "hey", "hello", "hi", "good morning", "good evening",
                "good afternoon", "hey astra", "hello astra",
            ],
            "content": (
                "Hey — Astra online. I'm your command OS: memory, routines, "
                "workspaces, agents, and morning brief on paid tiers. "
                "Try 'what time is it', 'show squad', or 'help me plan my morning'."
            ),
        },
    ]
}


class KnowledgeEngine:
    """
    Local structured knowledge retrieval.
    """

    def __init__(self, knowledge_path: Path = None):
        self.knowledge_path = knowledge_path or Path("data/knowledge.json")
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self) -> dict:
        if not self.knowledge_path.exists():
            self.knowledge_path.parent.mkdir(parents=True, exist_ok=True)
            self.knowledge_path.write_text(
                json.dumps(DEFAULT_KNOWLEDGE, indent=4),
                encoding="utf-8",
            )
            return DEFAULT_KNOWLEDGE

        with open(self.knowledge_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def search(self, query: str) -> list:
        normalized = query.lower().strip()
        results = []

        for entry in self.knowledge.get("entries", []):
            score = 0

            if normalized in entry.get("topic", "").lower():
                score += 3

            for keyword in entry.get("keywords", []):
                if keyword in normalized or normalized in keyword:
                    score += 2

            if score > 0:
                results.append({"score": score, **entry})

        results.sort(key=lambda item: item["score"], reverse=True)
        return results

    def best_match(self, query: str) -> str | None:
        results = self.search(query)

        if not results:
            return None

        return results[0]["content"]

    def list_topics(self) -> list:
        return [entry["topic"] for entry in self.knowledge.get("entries", [])]
