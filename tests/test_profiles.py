from astra.core.profiles.profile_manager import ProfileManager
from astra.core.astra_core import AstraCore


def test_profile_create_and_switch(tmp_path):
    profiles = ProfileManager(tmp_path)
    profiles.registry_file = tmp_path / "data" / "profiles.json"
    profiles.data_dir = tmp_path / "data"
    profiles.users_root = tmp_path / "data" / "users"
    profiles.users_root.mkdir(parents=True, exist_ok=True)
    profiles.registry = {"active": "cosmic", "profiles": {"cosmic": {"name": "Cosmic"}}}

    created = profiles.create_profile("Guest User")
    assert created["created"] is True

    core = AstraCore(project_root=tmp_path)
    core.initialize()

    core.profiles = profiles
    result = profiles.switch_profile("guest_user", core)

    assert result["success"] is True
    assert profiles.active_profile == "guest_user"


def test_profile_list(tmp_path):
    profiles = ProfileManager(tmp_path)
    profiles.registry_file = tmp_path / "data" / "profiles.json"
    profiles.data_dir = tmp_path / "data"
    profiles.users_root = tmp_path / "data" / "users"
    profiles.users_root.mkdir(parents=True, exist_ok=True)

    entries = profiles.list_profiles()
    assert any(entry["id"] == "cosmic" for entry in entries)
