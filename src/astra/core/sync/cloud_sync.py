"""Cloud sync for memory and session data across devices."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

from astra.core.sync.sync_crypto import SyncCrypto


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CloudSyncEngine:
    """
    Local-first sync with optional remote endpoint and encryption.

    Set ASTRA_SYNC_URL for remote sync.
    Set ASTRA_SYNC_KEY for encrypted bundles.
    """

    def __init__(self, memory_manager, project_root=None, sync_key: str = ""):
        self.memory = memory_manager
        self.project_root = Path(project_root or Path.cwd())
        self.sync_dir = self.project_root / "data" / "sync"
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.sync_dir / "sync_meta.json"
        self.device_file = self.sync_dir / "device.json"
        self.bundle_file = self.sync_dir / "latest_bundle.json"
        self.device_id = self._load_device_id()
        self.meta = self._load_meta()
        self.remote_url = os.environ.get("ASTRA_SYNC_URL", "").strip()
        self.crypto = SyncCrypto(sync_key or os.environ.get("ASTRA_SYNC_KEY", ""))

    def track_key(self, key: str, value) -> None:
        current = self.meta.get(key, {})
        version = current.get("version", 0) + 1

        self.meta[key] = {
            "updated_at": _utc_now(),
            "version": version,
            "device_id": self.device_id,
            "value_type": type(value).__name__,
        }
        self._save_meta()

    def export_bundle(self) -> dict:
        memory_payload = {}

        for key, value in self.memory.list_all().items():
            meta = self.meta.get(key, {})
            memory_payload[key] = {
                "value": value,
                "updated_at": meta.get("updated_at", _utc_now()),
                "version": meta.get("version", 1),
                "device_id": meta.get("device_id", self.device_id),
            }

        bundle = {
            "device_id": self.device_id,
            "exported_at": _utc_now(),
            "memory": memory_payload,
        }

        stored = self.crypto.encrypt_bundle(bundle) if self.crypto.enabled else bundle

        with open(self.bundle_file, "w", encoding="utf-8") as file:
            json.dump(stored, file, indent=2)

        return stored

    def import_bundle(self, envelope: dict, merge: bool = True) -> dict:
        bundle = self._unwrap_bundle(envelope)
        memory_payload = bundle.get("memory", {})
        imported = 0
        skipped = 0

        for key, entry in memory_payload.items():
            incoming = {
                "value": entry.get("value"),
                "updated_at": entry.get("updated_at", _utc_now()),
                "version": entry.get("version", 1),
                "device_id": entry.get("device_id", "unknown"),
            }

            if merge and key in self.meta:
                local = self.meta[key]
                local_time = local.get("updated_at", "")
                incoming_time = incoming["updated_at"]

                if local_time >= incoming_time:
                    skipped += 1
                    continue

            self.memory.remember(key, incoming["value"])
            self.meta[key] = {
                "updated_at": incoming["updated_at"],
                "version": incoming["version"],
                "device_id": incoming["device_id"],
                "value_type": type(incoming["value"]).__name__,
            }
            imported += 1

        self._save_meta()

        return {
            "imported": imported,
            "skipped": skipped,
            "device_id": self.device_id,
        }

    def sync(self) -> dict:
        stored = self.export_bundle()
        bundle = self._unwrap_bundle(stored)
        result = {
            "device_id": self.device_id,
            "exported_keys": len(bundle.get("memory", {})),
            "local_bundle": str(self.bundle_file),
            "remote": False,
            "encrypted": self.crypto.enabled,
            "imported": 0,
            "skipped": 0,
            "message": "Memory exported locally.",
        }

        if self.crypto.enabled:
            result["message"] = (
                f"Memory encrypted and exported to {self.bundle_file.name}."
            )
        else:
            result["message"] = (
                f"Memory exported to {self.bundle_file.name}. "
                "Set ASTRA_SYNC_KEY to encrypt."
            )

        if self.remote_url:
            remote_result = self._sync_remote(stored)
            result.update(remote_result)
            result["remote"] = True
            result["message"] = remote_result.get(
                "message",
                "Memory synced with remote endpoint.",
            )

        return result

    def status(self) -> dict:
        return {
            "device_id": self.device_id,
            "tracked_keys": len(self.meta),
            "memory_keys": len(self.memory.list_all()),
            "remote_configured": bool(self.remote_url),
            "remote_url": self.remote_url or None,
            "encryption_enabled": self.crypto.enabled,
            "bundle_path": str(self.bundle_file),
        }

    def _unwrap_bundle(self, envelope: dict) -> dict:
        if envelope.get("encrypted"):
            return self.crypto.decrypt_bundle(envelope)
        return envelope

    def _sync_remote(self, stored: dict) -> dict:
        payload = json.dumps(stored).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        try:
            push_request = request.Request(
                self.remote_url,
                data=payload,
                headers=headers,
                method="POST",
            )

            with request.urlopen(push_request, timeout=10) as response:
                response.read()

            pull_request = request.Request(self.remote_url, method="GET")

            with request.urlopen(pull_request, timeout=10) as response:
                body = response.read().decode("utf-8")

            remote_envelope = json.loads(body) if body else {}
            merge_result = self.import_bundle(remote_envelope, merge=True)

            return {
                "imported": merge_result["imported"],
                "skipped": merge_result["skipped"],
                "message": "Remote sync complete.",
            }
        except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            return {
                "imported": 0,
                "skipped": 0,
                "message": f"Remote sync failed: {exc}. Local export saved.",
                "error": str(exc),
            }

    def _load_device_id(self) -> str:
        if self.device_file.exists():
            with open(self.device_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("device_id", self._create_device_id())

        return self._create_device_id()

    def _create_device_id(self) -> str:
        device_id = str(uuid.uuid4())
        with open(self.device_file, "w", encoding="utf-8") as file:
            json.dump({"device_id": device_id, "created_at": _utc_now()}, file, indent=2)
        return device_id

    def _load_meta(self) -> dict:
        if not self.meta_file.exists():
            return {}

        with open(self.meta_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def _save_meta(self) -> None:
        with open(self.meta_file, "w", encoding="utf-8") as file:
            json.dump(self.meta, file, indent=2)

    def reconfigure(self, sync_dir: Path) -> None:
        self.sync_dir = Path(sync_dir)
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.sync_dir / "sync_meta.json"
        self.device_file = self.sync_dir / "device.json"
        self.bundle_file = self.sync_dir / "latest_bundle.json"
        self.meta = self._load_meta()

        if not self.device_file.exists():
            self.device_id = self._create_device_id()
        else:
            self.device_id = self._load_device_id()
