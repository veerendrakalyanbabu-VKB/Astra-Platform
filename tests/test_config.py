import os
from pathlib import Path

from astra.core.config.config_manager import ConfigManager


def test_config_loads_defaults():
    config = ConfigManager().load()

    assert config["app_name"] == "Astra Platform"
    assert config["version"] == "3.5.0"


def test_config_loads_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text('OPENAI_API_KEY=sk-test-key\nASTRA_DEBUG=true\n', encoding="utf-8")

    config = ConfigManager(project_root=tmp_path).load()

    assert os.environ.get("OPENAI_API_KEY") == "sk-test-key"
    assert config["llm_enabled"] is True
    assert config["debug"] is True

    os.environ.pop("OPENAI_API_KEY", None)
