"""30-day free trial lifecycle for Campus and Startup plans."""

import json
from datetime import datetime, timedelta
from pathlib import Path

from astra.core.billing.roi_engine import TRIAL_DAYS

TRIAL_TIERS = frozenset({"campus", "startup"})


class TrialManager:

    def __init__(self, project_root: Path, tier_manager):
        self.project_root = Path(project_root)
        self.tier_file = self.project_root / "data" / "tier.json"
        self.tier_manager = tier_manager

    def _read(self) -> dict:
        if not self.tier_file.exists():
            return {"tier": "cosmic"}

        try:
            return json.loads(self.tier_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"tier": "cosmic"}

    def _write(self, data: dict) -> None:
        self.tier_file.parent.mkdir(parents=True, exist_ok=True)
        self.tier_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def refresh(self) -> dict | None:
        """Expire trial if past end date. Returns expiry notice or None."""
        data = self._read()
        status = data.get("subscription_status")

        if status != "trial":
            return None

        trial_ends = data.get("trial_ends")
        if not trial_ends:
            return None

        try:
            ends = datetime.fromisoformat(trial_ends)
        except ValueError:
            return None

        if datetime.now() <= ends:
            return None

        previous_tier = data.get("tier", "campus")
        data["tier"] = "cosmic"
        data["subscription_status"] = "expired"
        data["expired_at"] = datetime.now().isoformat()
        data["previous_tier"] = previous_tier
        self._write(data)
        self.tier_manager.reload()

        tier_name = previous_tier.title()
        return {
            "expired": True,
            "message": (
                f"Your {tier_name} trial ended. You're on Cosmic (free) again. "
                f"Subscribe at the portal to keep MENTOR, morning brief, and unlimited commands."
            ),
        }

    def start_trial(self, tier_id: str, email: str = "", name: str = "") -> dict:
        if tier_id not in TRIAL_TIERS:
            return {
                "success": False,
                "message": f"Trial available for Campus and Startup only. Requested: {tier_id}",
            }

        data = self._read()

        if data.get("trial_used") and data.get("subscription_status") != "trial":
            return {
                "success": False,
                "message": (
                    "Free trial already used on this device. "
                    "Subscribe at the portal or say 'show plans'."
                ),
            }

        if data.get("subscription_status") == "trial":
            days = self.days_remaining(data)
            return {
                "success": True,
                "message": (
                    f"Trial already active — {days} days left on {data.get('tier', tier_id).title()}. "
                    "Open Command OS: python main.py --desktop"
                ),
                "days_remaining": days,
            }

        if data.get("subscription_status") == "active":
            return {
                "success": False,
                "message": "You already have an active paid plan.",
            }

        now = datetime.now()
        ends = now + timedelta(days=TRIAL_DAYS)

        payload = {
            "tier": tier_id,
            "source": "free_trial",
            "subscription_status": "trial",
            "trial_used": True,
            "trial_started": now.isoformat(),
            "trial_ends": ends.isoformat(),
            "activated_at": now.isoformat(),
            "customer_email": email,
            "customer_name": name,
        }
        self._write(payload)
        self.tier_manager.reload()

        tier = self.tier_manager.get_tier()
        return {
            "success": True,
            "message": (
                f"✓ 30-day {tier['name']} trial started. Full squad unlocked until "
                f"{ends.strftime('%b %d, %Y')}. "
                "Run: python main.py --desktop → try 'morning brief' or 'industrial revolution'"
            ),
            "days_remaining": TRIAL_DAYS,
            "trial_ends": ends.isoformat(),
        }

    def snapshot(self) -> dict:
        data = self._read()
        status = data.get("subscription_status", "free")
        days = self.days_remaining(data)

        return {
            "status": status,
            "on_trial": status == "trial",
            "days_remaining": days,
            "trial_ends": data.get("trial_ends"),
            "trial_started": data.get("trial_started"),
            "trial_used": data.get("trial_used", False),
            "tier_id": data.get("tier", "cosmic"),
            "email": data.get("customer_email", ""),
            "expiring_soon": status == "trial" and days is not None and days <= 5,
        }

    def days_remaining(self, data: dict = None) -> int | None:
        data = data or self._read()
        if data.get("subscription_status") != "trial":
            return None

        trial_ends = data.get("trial_ends")
        if not trial_ends:
            return None

        try:
            ends = datetime.fromisoformat(trial_ends)
        except ValueError:
            return None

        delta = ends - datetime.now()
        return max(0, delta.days + (1 if delta.seconds > 0 else 0))
