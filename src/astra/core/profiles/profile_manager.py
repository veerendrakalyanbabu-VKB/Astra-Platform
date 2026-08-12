"""Multi-user profile management with isolated data storage."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", name.lower().strip())
    return slug.strip("_") or "user"


class ProfileManager:

    def __init__(self, project_root=None):
        self.project_root = Path(project_root or Path.cwd())
        self.data_dir = self.project_root / "data"
        self.registry_file = self.data_dir / "profiles.json"
        self.users_root = self.data_dir / "users"
        self.users_root.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()
        self._ensure_default_profile()

    @property
    def active_profile(self) -> str:
        return self.registry.get("active", "cosmic")

    def list_profiles(self) -> list:
        profiles = self.registry.get("profiles", {})
        return [
            {
                "id": profile_id,
                "name": meta.get("name", profile_id),
                "active": profile_id == self.active_profile,
                "created_at": meta.get("created_at"),
            }
            for profile_id, meta in profiles.items()
        ]

    def create_profile(self, name: str) -> dict:
        profile_id = _slug(name)

        if profile_id in self.registry.get("profiles", {}):
            return {"id": profile_id, "created": False, "message": "Profile already exists."}

        profile_dir = self.get_profile_dir(profile_id)
        profile_dir.mkdir(parents=True, exist_ok=True)

        self.registry.setdefault("profiles", {})[profile_id] = {
            "name": name.strip() or profile_id.title(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_registry()

        return {"id": profile_id, "created": True, "message": f"Profile '{profile_id}' created."}

    def switch_profile(self, profile_id: str, core) -> dict:
        profile_id = _slug(profile_id)

        if profile_id not in self.registry.get("profiles", {}):
            return {"success": False, "message": f"Profile '{profile_id}' not found."}

        if profile_id == self.active_profile:
            return {"success": True, "message": f"Already using profile '{profile_id}'."}

        if core.session and core.context:
            core.session.save(core.context)

        self.registry["active"] = profile_id
        self._save_registry()
        self.apply_profile_paths(core)

        core.context.reset()

        if core.config.get("session_persistence", True):
            core.session.restore(core.context)

        display_name = self.registry["profiles"][profile_id].get("name", profile_id)
        core.memory.remember("user_name", display_name)

        return {
            "success": True,
            "message": f"Switched to profile '{display_name}'.",
            "profile_id": profile_id,
        }

    def apply_profile_paths(self, core) -> None:
        profile_dir = self.get_profile_dir(self.active_profile)
        profile_dir.mkdir(parents=True, exist_ok=True)

        core.memory.reconfigure(profile_dir)
        core.session.reconfigure(profile_dir / "session.json")
        core.routine_store.reconfigure(profile_dir)
        core.scheduler.reconfigure(profile_dir)
        core.learning.reconfigure(profile_dir / "learning.json")
        core.cloud_sync.reconfigure(profile_dir / "sync")
        core._wire_memory_sync()

    def get_profile_dir(self, profile_id: str = None) -> Path:
        profile_id = profile_id or self.active_profile
        return self.users_root / profile_id

    def _ensure_default_profile(self) -> None:
        profiles = self.registry.setdefault("profiles", {})

        if "cosmic" not in profiles:
            profiles["cosmic"] = {
                "name": "Cosmic",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self.registry["active"] = "cosmic"
            self._save_registry()

        self.get_profile_dir("cosmic").mkdir(parents=True, exist_ok=True)

    def _load_registry(self) -> dict:
        if not self.registry_file.exists():
            return {"active": "cosmic", "profiles": {}}

        with open(self.registry_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def _save_registry(self) -> None:
        with open(self.registry_file, "w", encoding="utf-8") as file:
            json.dump(self.registry, file, indent=2)
