from astra.core.actions.executor import Executor
from astra.core.actions.result import ActionResult
from astra.core.context import ContextEngine
from astra.core.intent.intent_engine import IntentEngine
from astra.core.memory.memory_manager import MemoryManager
from astra.core.permissions import PermissionManager
from astra.core.pipeline import PipelineOrchestrator
from astra.core.planner.smart_planner import SmartPlanner
from astra.core.planner.routine_store import RoutineStore
from astra.core.planner.scheduler import RoutineScheduler
from astra.core.reasoning import ReasoningEngine
from astra.core.sync.cloud_sync import CloudSyncEngine


def _build_pipeline(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    memory = MemoryManager()
    memory.data_folder = data_dir
    memory.memory_file = data_dir / "memory.json"
    memory.memory_file.write_text("{}", encoding="utf-8")
    memory.memory = memory.load()

    cloud_sync = CloudSyncEngine(memory, project_root=tmp_path)
    cloud_sync.sync_dir = data_dir / "sync"
    cloud_sync.sync_dir.mkdir(parents=True, exist_ok=True)
    cloud_sync.meta_file = cloud_sync.sync_dir / "sync_meta.json"
    cloud_sync.device_file = cloud_sync.sync_dir / "device.json"
    cloud_sync.bundle_file = cloud_sync.sync_dir / "latest_bundle.json"

    routine_store = RoutineStore(tmp_path)
    routine_store.store_file = data_dir / "routines.json"
    routine_store.data_dir = data_dir

    scheduler = RoutineScheduler(tmp_path)
    scheduler.schedule_file = data_dir / "schedules.json"

    context = ContextEngine()
    permissions = PermissionManager()

    pipeline = PipelineOrchestrator(
        intent_engine=IntentEngine(context_engine=context),
        planner=SmartPlanner(routine_store),
        reasoning_engine=ReasoningEngine(),
        executor=Executor(
            memory_manager=memory,
            cloud_sync=cloud_sync,
            routine_store=routine_store,
            scheduler=scheduler,
            profile_manager=None,
            marketplace=None,
            plugin_manager=None,
            core=None,
        ),
        context_engine=context,
        permission_manager=permissions,
    )

    return pipeline, permissions, context, memory, cloud_sync, routine_store


def test_pipeline_executes_get_time(tmp_path):
    pipeline, _, context, _, _, _ = _build_pipeline(tmp_path)

    result = pipeline.process("What time is it?")

    assert result.executed is True
    assert result.intent.intent == "GET_TIME"
    assert "current time" in result.message.lower()
    assert context.get_state("last_intent") == "GET_TIME"


def test_pipeline_blocks_critical_action(tmp_path):
    pipeline, _, _, _, _, _ = _build_pipeline(tmp_path)

    from astra.core.planner.plan import Plan

    plan = Plan(action="FORMAT_DISK", parameters={"drive": "C:"})
    reasoning = pipeline.reasoning.think(plan)

    assert reasoning["decision"]["decision"] == "BLOCK"


def test_pipeline_unknown_intent(tmp_path):
    pipeline, _, _, _, _, _ = _build_pipeline(tmp_path)

    result = pipeline.process("xyzzy plugh")

    assert result.executed is False
    assert result.intent.intent == "UNKNOWN"


def test_pipeline_confirm_flow(tmp_path):
    pipeline, permissions, _, _, _, _ = _build_pipeline(tmp_path)

    result = pipeline.process("Delete old notes")

    assert result.needs_confirmation is True
    assert permissions.has_pending() is True

    approved = pipeline.execute_approved_plan("yes")

    assert approved.executed is True
    assert permissions.has_pending() is False
    assert "simulated deletion" in approved.message.lower()


def test_pipeline_recall_memory(tmp_path):
    pipeline, _, _, memory, _, _ = _build_pipeline(tmp_path)

    pipeline.process("Remember my favorite color is blue")
    result = pipeline.process("What is my favorite color")

    assert result.executed is True
    assert "blue" in result.message.lower()
    assert memory.recall("favorite_color") is not None


def test_pipeline_runs_goal_plan(tmp_path, monkeypatch):
    pipeline, _, _, _, _, _ = _build_pipeline(tmp_path)

    calls = []

    def fake_execute(plan):
        calls.append(plan.action)
        return ActionResult(success=True, message=f"did {plan.action}")

    monkeypatch.setattr(pipeline.executor, "execute", fake_execute)

    result = pipeline.process("organize my morning routine")

    assert result.executed is True
    assert len(calls) == 3
    assert "Running Morning Routine" in result.message


def test_pipeline_create_and_run_custom_routine(tmp_path, monkeypatch):
    pipeline, _, _, _, _, routine_store = _build_pipeline(tmp_path)

    create = pipeline.process(
        "create routine myday: get time, show memory"
    )
    assert create.executed is True
    assert routine_store.get_routine("myday") is not None

    calls = []

    def fake_execute(plan):
        calls.append(plan.action)
        return ActionResult(success=True, message=f"did {plan.action}")

    monkeypatch.setattr(pipeline.executor, "execute", fake_execute)

    result = pipeline.process("run myday")

    assert result.executed is True
    assert len(calls) == 2

