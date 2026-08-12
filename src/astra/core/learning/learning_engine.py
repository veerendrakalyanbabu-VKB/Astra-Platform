import json
from datetime import datetime
from pathlib import Path


class LearningEngine:
    """
    Tracks pipeline outcomes for future improvement.
    """

    def __init__(self, learning_path: Path = None):
        self.learning_path = learning_path or Path("data/learning.json")
        self.records = self._load()

    def _load(self) -> list:
        if not self.learning_path.exists():
            self.learning_path.parent.mkdir(parents=True, exist_ok=True)
            self.learning_path.write_text("[]", encoding="utf-8")
            return []

        with open(self.learning_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def record(self, user_input: str, intent: str, success: bool, message: str) -> None:
        self.records.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "intent": intent,
            "success": success,
            "message": message,
        })

        if len(self.records) > 500:
            self.records = self.records[-500:]

        self._save()

    def _save(self) -> None:
        with open(self.learning_path, "w", encoding="utf-8") as file:
            json.dump(self.records, file, indent=2)

    def stats(self) -> dict:
        total = len(self.records)

        if total == 0:
            return {"total": 0, "success_rate": 0.0, "top_intents": {}}

        successes = sum(1 for item in self.records if item["success"])
        intent_counts = {}

        for item in self.records:
            intent_counts[item["intent"]] = intent_counts.get(item["intent"], 0) + 1

        top = dict(sorted(intent_counts.items(), key=lambda pair: pair[1], reverse=True)[:5])

        return {
            "total": total,
            "success_rate": round(successes / total, 3),
            "top_intents": top,
        }

    def reconfigure(self, learning_path: Path) -> None:
        self.learning_path = Path(learning_path)
        self.records = self._load()
