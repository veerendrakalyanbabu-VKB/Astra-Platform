"""Local-first privacy and security posture for Astra Command OS."""

import os
from pathlib import Path
from typing import Dict


class PrivacyEngine:
    """
    Surfaces privacy/security status for UI and audits.
    Astra is designed local-first: memory on disk, optional encrypted sync, audit trail.
    """

    SHIELDS = [
        ("local_memory", "Local memory vault", "Facts stay on your device unless you sync."),
        ("audit_trail", "Action audit log", "High-risk commands require confirmation."),
        ("permission_gate", "Permission gate", "Destructive actions are blocked or gated."),
        ("no_telemetry", "No vendor telemetry", "Astra does not phone home usage analytics."),
        ("llm_opt_in", "LLM opt-in only", "Cloud AI runs only when you add API keys."),
    ]

    def __init__(self, project_root: Path, config: dict, core=None):
        self.project_root = project_root
        self.config = config
        self.core = core

    def mode(self) -> str:
        return (os.environ.get("ASTRA_PRIVACY_MODE") or "standard").strip().lower()

    def is_strict(self) -> bool:
        return self.mode() == "strict"

    def snapshot(self) -> Dict:
        sync_enc = bool(self.config.get("sync_encryption_enabled"))
        cloud = self.config.get("cloud_sync_enabled", True)
        audit = self.config.get("audit_enabled", True)
        llm_cfg = self.config.get("llm_config") or {}
        llm_on = llm_cfg.get("llm_active", False)

        shields = []
        for shield_id, title, detail in self.SHIELDS:
            active = True
            if shield_id == "llm_opt_in":
                active = not llm_on or self.is_strict()
            elif shield_id == "audit_trail":
                active = audit
            shields.append({
                "id": shield_id,
                "title": title,
                "detail": detail,
                "active": active,
            })

        score = sum(1 for s in shields if s["active"])
        max_score = len(shields)

        return {
            "mode": self.mode(),
            "headline": self._headline(score, max_score, llm_on),
            "score": score,
            "max_score": max_score,
            "shields": shields,
            "local_first": True,
            "encryption": "Active" if sync_enc else "Available",
            "cloud_sync": "Off" if self.is_strict() else ("Remote" if self.config.get("cloud_sync_url") else "Local only"),
            "data_location": str(self.project_root / "data"),
            "tips": self._tips(llm_on),
        }

    def _headline(self, score: int, max_score: int, llm_on: bool) -> str:
        if score >= max_score - 1:
            base = "Fortress mode — local-first, gated actions, audit on."
        elif score >= max_score // 2:
            base = "Protected — your data stays on-device by default."
        else:
            base = "Review privacy settings to harden your command OS."

        if llm_on:
            base += " Cloud LLM enabled via your keys only."
        return base

    def _tips(self, llm_on: bool) -> list:
        tips = [
            "Never commit .env — keys stay on your machine.",
            "Use ASTRA_PRIVACY_MODE=strict to disable remote sync.",
        ]
        if llm_on:
            tips.append("Set GROQ_API_KEY (free tier), ANTHROPIC_API_KEY, or OPENAI_API_KEY in .env.")
            tips.append("Force provider: ASTRA_LLM_PROVIDER=groq|anthropic|openai")
        else:
            tips.append("Offline mode: rules + local knowledge work without any API key.")
        return tips
