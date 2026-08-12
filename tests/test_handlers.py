import json

from astra.core.actions.handlers.get_time import GetTimeHandler
from astra.core.actions.handlers.recall_memory import RecallMemoryHandler
from astra.core.actions.handlers.save_memory import SaveMemoryHandler
from astra.core.memory.memory_manager import MemoryManager


def test_get_time_handler():
    handler = GetTimeHandler()
    result = handler.execute({})

    assert result.success is True
    assert "time" in result.data
    assert "formatted" in result.data


def test_save_memory_handler(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    memory_file = data_dir / "memory.json"
    memory_file.write_text("{}", encoding="utf-8")

    manager = MemoryManager()
    manager.data_folder = data_dir
    manager.memory_file = memory_file

    handler = SaveMemoryHandler(manager)
    result = handler.execute({"text": "my favorite color is blue"})

    assert result.success is True
    assert result.data["key"] == "favorite_color"

    stored = json.loads(memory_file.read_text(encoding="utf-8"))
    assert stored["favorite_color"] == "my favorite color is blue"


def test_recall_memory_handler(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    memory_file = data_dir / "memory.json"
    memory_file.write_text(
        '{"favorite_color": "my favorite color is blue"}',
        encoding="utf-8",
    )

    manager = MemoryManager()
    manager.data_folder = data_dir
    manager.memory_file = memory_file
    manager.memory = manager.load()

    handler = RecallMemoryHandler(manager)
    result = handler.execute({"query": "favorite color"})

    assert result.success is True
    assert "blue" in result.message
