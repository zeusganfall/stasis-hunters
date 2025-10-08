from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Payoff:
    id: str
    description: str
    required_seeds: List[str]
    canonical: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payoff":
        return cls(
            id=data["id"],
            description=data["description"],
            required_seeds=data["required_seeds"],
            canonical=data["canonical"],
        )