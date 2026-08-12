from astra.core.sync.sync_crypto import SyncCrypto


def test_sync_crypto_round_trip():
    crypto = SyncCrypto("test-secret-key")
    bundle = {
        "device_id": "abc",
        "memory": {"city": {"value": "Austin", "version": 1}},
    }

    encrypted = crypto.encrypt_bundle(bundle)

    assert encrypted["encrypted"] is True
    assert "payload" in encrypted

    decrypted = crypto.decrypt_bundle(encrypted)

    assert decrypted["device_id"] == "abc"
    assert decrypted["memory"]["city"]["value"] == "Austin"


def test_sync_crypto_wrong_key_fails():
    crypto = SyncCrypto("correct-key")
    bundle = {"device_id": "abc", "memory": {}}
    encrypted = crypto.encrypt_bundle(bundle)

    wrong = SyncCrypto("wrong-key")

    try:
        wrong.decrypt_bundle(encrypted)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "authentication failed" in str(error).lower()


def test_sync_crypto_disabled_passthrough():
    crypto = SyncCrypto("")
    bundle = {"device_id": "abc", "memory": {}}

    assert crypto.encrypt_bundle(bundle) == bundle
