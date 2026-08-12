import json
from pathlib import Path
from typing import Callable, Dict, List, Optional


class ToolManager:
    """
    Registers and dispatches external tools and capabilities.
    """

    def __init__(self):
        self._tools: Dict[str, dict] = {}

    def register(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        parameters: dict = None,
    ) -> None:
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "handler": handler,
        }

    def invoke(self, name: str, parameters: dict = None) -> dict:
        tool = self._tools.get(name)

        if not tool:
            return {
                "success": False,
                "error": f"Tool '{name}' not found.",
            }

        try:
            result = tool["handler"](parameters or {})
            return {
                "success": True,
                "result": result,
            }
        except Exception as error:
            return {
                "success": False,
                "error": str(error),
            }

    def list_tools(self) -> List[dict]:
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            }
            for tool in self._tools.values()
        ]

    def has_tool(self, name: str) -> bool:
        return name in self._tools


def register_builtin_tools(tool_manager: ToolManager) -> None:
    """Register core built-in tools."""

    def calculator(params):
        expression = params.get("expression", "0")
        allowed = set("0123456789+-*/(). ")

        if not set(expression) <= allowed:
            raise ValueError("Invalid characters in expression.")

        return {"expression": expression, "result": eval(expression, {"__builtins__": {}}, {})}

    def echo(params):
        return {"message": params.get("message", "")}

    tool_manager.register(
        "calculator",
        calculator,
        description="Evaluate a basic math expression.",
        parameters={"expression": "string"},
    )

    tool_manager.register(
        "echo",
        echo,
        description="Echo back a message.",
        parameters={"message": "string"},
    )
