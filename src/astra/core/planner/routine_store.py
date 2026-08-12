"""Persistent custom user-defined routines."""

import json
from pathlib import Path

from astra.core.planner.plan import PlanStep


class RoutineStore:

    def __init__(self, project_root=None):
        root = Path(project_root or Path.cwd())
        self.data_dir = root / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.store_file = self.data_dir / "routines.json"
        self.routines = self._load()

    def save_routine(self, key: str, title: str, steps: list, description: str = "") -> None:
        self.routines[key] = {
            "title": title,
            "description": description or f"Custom routine: {title}",
            "steps": [
                {"action": step.action, "parameters": step.parameters}
                for step in steps
            ],
        }
        self._persist()

    def delete_routine(self, key: str) -> bool:
        if key not in self.routines:
            return False

        del self.routines[key]
        self._persist()
        return True

    def get_routine(self, key: str):
        normalized = key.lower().strip().replace(" ", "_")
        routine = self.routines.get(normalized)

        if not routine:
            return None

        steps = [
            PlanStep(entry["action"], entry.get("parameters", {}))
            for entry in routine["steps"]
        ]

        return {
            "title": routine["title"],
            "description": routine["description"],
            "steps": steps,
        }

    def list_all(self) -> list:
        return [
            {
                "key": key,
                "title": routine["title"],
                "description": routine["description"],
                "steps": len(routine["steps"]),
                "custom": True,
            }
            for key, routine in self.routines.items()
        ]

    def _load(self) -> dict:
        if not self.store_file.exists():
            return {}

        with open(self.store_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def _persist(self) -> None:
        with open(self.store_file, "w", encoding="utf-8") as file:
            json.dump(self.routines, file, indent=2)

    def reconfigure(self, profile_dir: Path) -> None:
        profile_dir = Path(profile_dir)
        profile_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = profile_dir
        self.store_file = profile_dir / "routines.json"
        self.routines = self._load()
