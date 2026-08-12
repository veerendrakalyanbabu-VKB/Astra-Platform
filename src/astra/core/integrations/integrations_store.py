"""User integration settings — calendar, weather, location."""

import json
from pathlib import Path
from typing import Dict


class IntegrationsStore:

    def __init__(self, project_root: Path):
        self.path = Path(project_root) / "data" / "integrations.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as file:
                    return {**self.defaults(), **json.load(file)}
            except (json.JSONDecodeError, OSError):
                pass
        data = self.defaults()
        self._save(data)
        return data

    def defaults(self) -> dict:
        return {
            "calendar_ics_url": "",
            "city": "",
            "latitude": None,
            "longitude": None,
            "focus_minutes": 25,
            "auto_location": True,
            "location_source": "",
            "region": "",
            "country": "",
            "location_detected_at": "",
        }

    def _save(self, data: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set_calendar_url(self, url: str) -> dict:
        url = (url or "").strip()
        if url and not url.startswith(("http://", "https://", "webcal://")):
            return {"success": False, "message": "Calendar URL must start with http:// or https://"}
        self._data["calendar_ics_url"] = url.replace("webcal://", "https://", 1)
        self._save(self._data)
        return {"success": True, "message": "Calendar connected. Say 'show calendar' or 'morning brief'."}

    def set_city(self, city: str) -> dict:
        city = (city or "").strip()[:64]
        if not city:
            return {"success": False, "message": "City name cannot be empty."}
        self._data["city"] = city
        self._data["latitude"] = None
        self._data["longitude"] = None
        self._data["location_source"] = "manual"
        self._data["location_detected_at"] = ""
        self._save(self._data)
        return {"success": True, "message": f"Location set to {city}. Say 'show weather'."}

    def snapshot(self) -> Dict:
        return dict(self._data)
