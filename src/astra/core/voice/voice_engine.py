class VoiceEngine:
    """
    Speech input and output for Astra.
    ElevenLabs when ELEVENLABS_API_KEY is set; pyttsx3 offline fallback.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.stt_available = False
        self.tts_available = False
        self.tts_engine = "none"
        self._tts_engine = None
        self._elevenlabs = None
        self._recognizer = None

        if enabled:
            self._init_elevenlabs()
            self._init_tts()
            self._init_stt()

    def _init_elevenlabs(self) -> None:
        from astra.core.voice.elevenlabs_tts import ElevenLabsTTS

        self._elevenlabs = ElevenLabsTTS()
        if self._elevenlabs.enabled:
            self.tts_available = True
            self.tts_engine = "elevenlabs"

    def _init_tts(self) -> None:
        if self.tts_available:
            return

        try:
            import pyttsx3

            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty("rate", 175)
            self.tts_available = True
            self.tts_engine = "pyttsx3"

        except Exception:
            self.tts_available = False

    def _init_stt(self) -> None:
        try:
            import speech_recognition as sr

            self._recognizer = sr.Recognizer()
            self.stt_available = True

        except Exception:
            self.stt_available = False

    @property
    def ready(self) -> bool:
        return self.stt_available or self.tts_available

    def speak(self, text: str) -> bool:
        if not self.enabled or not self.tts_available or not text:
            return False

        if self._elevenlabs and self._elevenlabs.enabled:
            if self._elevenlabs.speak(text):
                return True

        if not self._tts_engine:
            return False

        try:
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()
            return True

        except Exception:
            return False

    def listen(self, timeout: int = 5, phrase_limit: int = 8) -> str:
        if not self.enabled or not self.stt_available:
            return ""

        import speech_recognition as sr

        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit,
                )

            text = self._recognizer.recognize_google(audio, language="en-US")
            return text.strip()

        except sr.WaitTimeoutError:
            return ""

        except sr.UnknownValueError:
            return ""

        except Exception:
            return ""

    def status(self) -> dict:
        return {
            "enabled": self.enabled,
            "speech_to_text": self.stt_available,
            "text_to_speech": self.tts_available,
            "tts_engine": self.tts_engine,
            "elevenlabs": bool(self._elevenlabs and self._elevenlabs.enabled),
        }
