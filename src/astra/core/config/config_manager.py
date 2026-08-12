import os
from pathlib import Path

from astra.core.llm.llm_client import resolve_llm_config


class ConfigManager:
    """
    Loads Astra configuration from defaults, .env file, and environment variables.
    """

    DEFAULTS = {
        "app_name": "Astra Platform",
        "version": "3.5.0",
        "voice": True,
        "llm_enabled": True,
        "session_persistence": True,
        "audit_enabled": True,
        "debug": False,
        "cloud_sync_enabled": True,
        "goal_planner_enabled": True,
        "windows_layer_enabled": True,
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.env_path = self.project_root / ".env"

    def load(self) -> dict:
        config = dict(self.DEFAULTS)
        self._load_dotenv()
        self._apply_environment(config)
        return config

    def _load_dotenv(self) -> None:
        if not self.env_path.exists():
            return

        with open(self.env_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                os.environ.setdefault(key, value)

    def _apply_environment(self, config: dict) -> None:
        llm_cfg = resolve_llm_config()
        config.update(llm_cfg)
        config["llm_config"] = llm_cfg
        config["llm_enabled"] = llm_cfg["llm_active"]

        if os.environ.get("ASTRA_DEBUG", "").lower() in ("1", "true", "yes"):
            config["debug"] = True

        if os.environ.get("ASTRA_VOICE", "").lower() in ("0", "false", "no"):
            config["voice"] = False

        if os.environ.get("ASTRA_SYNC_URL"):
            config["cloud_sync_enabled"] = True
            config["cloud_sync_url"] = os.environ.get("ASTRA_SYNC_URL")

        if os.environ.get("ASTRA_SYNC_KEY"):
            config["sync_encryption_enabled"] = True

        if os.environ.get("ASTRA_PRIVACY_MODE", "").lower() == "strict":
            config["cloud_sync_enabled"] = False

        # Back-compat flags
        config["openai_api_key_set"] = llm_cfg["openai_key_set"]
        config["anthropic_api_key_set"] = llm_cfg["anthropic_key_set"]
        config["groq_api_key_set"] = llm_cfg.get("groq_key_set", False)
