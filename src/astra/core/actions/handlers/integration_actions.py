from typing import Dict

from astra.core.intent.intents import (
    SHOW_WEATHER,
    SHOW_CALENDAR,
    CONNECT_CALENDAR,
    SET_CITY,
    FOCUS_TIMER,
    DETECT_LOCATION,
)
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class ShowWeatherHandler(ActionHandler):

    def __init__(self, weather_engine):
        self.weather = weather_engine

    def can_handle(self, action: str) -> bool:
        return action == SHOW_WEATHER

    def execute(self, parameters: Dict) -> ActionResult:
        snap = self.weather.current()
        return ActionResult(success=snap["available"], message=snap["message"], data=snap)


class ShowCalendarHandler(ActionHandler):

    def __init__(self, calendar_engine):
        self.calendar = calendar_engine

    def can_handle(self, action: str) -> bool:
        return action == SHOW_CALENDAR

    def execute(self, parameters: Dict) -> ActionResult:
        snap = self.calendar.today_events()
        return ActionResult(success=snap["available"], message=snap["message"], data=snap)


class ConnectCalendarHandler(ActionHandler):

    def __init__(self, integrations_store):
        self.settings = integrations_store

    def can_handle(self, action: str) -> bool:
        return action == CONNECT_CALENDAR

    def execute(self, parameters: Dict) -> ActionResult:
        url = parameters.get("url", "")
        result = self.settings.set_calendar_url(url)
        return ActionResult(success=result["success"], message=result["message"])


class SetCityHandler(ActionHandler):

    def __init__(self, integrations_store, memory_manager=None):
        self.settings = integrations_store
        self.memory = memory_manager

    def can_handle(self, action: str) -> bool:
        return action == SET_CITY

    def execute(self, parameters: Dict) -> ActionResult:
        city = parameters.get("city", "")
        result = self.settings.set_city(city)
        if result["success"] and self.memory:
            self.memory.save("city", city)
        return ActionResult(success=result["success"], message=result["message"])


class FocusTimerHandler(ActionHandler):

    def __init__(self, integrations_store, memory_manager):
        self.settings = integrations_store
        self.memory = memory_manager

    def can_handle(self, action: str) -> bool:
        return action == FOCUS_TIMER

    def execute(self, parameters: Dict) -> ActionResult:
        minutes = int(parameters.get("minutes", 25))
        minutes = max(5, min(minutes, 120))
        self.settings._data["focus_minutes"] = minutes
        self.settings._save(self.settings._data)
        if self.memory:
            self.memory.save("focus_timer_minutes", str(minutes))
        return ActionResult(
            success=True,
            message=(
                f"Focus block: {minutes} minutes. "
                "Say activate focus workspace to lock in."
            ),
        )


class DetectLocationHandler(ActionHandler):

    def __init__(self, location_engine, memory_manager=None):
        self.location = location_engine
        self.memory = memory_manager

    def can_handle(self, action: str) -> bool:
        return action == DETECT_LOCATION

    def execute(self, parameters: Dict) -> ActionResult:
        result = self.location.detect(force=True)
        if result.get("success") and self.memory and result.get("city"):
            self.memory.save("city", result["city"])
        return ActionResult(
            success=result.get("success", False),
            message=result.get("message", "Location detection failed."),
            data=result,
        )
