from typing import Dict

from astra.core.intent.intents import SHOW_VOICE_SETTINGS, SET_ASSISTANT_NAME, SET_WAKE_PHRASE, TOGGLE_WAKE_WORD
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class ShowVoiceSettingsHandler(ActionHandler):

    def __init__(self, voice_settings):
        self.settings = voice_settings

    def can_handle(self, action: str) -> bool:
        return action == SHOW_VOICE_SETTINGS

    def execute(self, parameters: Dict) -> ActionResult:
        return ActionResult(success=True, message=self.settings.format_status())


class SetAssistantNameHandler(ActionHandler):

    def __init__(self, voice_settings):
        self.settings = voice_settings

    def can_handle(self, action: str) -> bool:
        return action == SET_ASSISTANT_NAME

    def execute(self, parameters: Dict) -> ActionResult:
        name = parameters.get("name", "")
        result = self.settings.set_assistant_name(name)
        return ActionResult(success=result["success"], message=result["message"])


class SetWakePhraseHandler(ActionHandler):

    def __init__(self, voice_settings):
        self.settings = voice_settings

    def can_handle(self, action: str) -> bool:
        return action == SET_WAKE_PHRASE

    def execute(self, parameters: Dict) -> ActionResult:
        phrase = parameters.get("phrase", "")
        mode = parameters.get("mode", "chat")
        result = self.settings.add_wake_phrase(phrase, mode)
        return ActionResult(success=result["success"], message=result["message"])


class ToggleWakeWordHandler(ActionHandler):

    def __init__(self, voice_settings):
        self.settings = voice_settings

    def can_handle(self, action: str) -> bool:
        return action == TOGGLE_WAKE_WORD

    def execute(self, parameters: Dict) -> ActionResult:
        enabled = parameters.get("enabled", True)
        result = self.settings.set_wake_enabled(enabled)
        return ActionResult(success=result["success"], message=result["message"])
