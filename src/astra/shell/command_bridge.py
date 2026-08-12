"""Bridge between Desktop Shell UI and Astra Core pipeline."""

from dataclasses import dataclass, field
from typing import List, Optional

from astra.core.planner.routines import list_routines
from astra.core.planner.workspace import list_workspaces


@dataclass
class ShellResponse:
    message: str
    success: bool
    intent: str = ""
    needs_confirmation: bool = False
    blocked: bool = False
    steps: List[str] = field(default_factory=list)


class CommandBridge:
    """Handles command processing and confirmation flow for the shell."""

    QUICK_ACTIONS = {
        "Time": "what time is it",
        "Memory": "show my memory",
        "Morning": "organize my morning routine",
        "Sync": "sync my memory",
        "Windows": "list windows",
        "Coding WS": "activate coding workspace",
    }

    WINDOWS_ACTIONS = {
        "Focus Notepad": "focus notepad",
        "Volume 50": "set volume 50",
        "Minimize All": "minimize all",
        "System Info": "system info",
    }

    def __init__(self, core):
        self.core = core

    def run(self, text: str) -> ShellResponse:
        text = text.strip()

        if not text:
            return ShellResponse(message="", success=False)

        if self.core.permissions.has_pending():
            return self._handle_confirmation(text)

        result = self.core.process(text)
        steps = self._extract_steps(result.message)

        return ShellResponse(
            message=result.message or "Done.",
            success=result.executed or bool(result.message),
            intent=result.intent.intent,
            needs_confirmation=result.needs_confirmation,
            blocked=result.blocked,
            steps=steps,
        )

    def _handle_confirmation(self, text: str) -> ShellResponse:
        confirmation = self.core.permissions.parse_confirmation(text)

        if confirmation is True:
            result = self.core.pipeline.execute_approved_plan(text)
        elif confirmation is False:
            result = self.core.pipeline.cancel_pending(text)
        else:
            return ShellResponse(
                message="Please answer yes or no to confirm the pending action.",
                success=False,
                needs_confirmation=True,
            )

        return ShellResponse(
            message=result.message or "Done.",
            success=result.executed,
            intent=result.intent.intent,
            steps=self._extract_steps(result.message),
        )

    def create_routine(self, key: str, steps: str) -> ShellResponse:
        return self.run(f"create routine {key}: {steps}")

    def delete_routine(self, key: str) -> ShellResponse:
        return self.run(f"delete routine {key}")

    def run_routine(self, key: str) -> ShellResponse:
        return self.run(f"run {key}")

    def sync_now(self) -> ShellResponse:
        return self.run("sync my memory")

    def activate_workspace(self, name: str) -> ShellResponse:
        return self.run(f"activate {name} workspace")

    def get_routines(self) -> list:
        return list_routines(self.core.routine_store)

    def get_workspaces(self) -> list:
        return list_workspaces()

    def get_schedules(self) -> list:
        return self.core.scheduler.list_all()

    def get_suggestions(self) -> list:
        return self.core.proactive.suggest()

    def get_profiles(self) -> list:
        return self.core.profiles.list_profiles()

    def switch_profile(self, profile_id: str) -> ShellResponse:
        result = self.core.profiles.switch_profile(profile_id, self.core)
        return ShellResponse(message=result["message"], success=result["success"])

    def get_marketplace(self) -> list:
        return self.core.marketplace.list_catalog()

    def install_plugin(self, plugin_id: str) -> ShellResponse:
        result = self.core.marketplace.install(
            plugin_id,
            self.core.plugins,
            self.core,
        )
        return ShellResponse(message=result["message"], success=result["success"])

    def get_sync_status(self) -> dict:
        return self.core.cloud_sync.status()

    def _extract_steps(self, message: str) -> list:
        if not message:
            return []

        steps = []
        for line in message.splitlines():
            line = line.strip()
            if line.startswith("Step "):
                steps.append(line)
        return steps

    def _location_snapshot(self) -> dict:
        location = getattr(self.core, "location", None)
        if not location:
            return {}
        snap = self.core.integrations.snapshot()
        city = (snap.get("city") or "").strip()
        source = snap.get("location_source") or ""
        return {
            "city": city,
            "region": snap.get("region") or "",
            "country": snap.get("country") or "",
            "source": source,
            "auto_enabled": location.auto_enabled(),
            "label": location.format_location_line() if city else "",
        }

    def get_status(self) -> dict:
        config = self.core.config
        learning = self.core.learning.stats()
        metrics = self.core.metrics.snapshot()
        sync = self.core.cloud_sync.status()

        llm_cfg = config.get("llm_config") or {}
        llm_label = llm_cfg.get("llm_label", "Standby")
        llm_active = llm_cfg.get("llm_active", False)

        return {
            "version": self.core.VERSION,
            "user": self.core.memory.recall("user_name") or "User",
            "llm": "Active" if llm_active else "Standby",
            "llm_provider": llm_cfg.get("provider") or "none",
            "llm_label": llm_label,
            "plugins": self.core.plugins.loaded_plugins,
            "memory_count": len(self.core.memory.list_all()),
            "learning_rate": f"{learning['success_rate'] * 100:.0f}%",
            "requests": metrics["counters"].get("pipeline.requests", 0),
            "pending": self.core.permissions.has_pending(),
            "sync_device": sync["device_id"][:8],
            "cloud_sync": "Remote" if sync.get("remote_configured") else "Local",
            "encryption": "Active" if sync.get("encryption_enabled") else "Off",
            "routines": len(self.get_routines()),
            "schedules": len(self.get_schedules()),
            "profile": self.core.profiles.active_profile,
            "marketplace_plugins": len(self.get_marketplace()),
            "hotkey": "Ctrl+Shift+A",
            "privacy": self.core.privacy.snapshot() if self.core.privacy else {},
            "voice_settings": self.core.voice_settings.snapshot() if self.core.voice_settings else {},
            "location": self._location_snapshot(),
        }

    def get_command_dashboard(self) -> dict:
        from astra.core.agents import squad
        from astra.core.billing.stripe_billing import PORTAL_BASE, billing_status

        brief = self.core.morning_brief.generate()
        tier = self.core.tiers.get_tier()
        mode = self.core.workspace_mode.get_info()
        usage = self.core.usage.snapshot(self.core.tiers.tier_id)
        billing = billing_status()
        revolution = self.core.revolution.dashboard(self.core)
        roi = self.core.roi.dashboard()
        trial = self.core.trial.snapshot()
        tier_id = self.core.tiers.tier_id

        voice_prompts = [
            ("CORE", "run industrial revolution"),
            ("NOVA", "summarize AI agent market trends"),
            ("PILOT", "organize my morning routine"),
        ]
        if tier_id in ("campus", "startup", "enterprise") or self.core.tiers.tier_includes("mentor"):
            voice_prompts.append(("MENTOR", "explain recursion for beginners"))

        return {
            "kpis": {
                "automation": revolution["automation_index"],
                "hours_saved": roi["hours_saved_week"],
                "stage": revolution["stage"]["symbol"] + " " + revolution["stage"]["name"],
                "trial_days": trial.get("days_remaining") if trial.get("on_trial") else "—",
            },
            "squad": squad.list_agents(self.core.tiers.tier_id),
            "brief": brief,
            "tier": tier,
            "mode": mode,
            "usage": usage,
            "billing": billing,
            "revolution": revolution,
            "roi": roi,
            "trial": trial,
            "upgrade_url": billing.get("portal_url", PORTAL_BASE),
            "privacy": self.core.privacy.snapshot() if self.core.privacy else {},
            "voice_settings": self.core.voice_settings.snapshot() if self.core.voice_settings else {},
            "voice_prompts": voice_prompts,
            "location": self._location_snapshot(),
        }
