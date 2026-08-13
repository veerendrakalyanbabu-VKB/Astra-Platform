from astra.core.astra_core import AstraCore
from astra.shell.command_bridge import CommandBridge


def test_command_bridge():
    core = AstraCore()
    core.initialize()
    bridge = CommandBridge(core)

    response = bridge.run("what time is it")

    assert response.success
    assert "time" in response.message.lower()

    status = bridge.get_status()
    assert status["version"] == "3.6.0"
