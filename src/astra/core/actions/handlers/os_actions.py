from typing import Dict

from astra.core.intent.intents import (
    COPY_CLIPBOARD,
    FOCUS_WINDOW,
    GET_CLIPBOARD,
    LIST_WINDOWS,
    MINIMIZE_ALL,
    OPEN_FOLDER,
    SET_VOLUME,
    SYSTEM_INFO,
)
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class SystemInfoHandler(ActionHandler):

    def __init__(self, windows_layer):
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == SYSTEM_INFO

    def execute(self, parameters: Dict) -> ActionResult:
        result = self.windows.system_info()
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )


class OpenFolderHandler(ActionHandler):

    def __init__(self, windows_layer):
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == OPEN_FOLDER

    def execute(self, parameters: Dict) -> ActionResult:
        folder = parameters.get("folder", "")
        result = self.windows.open_folder(folder)
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )


class CopyClipboardHandler(ActionHandler):

    def __init__(self, windows_layer):
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == COPY_CLIPBOARD

    def execute(self, parameters: Dict) -> ActionResult:
        result = self.windows.copy_to_clipboard(parameters.get("text", ""))
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )


class GetClipboardHandler(ActionHandler):

    def __init__(self, windows_layer):
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == GET_CLIPBOARD

    def execute(self, parameters: Dict) -> ActionResult:
        result = self.windows.get_clipboard()
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )


class FocusWindowHandler(ActionHandler):

    def __init__(self, windows_layer):
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == FOCUS_WINDOW

    def execute(self, parameters: Dict) -> ActionResult:
        result = self.windows.focus_window(parameters.get("application", ""))
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )


class SetVolumeHandler(ActionHandler):

    def __init__(self, windows_layer):
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == SET_VOLUME

    def execute(self, parameters: Dict) -> ActionResult:
        level = parameters.get("level", 50)
        result = self.windows.set_volume(level)
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )


class MinimizeAllHandler(ActionHandler):

    def __init__(self, windows_layer):
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == MINIMIZE_ALL

    def execute(self, parameters: Dict) -> ActionResult:
        result = self.windows.minimize_all()
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )


class ListWindowsHandler(ActionHandler):

    def __init__(self, windows_layer):
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == LIST_WINDOWS

    def execute(self, parameters: Dict) -> ActionResult:
        result = self.windows.list_windows()
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )
