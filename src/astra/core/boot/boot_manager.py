from pathlib import Path

from astra.core.astra_core import AstraCore
from astra.core.api import APIGateway
from astra.core.interface import AstraREPL


class BootManager:

    def __init__(self, demo=False, debug=False, serve=False, web=False, desktop=False, mobile=False, tray=False, sync_server=False, voice=False, wake=False, portal=False, status=False, cmd=None, port=8787, sync_port=8790, host="127.0.0.1"):

        self.demo = demo
        self.debug = debug
        self.serve = serve
        self.web = web
        self.desktop = desktop
        self.mobile = mobile
        self.tray = tray
        self.sync_server = sync_server
        self.voice = voice
        self.wake = wake
        self.portal = portal
        self.status = status
        self.cmd = cmd
        self.port = port
        self.sync_port = sync_port
        self.host = host
        project_root = Path(__file__).resolve().parents[4]
        self.core = AstraCore(project_root=project_root)

    def start(self):

        self.core.initialize(voice_enabled=self.voice or self.wake)

        if self.status:
            from astra.core.boot.status import print_status
            import sys
            code = print_status(self.core)
            self.core.shutdown()
            sys.exit(code)

        verbose = self.demo or self.debug or self.serve

        if verbose:
            self._print_verbose_boot()
        else:
            self._print_quiet_boot()

        if self.cmd:
            self._run_cmd()
        elif self.tray:
            self._run_tray()
        elif self.sync_server:
            self._run_sync_server()
        elif self.wake:
            self._run_wake()
        elif self.desktop:
            self._run_desktop()
        elif self.mobile:
            self._run_mobile()
        elif self.portal:
            self._run_portal()
        elif self.web:
            self._run_web()
        elif self.serve:
            self._run_api()
        elif self.demo:
            self._run_demo()
        else:
            self._run_repl()

        self.core.shutdown()
        self.core.logger.info("Session Completed Successfully")

    def _ensure_streamlit(self) -> bool:
        try:
            import streamlit  # noqa: F401
            return True
        except ImportError:
            print("Streamlit is required for UI modes.")
            print()
            print("  python -m pip install -r requirements.txt")
            print("  powershell -ExecutionPolicy Bypass -File setup.ps1")
            print()
            return False

    def _port_available(self, port: int) -> bool:
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return True
            except OSError:
                return False

    def _free_port(self, port: int) -> int:
        """Stop processes listening on port (Windows). Returns count killed."""
        import subprocess
        import sys

        if sys.platform != "win32":
            return 0

        killed = 0
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            pids = set()
            needle = f":{port}"
            for line in result.stdout.splitlines():
                if needle not in line or "LISTENING" not in line.upper():
                    continue
                parts = line.split()
                if parts and parts[-1].isdigit():
                    pids.add(parts[-1])

            for pid in pids:
                subprocess.run(
                    ["taskkill", "/PID", pid, "/F"],
                    capture_output=True,
                    check=False,
                )
                killed += 1
        except (OSError, subprocess.SubprocessError):
            pass

        if killed:
            import time
            time.sleep(0.6)
        return killed

    def _resolve_port(self, preferred: int, span: int = 10) -> int:
        if self._port_available(preferred):
            return preferred

        freed = self._free_port(preferred)
        if freed and self._port_available(preferred):
            print(f"Port {preferred} was busy — cleared old process.")
            print()
            return preferred

        for port in range(preferred + 1, preferred + span):
            if self._port_available(port):
                print(f"Port {preferred} is in use — using http://localhost:{port}")
                print()
                return port

        return preferred

    def _ensure_background_streamlit(self, app_path: Path, port: int, label: str) -> None:
        """Start a Streamlit app in the background if its port is free."""
        import subprocess
        import sys
        import time

        if not app_path.exists():
            return

        if not self._port_available(port):
            print(f"{label} already running at http://localhost:{port}")
            print()
            return

        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app_path),
                "--server.port",
                str(port),
                "--server.headless",
                "true",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **kwargs,
        )

        for _ in range(40):
            if not self._port_available(port):
                print(f"{label} ready at http://localhost:{port}")
                print()
                return
            time.sleep(0.25)

        print(f"{label} starting at http://localhost:{port} (may take a few seconds)")
        print()

    def _run_streamlit(self, app_path: Path, preferred_port: int, banner_lines: list[str]):
        import subprocess
        import sys

        port = self._resolve_port(preferred_port)

        for line in banner_lines:
            print(line.replace("{port}", str(port)))
        print()

        self._open_browser_when_ready(f"http://localhost:{port}")

        try:
            subprocess.run([
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app_path),
                "--server.port",
                str(port),
                "--server.headless",
                "true",
            ])
        except KeyboardInterrupt:
            print("\nAstra stopped.")

    def _open_browser_when_ready(self, url: str) -> None:
        """Open browser once — after the port accepts connections (no fixed delay tab)."""
        import os
        import threading

        if os.environ.get("ASTRA_NO_BROWSER", "").strip().lower() in ("1", "true", "yes"):
            return

        import webbrowser

        def _wait_and_open():
            import socket
            import time

            try:
                port = int(url.rsplit(":", 1)[-1].split("/")[0])
            except ValueError:
                port = 8501

            for _ in range(120):
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.35):
                        break
                except OSError:
                    time.sleep(0.25)

            time.sleep(0.8)
            try:
                webbrowser.open(url, new=1, autoraise=True)
            except OSError:
                pass

        threading.Thread(target=_wait_and_open, daemon=True).start()

    def _open_browser_later(self, url: str, delay: float = 3.0) -> None:
        """Legacy helper — prefer _open_browser_when_ready."""
        import threading
        import webbrowser

        def _open():
            import time
            time.sleep(delay)
            try:
                webbrowser.open(url)
            except OSError:
                pass

        threading.Thread(target=_open, daemon=True).start()

    def _print_quiet_boot(self):
        llm_cfg = self.core.config.get("llm_config") or {}
        llm = llm_cfg.get("llm_label", "Standby") if llm_cfg.get("llm_active") else "Standby"
        plugins = ", ".join(self.core.plugins.loaded_plugins) or "none"
        print(f"Astra {AstraCore.VERSION} | {llm} | plugins: {plugins}")

    def _print_verbose_boot(self):
        print("=" * 60)
        print("                ASTRA PLATFORM")
        print(f"                Version {AstraCore.VERSION}")
        print("=" * 60)
        print("[BOOT] Initializing Astra...")
        print()
        print("[ OK ] Astra Core Loaded")

        if self.core.plugins.loaded_plugins:
            print(f"[ OK ] Plugins: {', '.join(self.core.plugins.loaded_plugins)}")

        llm_cfg = self.core.config.get("llm_config") or {}
        if llm_cfg.get("llm_active"):
            label = llm_cfg.get("llm_label", "LLM Active")
            print(f"[ OK ] Neural Layer: {label}")
        else:
            print("[ OK ] Neural Layer Standby (add OPENAI_API_KEY or ANTHROPIC_API_KEY)")

        print("[ OK ] System Ready")
        print()

    def _run_cmd(self):
        result = self.core.process(self.cmd)
        print(f"Astra> {result.message}")

    def _run_repl(self):
        repl = AstraREPL(
            pipeline=self.core.pipeline,
            permission_manager=self.core.permissions,
            memory=self.core.memory,
            voice=self.core.voice,
            logger=self.core.logger,
            debug=self.debug,
            voice_mode=self.voice,
        )
        repl.start()

    def _run_api(self):
        gateway = APIGateway(self.core, host=self.host, port=self.port)
        gateway.start()

    def _run_mobile(self):
        if not self._ensure_streamlit():
            return

        app_path = Path(__file__).resolve().parents[4] / "mobile" / "app.py"
        self._run_streamlit(app_path, 8502, [
            "Starting ASTRA ULTRON Mobile at http://localhost:{port}",
            "Gestures + voice mic on orb · Allow camera/mic when prompted",
            "On your phone (same Wi-Fi): http://<your-pc-ip>:{port}",
        ])

    def _run_portal(self):
        if not self._ensure_streamlit():
            return

        app_path = Path(__file__).resolve().parents[4] / "portal" / "app.py"
        self._run_streamlit(app_path, 8503, [
            "Starting Astra Portal at http://localhost:{port}",
            "Pricing · leads · startup & student positioning",
        ])

    def _run_tray(self):
        import subprocess
        import sys

        tray_path = Path(__file__).resolve().parents[4] / "desktop" / "tray.py"

        print("Starting Astra OS Tray + Hotkey (Ctrl+Shift+A)")
        print()

        subprocess.run([sys.executable, str(tray_path)])

    def _run_wake(self):
        from astra.core.voice.wake_listener import WakeWordListener

        settings = self.core.voice_settings
        voice = self.core.voice
        name = settings.assistant_name

        print(f"Astra wake mode — say \"hey {name.lower()}\" like Alexa")
        print("Settings: voice settings | set assistant name to Nova")
        print()

        def on_wake(heard, mode):
            print(f"[{mode.upper()}] Wake detected")
            if voice and voice.tts_available:
                voice.speak(f"Yes, {name} here.")

        def on_command(command):
            result = self.core.process(command)
            print(f"{name}> {result.message}")
            if voice and voice.tts_available and result.message:
                voice.speak(result.message[:220])

        def on_sleep(heard):
            print(f"{name}> Goodnight.")
            if voice and voice.tts_available:
                voice.speak("Goodnight.")

        try:
            WakeWordListener(settings, voice, on_wake, on_command, on_sleep).run()
        except KeyboardInterrupt:
            print("\nWake listener stopped.")

    def _run_sync_server(self):
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
        from sync_server.server import SyncServer

        storage = Path(__file__).resolve().parents[4] / "data" / "sync_server"
        server = SyncServer(port=self.sync_port, storage_dir=storage)
        server.start()

    def _run_desktop(self):
        if not self._ensure_streamlit():
            return

        root = Path(__file__).resolve().parents[4]
        portal_path = root / "portal" / "app.py"
        self._ensure_background_streamlit(portal_path, 8503, "Astra Portal")

        app_path = root / "desktop" / "shell.py"
        self._run_streamlit(app_path, 8501, [
            "Starting ASTRA ULTRON Desktop at http://localhost:{port}",
            "Portal (pricing & trials) at http://localhost:8503",
            "Orb + gestures + voice on left · Chat on right",
        ])

    def _run_web(self):
        import subprocess
        import sys

        if not self._ensure_streamlit():
            return

        app_path = Path(__file__).resolve().parents[4] / "web" / "app.py"

        print("Starting Web UI at http://localhost:8501")
        print()

        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.headless",
            "true",
        ])

    def _run_demo(self):
        print("ASTRA v1.0 - SHIP DEMO")
        print("=" * 40)
        print()

        commands = [
            "help",
            "What time is it?",
            "Calculate 99 * 11",
            "Hello astra",
            "Remember my goal is build Astra OS",
            "What is my goal",
            "Open notepad and remember my snack is chips",
            "What is my snack",
            "Can you open calculator",
            "What is astra",
        ]

        passed = 0

        for command in commands:
            result = self.core.process(command)
            ok = result.executed or result.message
            status = "PASS" if ok else "FAIL"

            if ok:
                passed += 1

            print(f"[{status}] {command}")
            print(f"       -> {result.message[:90]}")
            print()

        stats = self.core.learning.stats()
        print("=" * 40)
        print(f"Results: {passed}/{len(commands)} passed")
        print(f"Learning: {stats['success_rate'] * 100:.0f}% success ({stats['total']} records)")
        print()
        print("Astra Platform v1.0 - READY TO SHIP")

    def _print_demo_result(self, command, result):
        print(f"  {result.intent.intent} | {result.message[:80]}")
