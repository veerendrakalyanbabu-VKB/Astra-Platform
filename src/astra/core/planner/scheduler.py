"""Scheduled routine and protocol execution."""

import json
import re
from datetime import datetime
from pathlib import Path

SCHEDULE_COMMANDS = {
    "morning": "morning brief",
    "brief": "morning brief",
    "morning_brief": "morning brief",
    "morningbrief": "morning brief",
    "startup": "run startup protocol",
    "startup_protocol": "run startup protocol",
    "student": "run student protocol",
    "student_protocol": "run student protocol",
    "revolution": "industrial revolution",
    "industrial": "industrial revolution",
    "roi": "show roi",
    "sync": "sync my memory",
}


class RoutineScheduler:

    def __init__(self, project_root=None):
        root = Path(project_root or Path.cwd())
        self.schedule_file = root / "data" / "schedules.json"
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
        self.schedules = self._load()

    def resolve_command(self, name: str) -> str:
        key = name.lower().strip().replace(" ", "_")
        if key in SCHEDULE_COMMANDS:
            return SCHEDULE_COMMANDS[key]
        normalized = name.lower().strip()
        if normalized in SCHEDULE_COMMANDS.values():
            return normalized
        return f"run {name.replace('_', ' ')}"

    def add(self, routine_key: str, time_str: str, command: str = None) -> dict:
        parsed_time = self._parse_time(time_str)
        key = routine_key.lower().replace(" ", "_")
        resolved = command or self.resolve_command(routine_key)

        self.schedules[key] = {
            "routine": key,
            "command": resolved,
            "time": parsed_time,
            "enabled": True,
            "last_run": None,
        }
        self._save()

        return self.schedules[key]

    def remove(self, routine_key: str) -> bool:
        key = routine_key.lower().replace(" ", "_")

        if key not in self.schedules:
            return False

        del self.schedules[key]
        self._save()
        return True

    def list_all(self) -> list:
        return list(self.schedules.values())

    def run_due(self, run_callback) -> list:
        now = datetime.now()
        current = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")
        executed = []

        for key, entry in self.schedules.items():
            if not entry.get("enabled"):
                continue

            if entry.get("time") != current:
                continue

            if entry.get("last_run") == today:
                continue

            command = entry.get("command") or self.resolve_command(key)
            result = run_callback(command, entry)
            entry["last_run"] = today
            executed.append({
                "routine": key,
                "command": command,
                "time": entry.get("time"),
                "result": result,
            })

        if executed:
            self._save()

        return executed

    def _parse_time(self, time_str: str) -> str:
        normalized = time_str.lower().strip()

        match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", normalized)

        if not match:
            return "08:00"

        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        meridiem = match.group(3)

        if meridiem == "pm" and hour < 12:
            hour += 12

        if meridiem == "am" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute:02d}"

    def _load(self) -> dict:
        if not self.schedule_file.exists():
            return {}

        with open(self.schedule_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        for key, entry in data.items():
            if "command" not in entry:
                entry["command"] = self.resolve_command(entry.get("routine", key))

        return data

    def _save(self) -> None:
        with open(self.schedule_file, "w", encoding="utf-8") as file:
            json.dump(self.schedules, file, indent=2)

    def reconfigure(self, profile_dir: Path) -> None:
        profile_dir = Path(profile_dir)
        profile_dir.mkdir(parents=True, exist_ok=True)
        self.schedule_file = profile_dir / "schedules.json"
        self.schedules = self._load()
