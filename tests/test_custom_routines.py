from astra.core.planner.routine_parser import parse_steps
from astra.core.planner.routine_store import RoutineStore
from astra.core.planner.plan import PlanStep
from astra.core.intent.intents import GET_TIME, OPEN_APP, LIST_MEMORY


def test_parse_routine_steps():
    steps, errors = parse_steps("get time, open notepad, show memory")

    assert not errors
    assert len(steps) == 3
    assert steps[0].action == GET_TIME
    assert steps[1].parameters["application"] == "notepad"


def test_parse_unknown_step():
    _, errors = parse_steps("get time, do magic")

    assert "do magic" in errors


def test_routine_store_save_and_load(tmp_path):
    store = RoutineStore(tmp_path)
    store.store_file = tmp_path / "data" / "routines.json"
    store.data_dir = tmp_path / "data"
    store.data_dir.mkdir(parents=True, exist_ok=True)

    steps = [
        PlanStep(GET_TIME, {}),
        PlanStep(OPEN_APP, {"application": "notepad"}),
        PlanStep(LIST_MEMORY, {}),
    ]
    store.save_routine("myday", "My Day", steps)

    loaded = store.get_routine("myday")

    assert loaded is not None
    assert len(loaded["steps"]) == 3
    assert loaded["title"] == "My Day"


def test_routine_store_delete(tmp_path):
    store = RoutineStore(tmp_path)
    store.store_file = tmp_path / "data" / "routines.json"
    store.data_dir = tmp_path / "data"
    store.data_dir.mkdir(parents=True, exist_ok=True)

    store.save_routine("temp", "Temp", [PlanStep(GET_TIME, {})])
    assert store.delete_routine("temp") is True
    assert store.get_routine("temp") is None
