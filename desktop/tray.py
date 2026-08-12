"""Astra OS layer — system tray and global hotkey."""

import subprocess
import sys
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


HOTKEY = "ctrl+shift+a"


def _run_command_dialog(core):
    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    command = simpledialog.askstring(
        "Astra",
        "What should Astra do?",
        parent=root,
    )

    root.destroy()

    if command:
        result = core.process(command.strip())
        print(f"Astra> {result.message}")


def _scheduler_loop(core):
    while True:
        try:
            due = core.scheduler.run_due(
                lambda command, entry: core.process(command)
            )

            for item in due:
                msg = item["result"].message if hasattr(item["result"], "message") else str(item["result"])
                print(f"[schedule] Ran {item.get('command', item['routine'])}: {msg[:80]}")

        except Exception as error:
            print(f"[schedule] Error: {error}")

        time.sleep(60)


def start_tray():
    from astra.core.astra_core import AstraCore

    core = AstraCore(project_root=PROJECT_ROOT)
    core.initialize()

    scheduler_thread = threading.Thread(target=_scheduler_loop, args=(core,), daemon=True)
    scheduler_thread.start()

    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError:
        print("Tray mode requires: pip install pystray Pillow")
        print(f"Hotkey fallback: press {HOTKEY} in this window")
        _run_hotkey_fallback(core)
        return

    def create_icon():
        image = Image.new("RGB", (64, 64), color=(26, 26, 62))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill=(102, 126, 234))
        draw.text((22, 20), "A", fill=(255, 255, 255))
        return image

    def open_desktop(_icon, _item):
        subprocess.Popen([
            sys.executable,
            str(PROJECT_ROOT / "main.py"),
            "--desktop",
        ])

    def open_command(_icon, _item):
        _run_command_dialog(core)

    def sync_memory(_icon, _item):
        result = core.process("sync my memory")
        print(f"Astra> {result.message}")

    def on_quit(icon, _item):
        core.shutdown()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Open Desktop Shell", open_desktop),
        pystray.MenuItem("Quick Command...", open_command),
        pystray.MenuItem("Sync Memory", sync_memory),
        pystray.MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon("astra", create_icon(), "Astra OS", menu)

    try:
        import keyboard

        keyboard.add_hotkey(HOTKEY, lambda: _run_command_dialog(core))
        print(f"[ OK ] Hotkey active: {HOTKEY}")
    except ImportError:
        print("Install 'keyboard' for global hotkey: pip install keyboard")

    print(f"[ OK ] Astra Tray running — v{core.VERSION}")
    icon.run()


def _run_hotkey_fallback(core):
    try:
        import keyboard

        print(f"[ OK ] Hotkey active: {HOTKEY} (no tray icon)")
        keyboard.add_hotkey(HOTKEY, lambda: _run_command_dialog(core))
        keyboard.wait()
    except ImportError:
        print("Install tray deps: pip install -r requirements-tray.txt")
        core.shutdown()


if __name__ == "__main__":
    start_tray()
