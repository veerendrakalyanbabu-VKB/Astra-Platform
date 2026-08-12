from dataclasses import dataclass


@dataclass
class Goal:

    name: str

    description: str

    priority: int = 1