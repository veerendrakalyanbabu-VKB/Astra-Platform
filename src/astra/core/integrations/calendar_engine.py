"""Calendar via public ICS feed — Google Calendar secret URL supported."""

import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List


class CalendarEngine:

    def __init__(self, integrations_store):
        self.settings = integrations_store

    def today_events(self, limit: int = 5) -> Dict:
        url = (self.settings.get("calendar_ics_url") or "").strip()
        if not url:
            return {
                "available": False,
                "message": (
                    "Connect calendar: say 'connect calendar https://...ics' "
                    "(Google Calendar → Settings → Secret address in iCal format)"
                ),
                "events": [],
                "lines": [],
            }

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                text = response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            return {
                "available": False,
                "message": "Could not fetch calendar. Check your ICS URL.",
                "events": [],
                "lines": [],
            }

        events = self._parse_today(text)[:limit]
        if not events:
            return {
                "available": True,
                "message": "No events on your calendar today.",
                "events": [],
                "lines": ["Calendar clear today — deep work window open."],
            }

        lines = [f"{e['time']} — {e['title']}" for e in events]
        return {
            "available": True,
            "message": "Today's schedule:\n" + "\n".join(f"  • {l}" for l in lines),
            "events": events,
            "lines": lines,
        }

    def _parse_today(self, ics_text: str) -> List[dict]:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        blocks = re.split(r"BEGIN:VEVENT", ics_text, flags=re.IGNORECASE)
        events = []

        for block in blocks[1:]:
            summary = self._field(block, "SUMMARY") or "Event"
            dtstart = self._field(block, "DTSTART")
            if not dtstart:
                continue

            start = self._parse_dt(dtstart)
            if not start or not (today <= start.date() < tomorrow):
                continue

            events.append({
                "title": summary.strip(),
                "time": start.strftime("%H:%M"),
                "start": start.isoformat(),
            })

        events.sort(key=lambda e: e["start"])
        return events

    @staticmethod
    def _field(block: str, name: str) -> str:
        match = re.search(rf"^{name}[;:](.+)$", block, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _parse_dt(raw: str) -> datetime | None:
        raw = raw.strip()
        if raw.startswith("VALUE=DATE:"):
            raw = raw.split(":", 1)[-1]
        if "T" in raw:
            clean = raw.replace("Z", "")[:15]
            try:
                return datetime.strptime(clean, "%Y%m%dT%H%M%S")
            except ValueError:
                return None
        try:
            return datetime.strptime(raw[:8], "%Y%m%d")
        except ValueError:
            return None
