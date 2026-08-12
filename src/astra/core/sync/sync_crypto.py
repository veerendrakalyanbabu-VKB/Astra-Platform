"""Authenticated encryption for sync bundles using stdlib only."""

import base64
import hashlib
import hmac
import json
import os
import zlib


class SyncCrypto:

    def __init__(self, sync_key: str = ""):
        self.sync_key = sync_key.strip()

    @property
    def enabled(self) -> bool:
        return bool(self.sync_key)

    def encrypt_bundle(self, bundle: dict) -> dict:
        if not self.enabled:
            return bundle

        salt = os.urandom(16)
        key = self._derive_key(salt)
        plaintext = json.dumps(bundle, separators=(",", ":")).encode("utf-8")
        compressed = zlib.compress(plaintext)
        encrypted = self._xor_bytes(compressed, key)
        mac = hmac.new(key, salt + encrypted, hashlib.sha256).hexdigest()

        return {
            "encrypted": True,
            "algorithm": "PBKDF2-HMAC-SHA256+XOR",
            "salt": base64.b64encode(salt).decode("ascii"),
            "payload": base64.b64encode(encrypted).decode("ascii"),
            "mac": mac,
        }

    def decrypt_bundle(self, envelope: dict) -> dict:
        if not envelope.get("encrypted"):
            return envelope

        if not self.enabled:
            raise ValueError("ASTRA_SYNC_KEY required to decrypt sync bundle")

        salt = base64.b64decode(envelope["salt"])
        encrypted = base64.b64decode(envelope["payload"])
        key = self._derive_key(salt)
        expected_mac = envelope.get("mac", "")

        if not hmac.compare_digest(
            hmac.new(key, salt + encrypted, hashlib.sha256).hexdigest(),
            expected_mac,
        ):
            raise ValueError("Sync bundle authentication failed — wrong key or tampered data")

        compressed = self._xor_bytes(encrypted, key)
        plaintext = zlib.decompress(compressed)
        return json.loads(plaintext.decode("utf-8"))

    def _derive_key(self, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            self.sync_key.encode("utf-8"),
            salt,
            100000,
            dklen=32,
        )

    def _xor_bytes(self, data: bytes, key: bytes) -> bytes:
        stream = hashlib.sha256(key + b"astra-sync-stream").digest()
        return bytes(byte ^ stream[index % len(stream)] for index, byte in enumerate(data))
