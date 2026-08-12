"""Plugin marketplace — browse and install extensions."""

import json
import shutil
from pathlib import Path


class PluginMarketplace:

    def __init__(self, project_root=None):
        self.project_root = Path(project_root or Path.cwd())
        self.catalog_file = self.project_root / "marketplace" / "catalog.json"
        self.packages_dir = self.project_root / "marketplace" / "packages"
        self.plugins_dir = self.project_root / "plugins"

    def list_catalog(self) -> list:
        catalog = self._load_catalog()
        installed = self._installed_set()
        entries = []

        for plugin_id, meta in catalog.items():
            entries.append({
                "id": plugin_id,
                "name": meta.get("name", plugin_id),
                "description": meta.get("description", ""),
                "version": meta.get("version", "1.0.0"),
                "author": meta.get("author", "Unknown"),
                "installed": plugin_id in installed,
            })

        return entries

    def install(self, plugin_id: str, plugin_manager, core) -> dict:
        plugin_id = plugin_id.lower().strip()
        catalog = self._load_catalog()

        if plugin_id not in catalog:
            return {"success": False, "message": f"Plugin '{plugin_id}' not in marketplace."}

        source = self.packages_dir / f"{plugin_id}.py"

        if not source.exists():
            return {"success": False, "message": f"Package file missing for '{plugin_id}'."}

        target = self.plugins_dir / f"{plugin_id}.py"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

        loaded = plugin_manager.load_one(target, core)

        if not loaded:
            return {"success": False, "message": f"Installed but failed to load '{plugin_id}'."}

        return {
            "success": True,
            "message": f"Installed and loaded plugin '{catalog[plugin_id]['name']}'.",
            "plugin_id": plugin_id,
        }

    def _installed_set(self) -> set:
        if not self.plugins_dir.exists():
            return set()

        return {path.stem for path in self.plugins_dir.glob("*.py") if not path.name.startswith("_")}

    def _load_catalog(self) -> dict:
        if not self.catalog_file.exists():
            return {}

        with open(self.catalog_file, "r", encoding="utf-8") as file:
            return json.load(file)
