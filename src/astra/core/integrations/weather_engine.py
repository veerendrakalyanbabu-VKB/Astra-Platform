"""Weather via Open-Meteo — no API key required."""

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional


WMO_LABELS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light drizzle",
    61: "Rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Snow",
    80: "Showers",
    95: "Thunderstorm",
}


class WeatherEngine:

    def __init__(self, integrations_store, location_engine=None):
        self.settings = integrations_store
        self.location = location_engine

    def _coords(self) -> Optional[tuple]:
        lat = self.settings.get("latitude")
        lon = self.settings.get("longitude")
        if lat is not None and lon is not None:
            return float(lat), float(lon)

        city = (self.settings.get("city") or "").strip()
        if not city and self.location:
            self.location.ensure_location()
            city = (self.settings.get("city") or "").strip()
            lat = self.settings.get("latitude")
            lon = self.settings.get("longitude")
            if lat is not None and lon is not None:
                return float(lat), float(lon)

        if not city:
            return None

        url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            + urllib.parse.urlencode({"name": city, "count": 1, "language": "en", "format": "json"})
        )
        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                body = json.loads(response.read().decode("utf-8"))
            results = body.get("results") or []
            if not results:
                return None
            hit = results[0]
            self.settings._data["latitude"] = hit["latitude"]
            self.settings._data["longitude"] = hit["longitude"]
            self.settings._save(self.settings._data)
            return hit["latitude"], hit["longitude"]
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError, json.JSONDecodeError):
            return None

    def current(self) -> Dict:
        coords = self._coords()
        if not coords:
            return {
                "available": False,
                "message": (
                    "Location unknown. Auto-detect is on — try 'detect my location' "
                    "or say 'set city to YourCity'."
                ),
                "lines": [],
            }

        lat, lon = coords
        params = urllib.parse.urlencode({
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
        })
        url = f"https://api.open-meteo.com/v1/forecast?{params}"

        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            return {"available": False, "message": "Weather service unreachable.", "lines": []}

        current = body.get("current") or {}
        temp = current.get("temperature_2m")
        code = int(current.get("weather_code", 0))
        wind = current.get("wind_speed_10m")
        label = WMO_LABELS.get(code, "Variable conditions")
        city = self.settings.get("city") or "your area"

        line = f"{city}: {label}"
        if temp is not None:
            line += f", {temp:.0f}°C"
        if wind is not None:
            line += f", wind {wind:.0f} km/h"

        return {
            "available": True,
            "message": line,
            "lines": [line],
            "temp_c": temp,
            "label": label,
            "at": datetime.now().isoformat(),
        }
