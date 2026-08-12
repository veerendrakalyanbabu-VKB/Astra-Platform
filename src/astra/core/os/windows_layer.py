"""Native Windows integration layer for Astra."""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional


APP_ALIASES = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "calculator": "calc",
    "calc": "calc",
    "notepad": "notepad",
    "visual studio code": "code",
    "vscode": "code",
    "code": "code",
}

WINDOWS_PATHS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "code": [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
}

FOLDER_ALIASES = {
    "downloads": os.path.expanduser("~/Downloads"),
    "documents": os.path.expanduser("~/Documents"),
    "desktop": os.path.expanduser("~/Desktop"),
    "home": os.path.expanduser("~"),
}


class WindowsLayer:
    """Centralizes Windows OS operations."""

    def launch_app(self, application: str) -> Dict:
        application = application.strip().lower()

        if not application:
            return {
                "success": False,
                "message": "No application specified.",
                "error": "MISSING_APPLICATION",
            }

        target = APP_ALIASES.get(application, application)
        launch_target = self._resolve_app_target(target)

        if not launch_target:
            return {
                "success": False,
                "message": f"Could not launch {application}.",
                "error": "APP_NOT_FOUND",
            }

        try:
            subprocess.Popen([launch_target], shell=False)
            return {
                "success": True,
                "message": f"Launched {application}.",
                "data": {"application": application, "target": launch_target},
            }
        except Exception as error:
            return {
                "success": False,
                "message": f"Could not launch {application}.",
                "error": str(error),
            }

    def open_folder(self, folder: str) -> Dict:
        folder = folder.strip().lower()
        path = FOLDER_ALIASES.get(folder, folder)

        if not os.path.isdir(path):
            expanded = os.path.expanduser(folder)
            if os.path.isdir(expanded):
                path = expanded
            else:
                return {
                    "success": False,
                    "message": f"Folder not found: {folder}",
                    "error": "FOLDER_NOT_FOUND",
                }

        try:
            os.startfile(path)
            return {
                "success": True,
                "message": f"Opened folder: {path}",
                "data": {"folder": path},
            }
        except Exception as error:
            return {
                "success": False,
                "message": f"Could not open folder: {folder}",
                "error": str(error),
            }

    def copy_to_clipboard(self, text: str) -> Dict:
        if not text:
            return {
                "success": False,
                "message": "Nothing to copy.",
                "error": "EMPTY_TEXT",
            }

        try:
            self._set_clipboard(text)
            preview = text if len(text) <= 60 else text[:57] + "..."
            return {
                "success": True,
                "message": f"Copied to clipboard: {preview}",
                "data": {"text": text},
            }
        except Exception as error:
            return {
                "success": False,
                "message": "Could not copy to clipboard.",
                "error": str(error),
            }

    def get_clipboard(self) -> Dict:
        try:
            text = self._get_clipboard_text()

            if not text:
                return {
                    "success": True,
                    "message": "Clipboard is empty.",
                    "data": {"text": ""},
                }

            preview = text if len(text) <= 120 else text[:117] + "..."
            return {
                "success": True,
                "message": f"Clipboard: {preview}",
                "data": {"text": text},
            }
        except Exception as error:
            return {
                "success": False,
                "message": "Could not read clipboard.",
                "error": str(error),
            }

    def system_info(self) -> Dict:
        info = {
            "os": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "username": os.environ.get("USERNAME", "Unknown"),
            "home": str(Path.home()),
        }

        lines = [
            f"OS: {info['os']} {info['release']}",
            f"Machine: {info['machine']}",
            f"User: {info['username']}",
            f"Home: {info['home']}",
        ]

        return {
            "success": True,
            "message": " | ".join(lines),
            "data": info,
        }

    def focus_window(self, application: str) -> Dict:
        application = application.strip().lower()

        if not application:
            return {
                "success": False,
                "message": "No application specified to focus.",
                "error": "MISSING_APPLICATION",
            }

        target = APP_ALIASES.get(application, application)
        script = f"""
$target = '{target}'
$proc = Get-Process -ErrorAction SilentlyContinue |
    Where-Object {{ $_.MainWindowHandle -ne 0 -and $_.ProcessName -like "*$target*" }} |
    Select-Object -First 1
if (-not $proc) {{ exit 2 }}
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinFocus {{
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}}
"@
[WinFocus]::ShowWindow($proc.MainWindowHandle, 9) | Out-Null
[WinFocus]::SetForegroundWindow($proc.MainWindowHandle) | Out-Null
Write-Output $proc.ProcessName
"""

        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                check=True,
                capture_output=True,
                text=True,
            )
            focused = result.stdout.strip() or target
            return {
                "success": True,
                "message": f"Focused window: {focused}",
                "data": {"application": application, "process": focused},
            }
        except subprocess.CalledProcessError:
            return {
                "success": False,
                "message": f"No open window found for {application}.",
                "error": "WINDOW_NOT_FOUND",
            }

    def set_volume(self, level: int) -> Dict:
        level = max(0, min(100, int(level)))
        script = f"""
$level = {level}
$wshell = New-Object -ComObject WScript.Shell
1..50 | ForEach-Object {{ $wshell.SendKeys([char]174) | Out-Null }}
$steps = [math]::Round($level / 2)
1..$steps | ForEach-Object {{ $wshell.SendKeys([char]175) | Out-Null }}
Write-Output $level
"""

        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                check=True,
                capture_output=True,
                text=True,
            )
            return {
                "success": True,
                "message": f"Volume set to approximately {level}%.",
                "data": {"level": level},
            }
        except Exception as error:
            return {
                "success": False,
                "message": "Could not set volume.",
                "error": str(error),
            }

    def minimize_all(self) -> Dict:
        script = """
$shell = New-Object -ComObject Shell.Application
$shell.MinimizeAll()
Write-Output "minimized"
"""

        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                check=True,
                capture_output=True,
                text=True,
            )
            return {
                "success": True,
                "message": "All windows minimized.",
                "data": {},
            }
        except Exception as error:
            return {
                "success": False,
                "message": "Could not minimize windows.",
                "error": str(error),
            }

    def list_windows(self, limit: int = 8) -> Dict:
        script = f"""
Get-Process -ErrorAction SilentlyContinue |
    Where-Object {{ $_.MainWindowTitle -ne '' }} |
    Select-Object -First {limit} ProcessName, MainWindowTitle |
    ForEach-Object {{ "$($_.ProcessName): $($_.MainWindowTitle)" }}
"""

        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                check=True,
                capture_output=True,
                text=True,
            )
            lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]

            if not lines:
                return {
                    "success": True,
                    "message": "No visible windows found.",
                    "data": {"windows": []},
                }

            return {
                "success": True,
                "message": "Windows: " + " | ".join(lines),
                "data": {"windows": lines},
            }
        except Exception as error:
            return {
                "success": False,
                "message": "Could not list windows.",
                "error": str(error),
            }

    def _resolve_app_target(self, target: str) -> Optional[str]:
        if os.path.isfile(target):
            return target

        resolved = shutil.which(target)
        if resolved:
            return resolved

        for path in WINDOWS_PATHS.get(target, []):
            if os.path.isfile(path):
                return path

        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "", target],
                shell=False,
            )
            return target
        except Exception:
            return None

    def _set_clipboard(self, text: str) -> None:
        escaped = text.replace("'", "''")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"Set-Clipboard -Value '{escaped}'",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def _get_clipboard_text(self) -> str:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Clipboard -Raw",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
