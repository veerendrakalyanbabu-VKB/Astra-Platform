from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ActionResult:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = field(default_factory=dict)
    error: Optional[str] = None
