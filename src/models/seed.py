from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Seed:
    id: str
    title: str
    payoff: str
    essential_for_payoff: bool
    mirrored_to_chronicle_on_pickup: bool
    chapter: int
    meta: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Seed":
        return cls(
            id=data["id"],
            title=data["title"],
            payoff=data["payoff"],
            essential_for_payoff=data["essential_for_payoff"],
            mirrored_to_chronicle_on_pickup=data["mirrored_to_chronicle_on_pickup"],
            chapter=data["chapter"],
            meta=data.get("meta", {}),
        )