import shutil
from pathlib import Path

from astra.core.plugins.marketplace import PluginMarketplace
from astra.core.plugins.plugin_manager import PluginManager


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _setup_marketplace(tmp_path):
    destination = tmp_path / "marketplace"
    shutil.copytree(PROJECT_ROOT / "marketplace", destination)
    return PluginMarketplace(tmp_path)


def test_marketplace_catalog(tmp_path):
    marketplace = _setup_marketplace(tmp_path)
    catalog = marketplace.list_catalog()

    assert len(catalog) >= 3
    assert any(entry["id"] == "weather" for entry in catalog)


def test_marketplace_install(tmp_path):
    marketplace = _setup_marketplace(tmp_path)
    plugins = PluginManager(tmp_path / "plugins")
    plugins.plugins_dir.mkdir(parents=True, exist_ok=True)

    core = type("Core", (), {})()
    core.logger = None
    core.register_plugin_intent = lambda intent, patterns, handler: None

    result = marketplace.install("quotes", plugins, core)

    assert result["success"] is True
    assert (tmp_path / "plugins" / "quotes.py").exists()
    assert "quotes" in plugins.loaded_plugins
