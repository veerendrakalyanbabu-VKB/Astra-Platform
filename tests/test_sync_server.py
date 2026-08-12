import json
from urllib.request import urlopen, Request


def test_sync_server_post_and_get(tmp_path):
    from sync_server.server import SyncServer
    import threading
    import time

    storage = tmp_path / "sync_data"
    server = SyncServer(host="127.0.0.1", port=18790, storage_dir=storage)

    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.5)

    bundle = {"device_id": "test", "memory": {"city": {"value": "Austin", "version": 1}}}

    request = Request(
        "http://127.0.0.1:18790",
        data=json.dumps(bundle).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urlopen(request, timeout=5)

    response = urlopen("http://127.0.0.1:18790", timeout=5)
    result = json.loads(response.read().decode("utf-8"))

    assert result["memory"]["city"]["value"] == "Austin"

    server.server.shutdown()
