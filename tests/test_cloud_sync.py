from astra.core.memory.memory_manager import MemoryManager
from astra.core.sync.cloud_sync import CloudSyncEngine


def _build_sync(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    memory = MemoryManager()
    memory.data_folder = data_dir
    memory.memory_file = data_dir / "memory.json"
    memory.memory_file.write_text("{}", encoding="utf-8")
    memory.memory = memory.load()

    sync = CloudSyncEngine(memory, project_root=tmp_path)
    sync.sync_dir = data_dir / "sync"
    sync.sync_dir.mkdir(parents=True, exist_ok=True)
    sync.meta_file = sync.sync_dir / "sync_meta.json"
    sync.device_file = sync.sync_dir / "device.json"
    sync.bundle_file = sync.sync_dir / "latest_bundle.json"

    return memory, sync


def test_cloud_sync_export_and_import(tmp_path):
    memory, sync = _build_sync(tmp_path)

    memory.remember("favorite_color", "blue")
    sync.track_key("favorite_color", "blue")

    bundle = sync.export_bundle()

    assert "favorite_color" in bundle["memory"]
    assert bundle["memory"]["favorite_color"]["value"] == "blue"

    memory2 = MemoryManager()
    memory2.data_folder = tmp_path / "data2"
    memory2.data_folder.mkdir()
    memory2.memory_file = memory2.data_folder / "memory.json"
    memory2.memory_file.write_text("{}", encoding="utf-8")
    memory2.memory = memory2.load()

    sync2 = CloudSyncEngine(memory2, project_root=tmp_path / "device2")
    sync2.sync_dir = tmp_path / "device2" / "sync"
    sync2.sync_dir.mkdir(parents=True, exist_ok=True)
    sync2.meta_file = sync2.sync_dir / "sync_meta.json"
    sync2.device_file = sync2.sync_dir / "device.json"
    sync2.bundle_file = sync2.sync_dir / "latest_bundle.json"

    result = sync2.import_bundle(bundle)

    assert result["imported"] == 1
    assert memory2.recall("favorite_color") == "blue"


def test_cloud_sync_local_sync(tmp_path):
    memory, sync = _build_sync(tmp_path)

    memory.remember("city", "Austin")
    sync.track_key("city", "Austin")

    result = sync.sync()

    assert result["exported_keys"] == 1
    assert sync.bundle_file.exists()


def test_cloud_sync_status(tmp_path):
    _, sync = _build_sync(tmp_path)

    status = sync.status()

    assert status["device_id"]
    assert status["remote_configured"] is False
