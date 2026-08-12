from astra.core.pipeline.compound import split_compound_command
from astra.core.actions.executor import Executor
from astra.core.context import ContextEngine
from astra.core.intent.intent_engine import IntentEngine
from astra.core.memory.memory_manager import MemoryManager
from astra.core.permissions import PermissionManager
from astra.core.pipeline import PipelineOrchestrator
from astra.core.actions.result import ActionResult
from astra.core.planner.goal_planner import GoalPlanner
from astra.core.reasoning import ReasoningEngine


def test_split_compound():
    parts = split_compound_command("open notepad and remember my snack is chips")

    assert len(parts) == 2
    assert parts[0] == "open notepad"
    assert "remember" in parts[1]


def test_compound_pipeline(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    memory = MemoryManager()
    memory.data_folder = data_dir
    memory.memory_file = data_dir / "memory.json"
    memory.memory_file.write_text("{}", encoding="utf-8")

    context = ContextEngine()
    pipeline = PipelineOrchestrator(
        intent_engine=IntentEngine(context_engine=context),
        planner=GoalPlanner(),
        reasoning_engine=ReasoningEngine(),
        executor=Executor(memory_manager=memory),
        context_engine=context,
        permission_manager=PermissionManager(),
    )

    result = pipeline.process("open notepad and remember my snack is chips")

    assert result.executed is True
    assert "Then" in result.message
    assert memory.recall("snack") is not None
