"""Subscription tiers, trials, and feature gating for Astra Command OS."""

import json
from datetime import datetime
from pathlib import Path

from astra.core.billing.roi_engine import TRIAL_DAYS

TIERS = {
    "cosmic": {
        "id": "cosmic",
        "name": "Cosmic",
        "price": 0,
        "price_label": "Free forever",
        "tagline": "Personal command line + 3 agents",
        "agents": {"core", "nova", "pilot"},
        "features": {
            "morning_brief": False,
            "cloud_sync": False,
            "gesture_voice": True,
            "marketplace": True,
            "startup_mode": False,
            "student_mode": True,
            "max_profiles": 2,
        },
    },
    "campus": {
        "id": "campus",
        "name": "Campus",
        "price": 9,
        "price_label": "$9 / student / mo",
        "tagline": "MENTOR + study workflows + brief",
        "agents": {"core", "nova", "pilot", "mentor"},
        "features": {
            "morning_brief": True,
            "cloud_sync": True,
            "gesture_voice": True,
            "marketplace": True,
            "startup_mode": False,
            "student_mode": True,
            "max_profiles": 5,
        },
    },
    "startup": {
        "id": "startup",
        "name": "Startup",
        "price": 29,
        "price_label": "$29 / team / mo",
        "tagline": "LAUNCH + LEDGER + full squad + brief",
        "agents": {"core", "nova", "pilot", "mentor", "launch", "ledger"},
        "features": {
            "morning_brief": True,
            "cloud_sync": True,
            "gesture_voice": True,
            "marketplace": True,
            "startup_mode": True,
            "student_mode": True,
            "max_profiles": 10,
        },
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise",
        "price": None,
        "price_label": "Custom",
        "tagline": "White-label, SSO, dedicated deploy",
        "agents": {"core", "nova", "pilot", "mentor", "launch", "ledger"},
        "features": {
            "morning_brief": True,
            "cloud_sync": True,
            "gesture_voice": True,
            "marketplace": True,
            "startup_mode": True,
            "student_mode": True,
            "max_profiles": 999,
        },
    },
}


class TierManager:

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.tier_file = self.project_root / "data" / "tier.json"
        self._data = self._load_data()
        self._tier_id = self._effective_tier(self._data)

    def _load_data(self) -> dict:
        if not self.tier_file.exists():
            return {"tier": "cosmic", "subscription_status": "free"}

        try:
            data = json.loads(self.tier_file.read_text(encoding="utf-8"))
            tier = data.get("tier", "cosmic")
            if tier not in TIERS:
                data["tier"] = "cosmic"
            return data
        except (json.JSONDecodeError, OSError):
            return {"tier": "cosmic", "subscription_status": "free"}

    def _effective_tier(self, data: dict) -> str:
        tier = data.get("tier", "cosmic")
        if tier not in TIERS:
            return "cosmic"

        if data.get("subscription_status") == "trial":
            trial_ends = data.get("trial_ends")
            if trial_ends:
                try:
                    if datetime.now() > datetime.fromisoformat(trial_ends):
                        return "cosmic"
                except ValueError:
                    pass

        return tier

    def reload(self) -> None:
        self._data = self._load_data()
        self._tier_id = self._effective_tier(self._data)

    def get_raw_data(self) -> dict:
        return dict(self._data)

    def save(self) -> None:
        self.tier_file.parent.mkdir(parents=True, exist_ok=True)
        self._data["tier"] = self._tier_id
        self.tier_file.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def activate_paid(
        self,
        tier_id: str,
        source: str = "checkout",
        email: str = "",
        name: str = "",
    ) -> dict:
        if tier_id not in TIERS:
            return {"success": False, "message": f"Unknown plan: {tier_id}"}

        self._tier_id = tier_id
        self._data = {
            "tier": tier_id,
            "source": source,
            "subscription_status": "active",
            "activated_at": datetime.now().isoformat(),
            "customer_email": email,
        }
        if name:
            self._data["customer_name"] = name

        self.tier_file.parent.mkdir(parents=True, exist_ok=True)
        self.tier_file.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

        tier = TIERS[tier_id]
        return {
            "success": True,
            "message": (
                f"✓ {tier['name']} plan active — {tier['tagline']}. "
                "Say 'morning brief' or 'show roi' to see your value."
            ),
        }

    @property
    def tier_id(self) -> str:
        return self._tier_id

    def get_tier(self) -> dict:
        tier = TIERS[self._tier_id]
        trial_info = self._trial_info()

        return {
            "id": tier["id"],
            "name": tier["name"],
            "price": tier["price"],
            "price_label": tier["price_label"],
            "tagline": tier["tagline"],
            "agents": sorted(tier["agents"]),
            "features": dict(tier["features"]),
            "upgrade_options": self._upgrade_options(),
            "subscription_status": self._data.get("subscription_status", "free"),
            "trial": trial_info,
        }

    def _trial_info(self) -> dict:
        status = self._data.get("subscription_status", "free")
        if status != "trial":
            return {"active": False}

        trial_ends = self._data.get("trial_ends")
        days = None
        if trial_ends:
            try:
                ends = datetime.fromisoformat(trial_ends)
                delta = ends - datetime.now()
                days = max(0, delta.days + (1 if delta.seconds > 0 else 0))
            except ValueError:
                pass

        return {
            "active": True,
            "days_remaining": days,
            "trial_ends": trial_ends,
            "trial_started": self._data.get("trial_started"),
            "expiring_soon": days is not None and days <= 5,
        }

    def _upgrade_options(self) -> list:
        order = ["cosmic", "campus", "startup", "enterprise"]
        current = order.index(self._tier_id) if self._tier_id in order else 0
        options = []

        for tier_id in order[current + 1:]:
            t = TIERS[tier_id]
            options.append({
                "id": tier_id,
                "name": t["name"],
                "price_label": t["price_label"],
                "tagline": t["tagline"],
                "trial_days": TRIAL_DAYS if tier_id in ("campus", "startup") else 0,
            })

        return options

    def set_tier(self, tier_id: str) -> dict:
        if tier_id not in TIERS:
            return {"success": False, "message": f"Unknown plan: {tier_id}"}

        self._tier_id = tier_id
        self._data["tier"] = tier_id
        self.save()
        tier = TIERS[tier_id]
        return {
            "success": True,
            "message": f"Plan activated: {tier['name']} — {tier['tagline']}",
        }

    def has_feature(self, feature: str) -> bool:
        return TIERS[self._tier_id]["features"].get(feature, False)

    def tier_includes(self, agent_id: str) -> bool:
        return tier_includes_agent(self._tier_id, agent_id)

    def demo_activate(self, tier_id: str) -> dict:
        return self.activate_paid(tier_id, source="demo")


def tier_includes_agent(tier_id: str, agent_id: str) -> bool:
    tier = TIERS.get(tier_id, TIERS["cosmic"])
    return agent_id in tier["agents"]
