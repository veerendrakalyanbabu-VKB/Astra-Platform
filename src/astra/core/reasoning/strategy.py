from dataclasses import dataclass


@dataclass
class Strategy:

    name: str

    steps: list

    confidence: float = 1.0