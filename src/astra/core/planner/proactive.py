"""Proactive suggestions based on time, memory, and learning."""

from datetime import datetime


class ProactiveEngine:

    TIME_SUGGESTIONS = {
        "morning": [
            "morning brief",
            "show weather",
            "organize my morning routine",
            "industrial revolution",
        ],
        "afternoon": [
            "revolution status",
            "show squad",
            "ask nova about AI trends",
        ],
        "evening": [
            "revolution status",
            "sync my memory",
            "show my memory",
        ],
    }

    WORKSPACE_SUGGESTIONS = [
        "activate coding workspace",
        "activate focus workspace",
        "activate chill workspace",
    ]

    def __init__(self, memory_manager=None, learning_engine=None):
        self.memory = memory_manager
        self.learning = learning_engine

    def suggest(self, limit: int = 5) -> list:
        suggestions = []
        period = self._time_period()

        for item in self.TIME_SUGGESTIONS.get(period, []):
            suggestions.append({"command": item, "reason": f"{period.title()} suggestion"})

        if self.learning:
            stats = self.learning.stats()

            for intent, count in stats.get("top_intents", {}).items():
                mapped = self._intent_to_command(intent)

                if mapped:
                    suggestions.append({
                        "command": mapped,
                        "reason": f"You often use {intent.lower()}",
                    })

        if self.memory and self.memory.exists("goal"):
            suggestions.append({
                "command": "what is my goal",
                "reason": "Check your saved goal",
            })

        suggestions.extend([
            {"command": cmd, "reason": "Workspace preset"}
            for cmd in self.WORKSPACE_SUGGESTIONS
        ])

        seen = set()
        unique = []

        for item in suggestions:
            if item["command"] not in seen:
                seen.add(item["command"])
                unique.append(item)

            if len(unique) >= limit:
                break

        return unique

    def _time_period(self) -> str:
        hour = datetime.now().hour

        if hour < 12:
            return "morning"

        if hour < 17:
            return "afternoon"

        return "evening"

    def _intent_to_command(self, intent: str) -> str:
        mapping = {
            "GET_TIME": "what time is it",
            "OPEN_APP": "open notepad",
            "RUN_GOAL": "organize my morning routine",
            "RUN_PROTOCOL": "industrial revolution",
            "REVOLUTION_STATUS": "revolution status",
            "LIST_MEMORY": "show my memory",
            "SYNC_MEMORY": "sync my memory",
            "SYSTEM_INFO": "system info",
        }
        return mapping.get(intent, "")
