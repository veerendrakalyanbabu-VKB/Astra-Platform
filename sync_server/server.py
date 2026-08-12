"""Standalone sync server for Astra memory bundles."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class SyncServerHandler(BaseHTTPRequestHandler):

    storage_dir = None

    def log_message(self, format, *args):
        print(f"[sync] {self.address_string()} {format % args}")

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))

        if length == 0:
            return {}

        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        bundle_path = self.storage_dir / "latest_bundle.json"

        if not bundle_path.exists():
            self._send_json(200, {"device_id": "server", "memory": {}})
            return

        with open(bundle_path, "r", encoding="utf-8") as file:
            bundle = json.load(file)

        self._send_json(200, bundle)

    def do_POST(self):
        try:
            bundle = self._read_json()
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        bundle_path = self.storage_dir / "latest_bundle.json"

        with open(bundle_path, "w", encoding="utf-8") as file:
            json.dump(bundle, file, indent=2)

        keys = len(bundle.get("memory", {}))
        self._send_json(200, {
            "status": "ok",
            "stored_keys": keys,
            "message": f"Stored {keys} memory keys.",
        })


class SyncServer:

    def __init__(self, host="127.0.0.1", port=8790, storage_dir=None):
        self.host = host
        self.port = port
        self.storage_dir = Path(storage_dir or "data/sync_server")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.server = None

    def start(self) -> None:
        SyncServerHandler.storage_dir = self.storage_dir
        self.server = ThreadingHTTPServer((self.host, self.port), SyncServerHandler)

        print(f"[ OK ] Sync Server listening on http://{self.host}:{self.port}")
        print()
        print("  Set in .env:")
        print(f"    ASTRA_SYNC_URL=http://{self.host}:{self.port}")
        print()

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print()
            print("[ OK ] Sync Server stopped")
