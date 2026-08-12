from pathlib import Path

from astra.core.config.config_manager import ConfigManager
from astra.core.security.privacy_engine import PrivacyEngine


def test_privacy_snapshot(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    config = ConfigManager(project_root=tmp_path).load()
    engine = PrivacyEngine(tmp_path, config)

    snap = engine.snapshot()
    assert snap["local_first"] is True
    assert snap["max_score"] >= 4
    assert len(snap["shields"]) >= 4
    assert "Fortress" in snap["headline"] or "Protected" in snap["headline"]
