import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from astra.core.boot.boot_manager import BootManager


def main():
    parser = argparse.ArgumentParser(description="Astra Platform")
    parser.add_argument("--demo", action="store_true", help="Run ship demo")
    parser.add_argument("--serve", action="store_true", help="Start REST API")
    parser.add_argument("--web", action="store_true", help="Start basic web UI")
    parser.add_argument("--desktop", action="store_true", help="Start Desktop Shell")
    parser.add_argument("--mobile", action="store_true", help="Start Mobile Companion")
    parser.add_argument("--tray", action="store_true", help="Start system tray + hotkey")
    parser.add_argument("--sync-server", action="store_true", help="Start sync server")
    parser.add_argument("--voice", action="store_true", help="Voice mode REPL")
    parser.add_argument("--wake", action="store_true", help="Alexa-style wake word listener")
    parser.add_argument("--portal", action="store_true", help="Start Astra Portal (pricing & leads)")
    parser.add_argument("--status", action="store_true", help="Health check")
    parser.add_argument("--cmd", type=str, help="Run one command and exit")
    parser.add_argument("--port", type=int, default=8787, help="API port")
    parser.add_argument("--sync-port", type=int, default=8790, help="Sync server port")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="API bind host")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    boot = BootManager(
        demo=args.demo,
        debug=args.debug,
        serve=args.serve,
        web=args.web,
        desktop=args.desktop,
        mobile=args.mobile,
        tray=args.tray,
        sync_server=args.sync_server,
        voice=args.voice,
        wake=args.wake,
        portal=args.portal,
        status=args.status,
        cmd=args.cmd,
        port=args.port,
        sync_port=args.sync_port,
        host=args.host,
    )
    try:
        boot.start()
    except KeyboardInterrupt:
        print("\nAstra stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
