import sys


class AstraREPL:
    """
    Interactive command interface for Astra Platform.
    Supports text and optional voice modes.
    """

    BANNER = """
    ╔══════════════════════════════════════════════════════════╗
    ║                     A S T R A                          ║
    ║              AI-Native Computing Platform              ║
    ║                    Version 2.2.0                       ║
    ╚══════════════════════════════════════════════════════════╝
    """

    PROMPT = "You> "
    ASTRA = "Astra> "

    EXIT_COMMANDS = frozenset({"exit", "quit", "bye", "goodbye"})
    VOICE_COMMANDS = frozenset({"voice", "listen", "mic"})

    def __init__(
        self,
        pipeline,
        permission_manager,
        memory,
        voice=None,
        logger=None,
        debug=False,
        voice_mode=False,
    ):
        self.pipeline = pipeline
        self.permissions = permission_manager
        self.memory = memory
        self.voice = voice
        self.logger = logger
        self.debug = debug
        self.voice_mode = voice_mode
        self.running = False

    def start(self):

        self.running = True
        print(self.BANNER)

        user_name = self.memory.recall("user_name")

        if user_name:
            print(f"  Welcome back, {user_name}.")
        else:
            print("  Welcome to Astra.")

        if self.voice_mode and self.voice and self.voice.ready:
            print("  Voice mode active. Speak after the listening prompt.")
            print("  Type text anytime, or 'voice' to listen.")
        else:
            print("  Type 'help' for commands, 'exit' to leave.")

        print()

        if not sys.stdin.isatty():
            self._non_interactive_help()
            return

        eof_count = 0

        while self.running:
            try:
                if self.voice_mode and self.voice and self.voice.stt_available:
                    user_input = self._listen_or_type()
                else:
                    user_input = input(self.PROMPT).strip()

                eof_count = 0

            except EOFError:
                eof_count += 1

                if eof_count >= 2:
                    print()
                    self._farewell()
                    break

                print()
                print(f"{self.ASTRA}Input closed. Press Enter again to exit, or type a command.")
                continue

            except KeyboardInterrupt:
                print()
                print(f"{self.ASTRA}Interrupted. Type 'exit' to leave.")
                continue

            if not user_input:
                continue

            if user_input.lower() in self.EXIT_COMMANDS:
                self._farewell()
                break

            if user_input.lower() in self.VOICE_COMMANDS:
                user_input = self._listen_once()

                if not user_input:
                    print(f"{self.ASTRA}I didn't catch that.")
                    continue

            self._handle_input(user_input)

    def _listen_or_type(self) -> str:
        print(f"{self.PROMPT}[speak or type] ", end="", flush=True)
        heard = self.voice.listen(timeout=4)

        if heard:
            print(heard)
            return heard.strip()

        return input().strip()

    def _listen_once(self) -> str:
        print(f"{self.ASTRA}Listening...")
        heard = self.voice.listen(timeout=6)

        if heard:
            print(f"{self.PROMPT}{heard}")

        return heard.strip() if heard else ""

    def _handle_input(self, user_input: str):

        if self.permissions.has_pending():
            confirmation = self.permissions.parse_confirmation(user_input)

            if confirmation is True:
                result = self.pipeline.execute_approved_plan(user_input)
                self._respond(result)
                return

            if confirmation is False:
                result = self.pipeline.cancel_pending(user_input)
                print(f"{self.ASTRA}{result.message}")
                return

            print(f"{self.ASTRA}Please answer yes or no.")
            print(f"{self.ASTRA}{self.permissions.describe_pending()}")
            return

        result = self.pipeline.process(user_input)

        if result.needs_confirmation:
            self._print_confirmation_request(result)
            return

        self._respond(result)

    def _respond(self, result):

        if self.debug:
            self._print_debug(result)

        if result.blocked:
            message = result.message
            print(f"{self.ASTRA}{message}")
            self._speak(message)
            return

        if result.executed or result.message:
            message = result.message
            print(f"{self.ASTRA}{message}")
            self._speak(message)
            return

        message = "I couldn't complete that request."
        print(f"{self.ASTRA}{message}")
        self._speak(message)

    def _speak(self, text: str) -> None:
        if self.voice_mode and self.voice and self.voice.tts_available:
            self.voice.speak(text)

    def _print_confirmation_request(self, result):

        print(f"{self.ASTRA}{result.message}")

        if self.permissions.has_pending():
            print(f"{self.ASTRA}{self.permissions.describe_pending()}")

        print(f"{self.ASTRA}Confirm? (yes/no)")

        if self.debug and result.reasoning:
            analysis = result.reasoning["analysis"]
            print(f"  [debug] action={analysis['goal']} risk={analysis['risk']}")

    def _print_debug(self, result):

        print(f"  [debug] intent={result.intent.intent} confidence={result.intent.confidence}")

        if result.intent.entities:
            print(f"  [debug] entities={result.intent.entities}")

        if result.reasoning:
            decision = result.reasoning["decision"]["decision"]
            risk = result.reasoning["analysis"]["risk"]
            print(f"  [debug] decision={decision} risk={risk}")

    def _farewell(self):

        self.running = False
        message = "Goodbye."
        print(f"{self.ASTRA}{message}")
        print()
        self._speak(message)

        if self.logger:
            self.logger.info("REPL session ended")

    def _non_interactive_help(self):
        print(f"{self.ASTRA}This terminal cannot accept interactive input.")
        print()
        print("  Try one of these instead:")
        print("    python main.py --web     Open Web UI in browser")
        print("    python main.py --demo    Run automated demo")
        print("    astra.bat                Windows menu launcher")
        print()
        print("  Or open Windows Terminal / PowerShell and run:")
        print("    cd c:\\Astra\\astra-platform")
        print("    python main.py")
        print()
