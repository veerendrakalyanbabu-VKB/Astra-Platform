from astra.core.planner.plan import Plan
from astra.core.actions.registry import ActionRegistry
from astra.core.actions.result import ActionResult


class Executor:

    def __init__(
        self,
        memory_manager=None,
        knowledge_engine=None,
        tool_manager=None,
        logger=None,
        windows_layer=None,
        cloud_sync=None,
        routine_store=None,
        scheduler=None,
        profile_manager=None,
        marketplace=None,
        plugin_manager=None,
        core=None,
        llm_responder=None,
    ):

        self.logger = logger
        self.registry = ActionRegistry()

        from astra.core.os import WindowsLayer
        from astra.core.actions.handlers import (
            OpenAppHandler,
            SaveMemoryHandler,
            RecallMemoryHandler,
            ListMemoryHandler,
            GetTimeHandler,
            AskKnowledgeHandler,
            CalculateHandler,
            HelpHandler,
            DeleteFileHandler,
            ShutdownHandler,
            RunGoalHandler,
            SyncMemoryHandler,
        )
        from astra.core.actions.handlers.os_actions import (
            SystemInfoHandler,
            OpenFolderHandler,
            CopyClipboardHandler,
            GetClipboardHandler,
            FocusWindowHandler,
            SetVolumeHandler,
            MinimizeAllHandler,
            ListWindowsHandler,
        )
        from astra.core.actions.handlers.routine_actions import (
            CreateRoutineHandler,
            ListRoutinesHandler,
            DeleteRoutineHandler,
        )
        from astra.core.actions.handlers.schedule_routine import (
            ScheduleRoutineHandler,
            ListSchedulesHandler,
        )
        from astra.core.actions.handlers.profile_actions import (
            ListProfilesHandler,
            CreateProfileHandler,
            SwitchProfileHandler,
            WhoAmIHandler,
        )
        from astra.core.actions.handlers.marketplace_actions import (
            ListMarketplaceHandler,
            InstallPluginHandler,
        )

        if windows_layer is None:
            windows_layer = WindowsLayer()

        self.registry.register(OpenAppHandler(windows_layer))
        self.registry.register(GetTimeHandler())
        self.registry.register(HelpHandler())
        self.registry.register(DeleteFileHandler())
        self.registry.register(ShutdownHandler())
        self.registry.register(RunGoalHandler())
        self.registry.register(SystemInfoHandler(windows_layer))
        self.registry.register(OpenFolderHandler(windows_layer))
        self.registry.register(CopyClipboardHandler(windows_layer))
        self.registry.register(GetClipboardHandler(windows_layer))
        self.registry.register(FocusWindowHandler(windows_layer))
        self.registry.register(SetVolumeHandler(windows_layer))
        self.registry.register(MinimizeAllHandler(windows_layer))
        self.registry.register(ListWindowsHandler(windows_layer))

        if cloud_sync:
            self.registry.register(SyncMemoryHandler(cloud_sync))

        if routine_store:
            self.registry.register(CreateRoutineHandler(routine_store))
            self.registry.register(ListRoutinesHandler(routine_store))
            self.registry.register(DeleteRoutineHandler(routine_store))

        if scheduler:
            self.registry.register(ScheduleRoutineHandler(scheduler))
            self.registry.register(ListSchedulesHandler(scheduler))

        if profile_manager and core:
            self.registry.register(ListProfilesHandler(profile_manager))
            self.registry.register(CreateProfileHandler(profile_manager))
            self.registry.register(SwitchProfileHandler(profile_manager, core))
            self.registry.register(WhoAmIHandler(profile_manager, memory_manager))

        if marketplace and plugin_manager and core:
            self.registry.register(ListMarketplaceHandler(marketplace))
            self.registry.register(InstallPluginHandler(marketplace, plugin_manager, core))

        if knowledge_engine:
            self.registry.register(AskKnowledgeHandler(knowledge_engine, llm_responder))

        if tool_manager:
            self.registry.register(CalculateHandler(tool_manager))

        if memory_manager:
            self.registry.register(SaveMemoryHandler(memory_manager))
            self.registry.register(RecallMemoryHandler(memory_manager))
            self.registry.register(ListMemoryHandler(memory_manager))

        if core:
            from astra.core.actions.handlers.command_os_actions import (
                MorningBriefHandler,
                AskAgentHandler,
                SetModeHandler,
                ShowPlansHandler,
                ShowSquadHandler,
                ActivatePlanHandler,
                RevolutionStatusHandler,
                RunProtocolHandler,
                ShowROIHandler,
                StartTrialHandler,
            )

            self.registry.register(MorningBriefHandler(core))
            self.registry.register(AskAgentHandler(core))
            self.registry.register(SetModeHandler(core.workspace_mode))
            self.registry.register(ShowPlansHandler(core.tiers))
            self.registry.register(ShowSquadHandler(core.tiers))
            self.registry.register(ActivatePlanHandler(core.tiers))
            self.registry.register(RevolutionStatusHandler(core))
            self.registry.register(RunProtocolHandler(core))
            self.registry.register(ShowROIHandler(core))
            self.registry.register(StartTrialHandler(core))

            from astra.core.actions.handlers.voice_settings_actions import (
                ShowVoiceSettingsHandler,
                SetAssistantNameHandler,
                SetWakePhraseHandler,
                ToggleWakeWordHandler,
            )

            if core.voice_settings:
                self.registry.register(ShowVoiceSettingsHandler(core.voice_settings))
                self.registry.register(SetAssistantNameHandler(core.voice_settings))
                self.registry.register(SetWakePhraseHandler(core.voice_settings))
                self.registry.register(ToggleWakeWordHandler(core.voice_settings))

            from astra.core.actions.handlers.integration_actions import (
                ShowWeatherHandler,
                ShowCalendarHandler,
                ConnectCalendarHandler,
                SetCityHandler,
                FocusTimerHandler,
                DetectLocationHandler,
            )

            if core.integrations and core.weather and core.calendar:
                self.registry.register(ShowWeatherHandler(core.weather))
                self.registry.register(ShowCalendarHandler(core.calendar))
                self.registry.register(ConnectCalendarHandler(core.integrations))
                self.registry.register(SetCityHandler(core.integrations, memory_manager))
                self.registry.register(FocusTimerHandler(core.integrations, memory_manager))
                if getattr(core, "location", None):
                    self.registry.register(DetectLocationHandler(core.location, memory_manager))

    def register_handler(self, handler) -> None:
        self.registry.register(handler)

    def execute(self, plan: Plan) -> ActionResult:

        handler = self.registry.get_handler(plan.action)

        if not handler:
            result = ActionResult(
                success=False,
                message=f"No handler registered for action '{plan.action}'.",
                error="HANDLER_NOT_FOUND",
            )
            self._log_result(plan.action, result)
            return result

        result = handler.execute(plan.parameters)
        self._log_result(plan.action, result)
        return result

    def _log_result(self, action: str, result: ActionResult) -> None:

        if not self.logger:
            return

        if result.success:
            self.logger.info(f"Action {action} succeeded: {result.message}")
        else:
            self.logger.error(f"Action {action} failed: {result.error or result.message}")
