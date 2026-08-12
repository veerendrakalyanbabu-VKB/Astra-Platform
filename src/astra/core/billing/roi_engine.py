"""ROI tracking — proves value so users gladly pay."""

import json
from datetime import date, datetime, timedelta
from pathlib import Path

MINUTES_SAVED = {
    "RUN_PROTOCOL": 15,
    "ASK_AGENT": 6,
    "MORNING_BRIEF": 10,
    "RUN_GOAL": 12,
    "SYNC_MEMORY": 5,
    "OPEN_APP": 3,
    "CREATE_ROUTINE": 8,
    "SCHEDULE_ROUTINE": 6,
    "ACTIVATE_WORKSPACE": 5,
    "LIST_MEMORY": 2,
    "GET_TIME": 1,
    "CALCULATE": 2,
    "SYSTEM_INFO": 3,
    "REVOLUTION_STATUS": 1,
}

DEFAULT_MINUTES = 2
HOURLY_VALUE_USD = 25
TRIAL_DAYS = 30


class ROIEngine:

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.roi_file = self.project_root / "data" / "roi.json"
        self.state = self._load()

    def _load(self) -> dict:
        default = {
            "total_minutes_saved": 0,
            "total_tasks_automated": 0,
            "daily": {},
            "started_at": datetime.now().isoformat(),
        }
        if not self.roi_file.exists():
            return default

        try:
            data = json.loads(self.roi_file.read_text(encoding="utf-8"))
            return {**default, **data}
        except (json.JSONDecodeError, OSError):
            return default

    def _save(self) -> None:
        self.roi_file.parent.mkdir(parents=True, exist_ok=True)
        self.roi_file.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def record(self, success: bool, intent: str = "") -> None:
        if not success:
            return

        minutes = MINUTES_SAVED.get(intent, DEFAULT_MINUTES)
        today = date.today().isoformat()
        daily = self.state.setdefault("daily", {})

        if today not in daily:
            daily[today] = {"minutes": 0, "tasks": 0}

        daily[today]["minutes"] += minutes
        daily[today]["tasks"] += 1
        self.state["total_minutes_saved"] = self.state.get("total_minutes_saved", 0) + minutes
        self.state["total_tasks_automated"] = self.state.get("total_tasks_automated", 0) + 1
        self._save()

    def _week_minutes(self) -> int:
        cutoff = date.today() - timedelta(days=6)
        total = 0
        for day_str, stats in self.state.get("daily", {}).items():
            try:
                day = date.fromisoformat(day_str)
            except ValueError:
                continue
            if day >= cutoff:
                total += stats.get("minutes", 0)
        return total

    def _today_minutes(self) -> int:
        today = date.today().isoformat()
        return self.state.get("daily", {}).get(today, {}).get("minutes", 0)

    def dashboard(self) -> dict:
        week_minutes = self._week_minutes()
        total_minutes = self.state.get("total_minutes_saved", 0)
        week_hours = round(week_minutes / 60, 1)
        total_hours = round(total_minutes / 60, 1)
        week_value = round((week_minutes / 60) * HOURLY_VALUE_USD, 0)
        total_value = round((total_minutes / 60) * HOURLY_VALUE_USD, 0)

        return {
            "hours_saved_today": round(self._today_minutes() / 60, 1),
            "hours_saved_week": week_hours,
            "hours_saved_total": total_hours,
            "tasks_automated_week": sum(
                stats.get("tasks", 0)
                for day_str, stats in self.state.get("daily", {}).items()
                if self._in_last_7_days(day_str)
            ),
            "tasks_automated_total": self.state.get("total_tasks_automated", 0),
            "value_saved_week_usd": week_value,
            "value_saved_total_usd": total_value,
            "hourly_value_usd": HOURLY_VALUE_USD,
            "headline": self._headline(week_hours, week_value),
        }

    def _in_last_7_days(self, day_str: str) -> bool:
        try:
            day = date.fromisoformat(day_str)
        except ValueError:
            return False
        return day >= date.today() - timedelta(days=6)

    def _headline(self, week_hours: float, week_value: float) -> str:
        if week_hours >= 5:
            return f"Astra saved you ~{week_hours}h this week (${week_value:.0f} value)."
        if week_hours >= 1:
            return f"~{week_hours}h reclaimed this week — keep building the habit."
        return "Every command compounds. Run a protocol to jump-start ROI."

    def status_message(self) -> str:
        dash = self.dashboard()
        lines = [
            "◈ ASTRA ROI REPORT",
            "",
            dash["headline"],
            "",
            f"Today:     {dash['hours_saved_today']}h saved",
            f"This week: {dash['hours_saved_week']}h saved · {dash['tasks_automated_week']} tasks",
            f"All time:  {dash['hours_saved_total']}h saved · {dash['tasks_automated_total']} tasks",
            f"Value (@${HOURLY_VALUE_USD}/hr): ${dash['value_saved_week_usd']:.0f} this week · "
            f"${dash['value_saved_total_usd']:.0f} total",
            "",
            "Paid plans pay for themselves when you save 1+ hour/week.",
        ]
        return "\n".join(lines)
