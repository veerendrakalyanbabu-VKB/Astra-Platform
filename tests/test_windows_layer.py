from unittest.mock import MagicMock, patch

from astra.core.os.windows_layer import WindowsLayer


def test_windows_system_info():
    windows = WindowsLayer()
    result = windows.system_info()

    assert result["success"] is True
    assert "OS:" in result["message"]
    assert result["data"]["os"]


def test_windows_open_folder_not_found():
    windows = WindowsLayer()
    result = windows.open_folder("nonexistent_folder_xyz")

    assert result["success"] is False


@patch("astra.core.os.windows_layer.WindowsLayer._set_clipboard")
def test_windows_copy_clipboard(mock_clipboard):
    mock_clipboard.return_value = None
    windows = WindowsLayer()

    result = windows.copy_to_clipboard("hello astra")

    assert result["success"] is True
    assert "hello astra" in result["message"]


@patch("astra.core.os.windows_layer.subprocess.Popen")
def test_windows_launch_app(mock_popen):
    mock_popen.return_value = MagicMock()
    windows = WindowsLayer()

    result = windows.launch_app("notepad")

    assert result["success"] is True
    assert "Launched notepad" in result["message"]


@patch("astra.core.os.windows_layer.subprocess.run")
def test_windows_minimize_all(mock_run):
    mock_run.return_value = MagicMock(stdout="minimized\n")
    windows = WindowsLayer()

    result = windows.minimize_all()

    assert result["success"] is True
    assert "minimized" in result["message"].lower()


@patch("astra.core.os.windows_layer.subprocess.run")
def test_windows_list_windows(mock_run):
    mock_run.return_value = MagicMock(stdout="notepad: Untitled - Notepad\n")
    windows = WindowsLayer()

    result = windows.list_windows()

    assert result["success"] is True
    assert "notepad" in result["message"].lower()
