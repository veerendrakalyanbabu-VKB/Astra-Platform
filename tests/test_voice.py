from astra.core.voice import VoiceEngine


def test_voice_engine_status():
    engine = VoiceEngine(enabled=False)

    assert engine.ready is False

    status = engine.status()

    assert status["enabled"] is False
    assert status["tts_engine"] == "none"
