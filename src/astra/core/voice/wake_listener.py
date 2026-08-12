"""Always-on wake phrase listener — Alexa-style activation for Astra."""

import time


class WakeWordListener:
    """
    Listens on the microphone for configured wake phrases.
    Uses SpeechRecognition (Google STT) — works out of the box on most PCs.
    """

    def __init__(self, voice_settings, voice_engine, on_wake, on_command, on_sleep):
        self.settings = voice_settings
        self.voice = voice_engine
        self.on_wake = on_wake
        self.on_command = on_command
        self.on_sleep = on_sleep
        self._running = False

    def run(self) -> None:
        if not self.voice or not self.voice.stt_available:
            print("Wake listener needs a microphone + SpeechRecognition.")
            print("Install: pip install -r requirements-voice.txt")
            return

        name = self.settings.assistant_name
        self._running = True
        print(f"Astra wake listener active — say \"hey {name.lower()}\" or \"wake up {name.lower()}\"")
        print("Ctrl+C to stop.")
        print()

        while self._running:
            heard = self.voice.listen(timeout=6, phrase_limit=6)
            if not heard:
                continue

            mode = self.settings.match_wake(heard)
            if mode == "sleep":
                self.on_sleep(heard)
                continue
            if mode in ("launch", "chat"):
                self.on_wake(heard, mode)
                command = self.settings.strip_wake_prefix(heard)
                if len(command) > 2:
                    self.on_command(command)
                else:
                    follow = self.voice.listen(timeout=8, phrase_limit=12)
                    if follow:
                        self.on_command(follow)
                continue

            if self._command_mode_hint(heard):
                self.on_command(heard)

    def stop(self) -> None:
        self._running = False

    @staticmethod
    def _command_mode_hint(text: str) -> bool:
        return text.lower().startswith(("astra ", "ask ", "open ", "what ", "show ", "run "))
