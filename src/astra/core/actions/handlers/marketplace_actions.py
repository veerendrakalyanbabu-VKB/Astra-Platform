from typing import Dict

from astra.core.intent.intents import INSTALL_PLUGIN, LIST_MARKETPLACE
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class ListMarketplaceHandler(ActionHandler):

    def __init__(self, marketplace):
        self.marketplace = marketplace

    def can_handle(self, action: str) -> bool:
        return action == LIST_MARKETPLACE

    def execute(self, parameters: Dict) -> ActionResult:
        catalog = self.marketplace.list_catalog()
        lines = ["Plugin Marketplace:"]

        for entry in catalog:
            status = "installed" if entry["installed"] else "available"
            lines.append(
                f"  {entry['id']} ({status}): {entry['name']} — {entry['description']}"
            )

        lines.append("")
        lines.append('Install with: install plugin weather')

        return ActionResult(
            success=True,
            message="\n".join(lines),
            data={"catalog": catalog},
        )


class InstallPluginHandler(ActionHandler):

    def __init__(self, marketplace, plugin_manager, core):
        self.marketplace = marketplace
        self.plugin_manager = plugin_manager
        self.core = core

    def can_handle(self, action: str) -> bool:
        return action == INSTALL_PLUGIN

    def execute(self, parameters: Dict) -> ActionResult:
        plugin_id = parameters.get("plugin", "")

        if not plugin_id:
            return ActionResult(
                success=False,
                message="Usage: install plugin weather",
                error="MISSING_PLUGIN",
            )

        result = self.marketplace.install(plugin_id, self.plugin_manager, self.core)

        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result,
        )
