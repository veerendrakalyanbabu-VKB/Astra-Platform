from datetime import datetime
from pathlib import Path


class Logger:
    """
    Astra Logger
    """

    def __init__(self):

        Path("logs").mkdir(exist_ok=True)

        self.log_file = Path("logs/astra.log")

    def _write(self, level, message):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {level} : {message}"

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(line + "\n")

    def info(self, message):
        self._write("INFO", message)

    def warn(self, message):
        self._write("WARN", message)

    def error(self, message):
        self._write("ERROR", message)

    def debug(self, message):
        self._write("DEBUG", message)