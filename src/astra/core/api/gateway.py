import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


class AstraAPIHandler(BaseHTTPRequestHandler):

    core = None

    def log_message(self, format, *args):
        if self.core and self.core.logger:
            self.core.logger.info(f"API {self.address_string()} {format % args}")

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

    def _pipeline_to_dict(self, result) -> dict:
        payload = {
            "input": result.input,
            "intent": result.intent.intent,
            "entities": result.intent.entities,
            "confidence": result.intent.confidence,
            "executed": result.executed,
            "blocked": result.blocked,
            "needs_confirmation": result.needs_confirmation,
            "message": result.message,
        }

        if result.reasoning:
            payload["risk"] = result.reasoning["analysis"]["risk"]
            payload["decision"] = result.reasoning["decision"]["decision"]

        return payload

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/v1/health":
            self._send_json(200, {
                "status": "ok",
                "version": self.core.VERSION,
                "ready": self.core.ready,
            })
            return

        if path == "/v1/metrics":
            self._send_json(200, self.core.metrics.snapshot())
            return

        if path == "/v1/tools":
            self._send_json(200, {"tools": self.core.tools.list_tools()})
            return

        if path == "/v1/knowledge":
            self._send_json(200, {
                "topics": self.core.knowledge.list_topics(),
            })
            return

        if path == "/v1/memory":
            self._send_json(200, {
                "memory": self.core.memory.list_all(),
            })
            return

        if path == "/v1/sync/status":
            self._send_json(200, self.core.cloud_sync.status())
            return

        if path == "/v1/sync/pull":
            bundle_path = self.core.cloud_sync.bundle_file
            if not bundle_path.exists():
                self._send_json(404, {"error": "No sync bundle available"})
                return

            with open(bundle_path, "r", encoding="utf-8") as file:
                bundle = json.load(file)

            self._send_json(200, bundle)
            return

        if path == "/v1/learning":
            self._send_json(200, self.core.learning.stats())
            return

        if path == "/v1/mobile/status":
            self._send_json(200, {
                "version": self.core.VERSION,
                "profile": self.core.profiles.active_profile,
                "user": self.core.memory.recall("user_name"),
                "memory_count": len(self.core.memory.list_all()),
                "plugins": self.core.plugins.loaded_plugins,
                "llm": bool((self.core.config.get("llm_config") or {}).get("llm_active")),
                "llm_provider": (self.core.config.get("llm_config") or {}).get("provider"),
            })
            return

        if path == "/v1/profiles":
            self._send_json(200, {"profiles": self.core.profiles.list_profiles()})
            return

        if path == "/v1/marketplace":
            self._send_json(200, {"catalog": self.core.marketplace.list_catalog()})
            return

        if path == "/v1/billing/status":
            from astra.core.billing.stripe_billing import billing_status

            tier = self.core.tiers.get_tier()
            usage = self.core.usage.snapshot(self.core.tiers.tier_id)
            self._send_json(200, {
                "tier": tier,
                "usage": usage,
                **billing_status(),
            })
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/v1/billing/webhook":
            length = int(self.headers.get("Content-Length", 0))
            payload = self.rfile.read(length)
            signature = self.headers.get("Stripe-Signature", "")

            from astra.core.billing.stripe_billing import (
                tier_from_checkout_event,
                verify_webhook,
            )

            event = verify_webhook(payload, signature)
            if not event:
                self._send_json(400, {"error": "Invalid webhook signature"})
                return

            tier_id = tier_from_checkout_event(event)
            if tier_id:
                self.core.tiers.activate_paid(tier_id, source="stripe_webhook")

            self._send_json(200, {"received": True, "tier": tier_id})
            return

        try:
            body = self._read_json()
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if path == "/v1/chat":
            message = body.get("message", "").strip()

            if not message:
                self._send_json(400, {"error": "Missing 'message' field"})
                return

            if self.core.permissions.has_pending():
                confirmation = self.core.permissions.parse_confirmation(message)

                if confirmation is True:
                    result = self.core.pipeline.execute_approved_plan(message)
                elif confirmation is False:
                    result = self.core.pipeline.cancel_pending(message)
                else:
                    self._send_json(409, {
                        "error": "Confirmation pending",
                        "pending": self.core.permissions.describe_pending(),
                    })
                    return
            else:
                result = self.core.process(message)

            self._send_json(200, self._pipeline_to_dict(result))
            return

        if path == "/v1/confirm":
            response = body.get("response", "").strip()
            confirmation = self.core.permissions.parse_confirmation(response)

            if not self.core.permissions.has_pending():
                self._send_json(409, {"error": "No pending confirmation"})
                return

            if confirmation is True:
                result = self.core.pipeline.execute_approved_plan(response)
            elif confirmation is False:
                result = self.core.pipeline.cancel_pending(response)
            else:
                self._send_json(400, {"error": "Response must be yes or no"})
                return

            self._send_json(200, self._pipeline_to_dict(result))
            return

        if path == "/v1/tools/invoke":
            name = body.get("name", "")
            parameters = body.get("parameters", {})
            result = self.core.tools.invoke(name, parameters)
            self._send_json(200 if result["success"] else 400, result)
            return

        if path == "/v1/sync/push":
            bundle = body if body.get("memory") else self.core.cloud_sync.export_bundle()
            result = self.core.cloud_sync.import_bundle(bundle, merge=True)
            self._send_json(200, {
                "status": "ok",
                "imported": result["imported"],
                "skipped": result["skipped"],
                "device_id": result["device_id"],
            })
            return

        if path == "/v1/sync/run":
            result = self.core.cloud_sync.sync()
            self._send_json(200, result)
            return

        if path == "/v1/profiles/switch":
            profile_id = body.get("profile", "").strip()

            if not profile_id:
                self._send_json(400, {"error": "Missing 'profile' field"})
                return

            result = self.core.profiles.switch_profile(profile_id, self.core)
            self._send_json(200, result)
            return

        if path == "/v1/profiles/create":
            name = body.get("name", "").strip()

            if not name:
                self._send_json(400, {"error": "Missing 'name' field"})
                return

            result = self.core.profiles.create_profile(name)
            self._send_json(200, result)
            return

        if path == "/v1/marketplace/install":
            plugin_id = body.get("plugin", "").strip()

            if not plugin_id:
                self._send_json(400, {"error": "Missing 'plugin' field"})
                return

            result = self.core.marketplace.install(
                plugin_id,
                self.core.plugins,
                self.core,
            )
            self._send_json(200 if result["success"] else 400, result)
            return

        self._send_json(404, {"error": "Not found"})


class APIGateway:

    def __init__(self, core, host="127.0.0.1", port=8787):
        self.core = core
        self.host = host
        self.port = port
        self.server = None

    def start(self) -> None:
        AstraAPIHandler.core = self.core
        self.server = ThreadingHTTPServer((self.host, self.port), AstraAPIHandler)

        print(f"[ OK ] API Gateway listening on http://{self.host}:{self.port}")
        print()
        print("  Endpoints:")
        print(f"    POST http://{self.host}:{self.port}/v1/chat")
        print(f"    POST http://{self.host}:{self.port}/v1/confirm")
        print(f"    GET  http://{self.host}:{self.port}/v1/health")
        print(f"    GET  http://{self.host}:{self.port}/v1/metrics")
        print(f"    GET  http://{self.host}:{self.port}/v1/tools")
        print(f"    GET  http://{self.host}:{self.port}/v1/memory")
        print()

        if self.core.logger:
            self.core.logger.info(f"API Gateway started on {self.host}:{self.port}")

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print()
            print("[ OK ] API Gateway stopped")

            if self.core.logger:
                self.core.logger.info("API Gateway stopped")
