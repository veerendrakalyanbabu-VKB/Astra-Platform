"""Quick system status check without starting REPL/API."""

import json


def print_status(core) -> int:
    config = core.config
    voice = core.voice.status() if core.voice else {}
    learning = core.learning.stats()
    metrics = core.metrics.snapshot()

    print()
    print("ASTRA STATUS")
    print("-" * 40)
    print(f"Version        : {core.VERSION}")
    print(f"Ready          : {core.ready}")
    llm_cfg = config.get("llm_config") or {}
    llm_line = llm_cfg.get("llm_label", "Standby") if llm_cfg.get("llm_active") else "Standby"
    print(f"LLM            : {llm_line}")
    print(f"Plugins        : {', '.join(core.plugins.loaded_plugins) or 'none'}")
    print(f"Voice STT/TTS  : {voice.get('speech_to_text', False)} / {voice.get('text_to_speech', False)}")
    print(f"Memory entries : {len(core.memory.list_all())}")
    print(f"Sync device    : {core.cloud_sync.device_id[:8]}...")
    print(f"Cloud sync     : {'Remote' if core.cloud_sync.remote_url else 'Local'}")
    print(f"Encryption     : {'Active' if core.cloud_sync.crypto.enabled else 'Off (set ASTRA_SYNC_KEY)'}")
    print(f"Profile         : {core.profiles.active_profile}")
    print(f"Marketplace     : {len(core.marketplace.list_catalog())} plugins available")
    print(f"Tray + hotkey  : python main.py --tray  (Ctrl+Shift+A)")
    print(f"Sync server    : python main.py --sync-server")
    print(f"Goal routines  : morning, work, focus, downloads + custom")
    print(f"Session saved  : {core.session.session_path.exists()}")
    print(f"Learning rate  : {learning['success_rate'] * 100:.0f}% ({learning['total']} records)")
    print(f"Requests       : {metrics['counters'].get('pipeline.requests', 0)}")
    print()
    print("Quick test...")

    result = core.process("What time is it?")
    ok = result.executed or "time" in result.message.lower()

    print(f"Pipeline test  : {'PASS' if ok else 'FAIL'}")
    print(f"Response       : {result.message[:80]}")
    print()

    if ok:
        print("All systems go. Run: python main.py")
        return 0

    print("Something failed. Check logs/astra.log")
    return 1
