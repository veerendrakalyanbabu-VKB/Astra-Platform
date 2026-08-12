"""Automatic location from IP — no API key, opt-out via ASTRA_AUTO_LOCATION=false."""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, Optional


class LocationEngine:
    """
    Detects approximate city from the user's public IP.
    Used for weather and morning brief when no manual city is set.
    """

    CACHE_HOURS = 24
    PROVIDERS = (
        "https://ipwho.is/",
        "http://ip-api.com/json/?fields=status,city,regionName,country,lat,lon",
    )

    def __init__(self, integrations_store):
        self.settings = integrations_store

    def auto_enabled(self) -> bool:
        flag = os.environ.get("ASTRA_AUTO_LOCATION", "true").strip().lower()
        return flag not in ("0", "false", "no", "off")

    def detect(self, force: bool = False) -> Dict:
        if not self.auto_enabled() and not force:
            return {
                "success": False,
                "message": "Auto-location is off. Set ASTRA_AUTO_LOCATION=true or say 'set city to YourCity'.",
            }

        if not force and self._cache_fresh():
            return {
                "success": True,
                "message": f"Location: {self.settings.get('city')} (cached)",
                "city": self.settings.get("city"),
                "source": self.settings.get("location_source", "ip"),
            }

        for url in self.PROVIDERS:
            hit = self._fetch(url)
            if hit:
                self._apply(hit)
                return {
                    "success": True,
                    "message": (
                        f"Detected your location: {hit['city']}"
                        + (f", {hit['region']}" if hit.get("region") else "")
                        + (f", {hit['country']}" if hit.get("country") else "")
                        + ". Weather and morning brief will use this automatically."
                    ),
                    **hit,
                }

        return {
            "success": False,
            "message": "Could not detect location from IP. Say 'set city to YourCity' manually.",
        }

    def ensure_location(self) -> bool:
        """Return True if city or coords are available (detect if needed)."""
        if (self.settings.get("city") or "").strip():
            return True
        if self.settings.get("latitude") is not None and self.settings.get("longitude") is not None:
            return True
        if not self.auto_enabled():
            return False
        result = self.detect()
        return result.get("success", False)

    def _cache_fresh(self) -> bool:
        if not (self.settings.get("city") or "").strip():
            return False
        if self.settings.get("location_source") != "ip":
            return bool((self.settings.get("city") or "").strip())

        detected_at = self.settings.get("location_detected_at")
        if not detected_at:
            return False
        try:
            ts = datetime.fromisoformat(detected_at)
            return datetime.now() - ts < timedelta(hours=self.CACHE_HOURS)
        except ValueError:
            return False

    def _apply(self, hit: dict) -> None:
        self.settings._data["city"] = hit["city"]
        self.settings._data["region"] = hit.get("region", "")
        self.settings._data["country"] = hit.get("country", "")
        self.settings._data["latitude"] = hit.get("latitude")
        self.settings._data["longitude"] = hit.get("longitude")
        self.settings._data["location_source"] = hit.get("source", "ip")
        self.settings._data["location_detected_at"] = datetime.now().isoformat()
        self.settings._data["auto_location"] = True
        self.settings._save(self.settings._data)

    def _fetch(self, url: str) -> Optional[dict]:
        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, KeyError):
            return None

        if "ipwho.is" in url:
            if not body.get("success", True):
                return None
            city = (body.get("city") or "").strip()
            if not city:
                return None
            return {
                "city": city,
                "region": body.get("region") or "",
                "country": body.get("country") or body.get("country_code") or "",
                "latitude": body.get("latitude"),
                "longitude": body.get("longitude"),
                "source": "ip",
            }

        if body.get("status") != "success":
            return None
        city = (body.get("city") or "").strip()
        if not city:
            return None
        return {
            "city": city,
            "region": body.get("regionName") or "",
            "country": body.get("country") or "",
            "latitude": body.get("lat"),
            "longitude": body.get("lon"),
            "source": "ip",
        }

    def format_location_line(self) -> str:
        city = self.settings.get("city") or "Unknown"
        region = self.settings.get("region") or ""
        country = self.settings.get("country") or ""
        parts = [city]
        if region and region.lower() != city.lower():
            parts.append(region)
        if country:
            parts.append(country)
        source = self.settings.get("location_source", "manual")
        tag = "auto" if source == "ip" else "manual"
        return f"{', '.join(parts)} ({tag})"
