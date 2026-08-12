"""Daily command usage tracking for freemium tier limits."""

import json
from datetime import date
from pathlib import Path

COSMIC_DAILY_LIMIT = 75

EXEMPT_INTENTS = frozenset({
    "HELP",
    "SHOW_PLANS",
    "ACTIVATE_PLAN",
    "REVOLUTION_STATUS",
    "SHOW_ROI",
    "START_TRIAL",
    "MORNING_BRIEF",
    "SHOW_WEATHER",
    "SHOW_CALENDAR",
    "DETECT_LOCATION",
    "SHOW_SQUAD",
    "GET_TIME",
    "LIST_MEMORY",
    "SHOW_VOICE_SETTINGS",
    "SET_CITY",
})


class UsageTracker:

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.usage_file = self.project_root / "data" / "usage.json"

    def _load(self) -> dict:
        if not self.usage_file.exists():
            return {"date": date.today().isoformat(), "count": 0}

        try:
            data = json.loads(self.usage_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"date": date.today().isoformat(), "count": 0}

        if data.get("date") != date.today().isoformat():
            return {"date": date.today().isoformat(), "count": 0}

        return data

    def _save(self, data: dict) -> None:
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        self.usage_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def daily_limit(self, tier_id: str) -> int | None:
        if tier_id == "cosmic":
            return COSMIC_DAILY_LIMIT
        return None

    def snapshot(self, tier_id: str) -> dict:
        data = self._load()
        limit = self.daily_limit(tier_id)
        used = data.get("count", 0)

        if limit is None:
            return {
                "limited": False,
                "used": used,
                "limit": None,
                "remaining": None,
            }

        return {
            "limited": True,
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used),
        }

    def check_allowed(self, tier_id: str, intent: str = "") -> tuple[bool, str]:
        if tier_id != "cosmic":
            return True, ""

        if intent in EXEMPT_INTENTS:
            return True, ""

        snap = self.snapshot(tier_id)
        if snap["remaining"] <= 0:
            return False, (
                f"Cosmic daily limit reached ({snap['limit']} action commands). "
                "Read-only commands still work: show weather, show squad, morning brief. "
                "Resets at midnight — or say 'show plans' when you're ready to upgrade."
            )

        return True, ""

    def record(self, tier_id: str, intent: str = "") -> None:
        if tier_id != "cosmic" or intent in EXEMPT_INTENTS:
            return

        data = self._load()
        data["count"] = data.get("count", 0) + 1
        data["date"] = date.today().isoformat()
        self._save(data)
