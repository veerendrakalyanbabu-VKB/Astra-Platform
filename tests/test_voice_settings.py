from pathlib import Path

from astra.core.voice.voice_settings import VoiceSettingsStore


def test_default_assistant_name(tmp_path):
    store = VoiceSettingsStore(tmp_path)
    assert store.assistant_name == "Astra"
    assert "hey astra" in store.launch_phrases()


def test_rename_updates_wake_phrases(tmp_path):
    store = VoiceSettingsStore(tmp_path)
    result = store.set_assistant_name("Nova")
    assert result["success"] is True
    assert store.assistant_name == "Nova"
    assert "hey nova" in store.launch_phrases()
    assert "wake up nova" in store.launch_phrases()


def test_match_wake_modes(tmp_path):
    store = VoiceSettingsStore(tmp_path)
    assert store.match_wake("hey astra what time is it") == "launch"
    assert store.match_wake("goodnight astra") == "sleep"


def test_toggle_wake(tmp_path):
    store = VoiceSettingsStore(tmp_path)
    store.set_wake_enabled(False)
    assert store.match_wake("hey astra") is None
    store.set_wake_enabled(True)
    assert store.match_wake("hey astra") == "launch"
