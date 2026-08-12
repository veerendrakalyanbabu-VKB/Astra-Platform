from astra.core.context import ContextEngine
from astra.core.session import SessionManager


def test_session_save_and_restore(tmp_path):
    session_path = tmp_path / "session.json"
    context = ContextEngine()

    context.remember_conversation("User", "hello")
    context.remember_conversation("Astra", "hi there")
    context.update_state("last_intent", "HELP")

    manager = SessionManager(session_path=session_path)
    manager.save(context)

    restored = ContextEngine()
    manager.restore(restored)

    assert restored.conversation.all()[0]["text"] == "hello"
    assert restored.get_state("last_intent") == "HELP"
