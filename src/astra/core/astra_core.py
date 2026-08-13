from astra.core.config.config_manager import ConfigManager
from astra.core.logging.logger import Logger
from astra.core.memory import MemoryManager
from astra.core.context import ContextEngine
from astra.core.intent.intent_engine import IntentEngine
from astra.core.planner.smart_planner import SmartPlanner
from astra.core.planner.routine_store import RoutineStore
from astra.core.planner.scheduler import RoutineScheduler
from astra.core.planner.proactive import ProactiveEngine
from astra.core.reasoning import ReasoningEngine
from astra.core.actions.executor import Executor
from astra.core.permissions import PermissionManager
from astra.core.pipeline import PipelineOrchestrator
from astra.core.bus import EventBus
from astra.core.observability import MetricsCollector
from astra.core.safety import SafetyEngine
from astra.core.tools import ToolManager, register_builtin_tools
from astra.core.knowledge import KnowledgeEngine
from astra.core.knowledge.llm_responder import LLMResponder
from astra.core.plugins import PluginManager
from astra.core.plugins.marketplace import PluginMarketplace
from astra.core.profiles import ProfileManager
from astra.core.learning import LearningEngine
from astra.core.voice import VoiceEngine
from astra.core.session import SessionManager
from astra.core.audit import AuditLogger
from astra.core.os import WindowsLayer
from astra.core.sync import CloudSyncEngine
from astra.core.billing.tiers import TierManager
from astra.core.billing.usage import UsageTracker
from astra.core.billing.roi_engine import ROIEngine
from astra.core.billing.trial_manager import TrialManager
from astra.core.modes.workspace_mode import WorkspaceMode
from astra.core.agents.morning_brief import MorningBriefEngine
from astra.core.revolution.revolution_engine import RevolutionEngine
from astra.core.security.privacy_engine import PrivacyEngine
from astra.core.voice.voice_settings import VoiceSettingsStore
from astra.core.integrations import IntegrationsStore, WeatherEngine, CalendarEngine, LocationEngine


class AstraCore:
    """
    Central service container for all Astra Core modules.
    """

    VERSION = "3.6.0"

    def __init__(self, project_root=None):
        from pathlib import Path

        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config = None
        self.logger = None
        self.memory = None
        self.context = None
        self.intent_engine = None
        self.planner = None
        self.reasoning = None
        self.permissions = None
        self.executor = None
        self.pipeline = None
        self.voice = None
        self.session = SessionManager()
        self.audit = None
        self.learning = LearningEngine()
        self.event_bus = EventBus()
        self.metrics = MetricsCollector()
        self.safety = SafetyEngine()
        self.tools = ToolManager()
        self.knowledge = KnowledgeEngine()
        self.llm_responder = None
        self.plugins = PluginManager(self.project_root / "plugins")
        self.marketplace = PluginMarketplace(self.project_root)
        self.profiles = ProfileManager(self.project_root)
        self.windows = None
        self.cloud_sync = None
        self.routine_store = None
        self.scheduler = None
        self.proactive = None
        self.tiers = None
        self.usage = None
        self.roi = None
        self.trial = None
        self.workspace_mode = None
        self.morning_brief = None
        self.revolution = None
        self.privacy = None
        self.voice_settings = None
        self.integrations = None
        self.weather = None
        self.calendar = None
        self.ready = False
        self.boot_time = None

    def initialize(self, voice_enabled: bool = False) -> None:

        self.config = ConfigManager(self.project_root).load()
        self.config["version"] = self.VERSION

        self.logger = Logger()
        self.logger.info(f"Astra Core {self.VERSION} initializing")

        self.audit = AuditLogger(enabled=self.config.get("audit_enabled", True))

        self.memory = MemoryManager()
        self.context = ContextEngine()
        self.windows = WindowsLayer()
        self.routine_store = RoutineStore(self.project_root)
        self.scheduler = RoutineScheduler(self.project_root)
        self.cloud_sync = CloudSyncEngine(self.memory, self.project_root)

        self.profiles.apply_profile_paths(self)

        if self.config.get("session_persistence", True):
            restored = self.session.restore(self.context)

            if restored:
                self.logger.info("Session restored from previous run")

        self.intent_engine = IntentEngine(
            context_engine=self.context,
            llm_enabled=self.config.get("llm_enabled", False),
        )
        self.llm_responder = LLMResponder(
            enabled=self.config.get("llm_enabled", False),
        )
        self.planner = SmartPlanner(
            routine_store=self.routine_store,
            memory_manager=self.memory,
            llm_enabled=self.config.get("llm_enabled", False),
        )
        self.proactive = ProactiveEngine(self.memory, self.learning)
        self.tiers = TierManager(self.project_root)
        self.usage = UsageTracker(self.project_root)
        self.roi = ROIEngine(self.project_root)
        self.trial = TrialManager(self.project_root, self.tiers)
        self.trial.refresh()
        self.workspace_mode = WorkspaceMode(self.memory, self.tiers)
        self.morning_brief = MorningBriefEngine(self)
        self.revolution = RevolutionEngine(self.project_root)
        self.privacy = PrivacyEngine(self.project_root, self.config, self)
        self.voice_settings = VoiceSettingsStore(self.project_root)
        self.integrations = IntegrationsStore(self.project_root)
        import os
        if os.environ.get("ASTRA_CITY") and not self.integrations.get("city"):
            self.integrations.set_city(os.environ.get("ASTRA_CITY", ""))
            self.integrations._data["location_source"] = "env"
            self.integrations._save(self.integrations._data)
        if os.environ.get("ASTRA_CALENDAR_ICS") and not self.integrations.get("calendar_ics_url"):
            self.integrations.set_calendar_url(os.environ.get("ASTRA_CALENDAR_ICS", ""))
        self.location = LocationEngine(self.integrations)
        self.weather = WeatherEngine(self.integrations, self.location)
        self.calendar = CalendarEngine(self.integrations)
        if self.location.auto_enabled() and not self.integrations.get("city"):
            self.location.detect()
        self.reasoning = ReasoningEngine()
        self.permissions = PermissionManager()
        self.voice = VoiceEngine(enabled=voice_enabled)

        register_builtin_tools(self.tools)

        self.executor = Executor(
            memory_manager=self.memory,
            knowledge_engine=self.knowledge,
            tool_manager=self.tools,
            logger=self.logger,
            windows_layer=self.windows,
            cloud_sync=self.cloud_sync,
            routine_store=self.routine_store,
            scheduler=self.scheduler,
            profile_manager=self.profiles,
            marketplace=self.marketplace,
            plugin_manager=self.plugins,
            core=self,
            llm_responder=self.llm_responder,
        )

        self.pipeline = PipelineOrchestrator(
            intent_engine=self.intent_engine,
            planner=self.planner,
            reasoning_engine=self.reasoning,
            executor=self.executor,
            context_engine=self.context,
            permission_manager=self.permissions,
            safety_engine=self.safety,
            learning_engine=self.learning,
            session_manager=self.session if self.config.get("session_persistence") else None,
            audit_logger=self.audit,
            event_bus=self.event_bus,
            metrics=self.metrics,
            logger=self.logger,
            llm_responder=self.llm_responder,
            memory_manager=self.memory,
            knowledge_engine=self.knowledge,
            tier_manager=self.tiers,
            usage_tracker=self.usage,
            revolution_engine=self.revolution,
            roi_engine=self.roi,
        )

        self._wire_events()
        plugin_count = self.plugins.load_all(self)

        if plugin_count:
            self.logger.info(f"Loaded {plugin_count} plugin(s)")

        if not self.memory.exists("user_name"):
            active = self.profiles.registry["profiles"][self.profiles.active_profile]
            self.memory.remember("user_name", active.get("name", "Cosmic"))

        import time

        self.boot_time = time.time()
        self.ready = True
        self.event_bus.publish("core.ready", {"version": self.VERSION})
        self.logger.info("Astra Core ready")

    def register_plugin_intent(self, intent: str, patterns: tuple, handler) -> None:
        self.intent_engine.register_patterns(intent, patterns)
        self.executor.register_handler(handler)

    def process(self, user_input: str):
        return self.pipeline.process(user_input)

    def shutdown(self) -> None:
        if self.session and self.context:
            self.session.save(self.context)

        if self.logger:
            self.logger.info("Astra Core shutdown")

    def _wire_memory_sync(self) -> None:
        original_remember = self.memory.remember

        def remember_with_sync(key, value):
            original_remember(key, value)
            self.cloud_sync.track_key(key, value)

        self.memory.remember = remember_with_sync

    def _wire_events(self) -> None:

        self.event_bus.subscribe("intent.classified", self._on_intent)
        self.event_bus.subscribe("decision.made", self._on_decision)
        self.event_bus.subscribe("action.completed", self._on_action)

    def _on_intent(self, payload: dict) -> None:
        self.metrics.increment(f"intent.{payload.get('intent', 'unknown')}")

    def _on_decision(self, payload: dict) -> None:
        self.metrics.increment(f"decision.{payload.get('decision', 'unknown')}")

    def _on_action(self, payload: dict) -> None:
        if payload.get("success"):
            self.metrics.increment("actions.success")
        else:
            self.metrics.increment("actions.failure")
