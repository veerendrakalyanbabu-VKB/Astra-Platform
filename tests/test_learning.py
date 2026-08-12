from astra.core.learning import LearningEngine


def test_learning_record_and_stats(tmp_path):
    path = tmp_path / "learning.json"
    engine = LearningEngine(learning_path=path)

    engine.record("open chrome", "OPEN_APP", True, "Launched chrome.")
    engine.record("bad command", "UNKNOWN", False, "Not understood.")

    stats = engine.stats()

    assert stats["total"] == 2
    assert stats["success_rate"] == 0.5
    assert stats["top_intents"]["OPEN_APP"] == 1
