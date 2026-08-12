from typing import Dict

from astra.core.intent.intents import CREATE_PROFILE, LIST_PROFILES, SWITCH_PROFILE, WHO_AM_I
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class ListProfilesHandler(ActionHandler):

    def __init__(self, profile_manager):
        self.profiles = profile_manager

    def can_handle(self, action: str) -> bool:
        return action == LIST_PROFILES

    def execute(self, parameters: Dict) -> ActionResult:
        entries = self.profiles.list_profiles()
        lines = ["Profiles:"]

        for entry in entries:
            marker = " (active)" if entry["active"] else ""
            lines.append(f"  {entry['id']}: {entry['name']}{marker}")

        lines.append("")
        lines.append('Switch with: switch profile guest')

        return ActionResult(success=True, message="\n".join(lines), data={"profiles": entries})


class CreateProfileHandler(ActionHandler):

    def __init__(self, profile_manager):
        self.profiles = profile_manager

    def can_handle(self, action: str) -> bool:
        return action == CREATE_PROFILE

    def execute(self, parameters: Dict) -> ActionResult:
        name = parameters.get("name", "")

        if not name:
            return ActionResult(
                success=False,
                message="Usage: create profile guest",
                error="MISSING_NAME",
            )

        result = self.profiles.create_profile(name)

        return ActionResult(
            success=result["created"],
            message=result["message"],
            data=result,
        )


class SwitchProfileHandler(ActionHandler):

    def __init__(self, profile_manager, core):
        self.profiles = profile_manager
        self.core = core

    def can_handle(self, action: str) -> bool:
        return action == SWITCH_PROFILE

    def execute(self, parameters: Dict) -> ActionResult:
        profile_id = parameters.get("profile", "")

        if not profile_id:
            return ActionResult(
                success=False,
                message="Usage: switch profile guest",
                error="MISSING_PROFILE",
            )

        result = self.profiles.switch_profile(profile_id, self.core)

        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result,
        )


class WhoAmIHandler(ActionHandler):

    def __init__(self, profile_manager, memory_manager):
        self.profiles = profile_manager
        self.memory = memory_manager

    def can_handle(self, action: str) -> bool:
        return action == WHO_AM_I

    def execute(self, parameters: Dict) -> ActionResult:
        profile_id = self.profiles.active_profile
        display_name = self.memory.recall("user_name") or profile_id

        return ActionResult(
            success=True,
            message=f"You are {display_name} (profile: {profile_id}).",
            data={"profile_id": profile_id, "name": display_name},
        )
