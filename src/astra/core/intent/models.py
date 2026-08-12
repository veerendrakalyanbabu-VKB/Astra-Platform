from dataclasses import dataclass
from typing import Dict


@dataclass
class IntentResult:
    intent: str
    entities: Dict
    confidence: float
