from astra.core.astra_core import AstraCore


def test_greet_plugin_via_core():
    core = AstraCore()
    core.initialize()

    assert "greet" in core.plugins.loaded_plugins

    result = core.process("hello astra")

    assert result.executed is True
    assert "plugin" in result.message.lower()
