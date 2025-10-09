from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class RequiredSeed:
    id: str
    must_be_mirrored: bool
    priority: int

@dataclass
class RequiredSeeds:
    mode: str
    seeds: List[RequiredSeed]

@dataclass
class Fallback:
    missing_seed: str
    alternatives: List[str]
    deadline_chapter: int
    priority: int
    note: str

@dataclass
class TriggerWindow:
    earliest_chapter: int
    latest_chapter: int

@dataclass
class Consequence:
    type: str
    data: Dict[str, Any]

@dataclass
class Validation:
    strict: bool
    error_on_violation: bool

@dataclass
class Payoff:
    id: str
    title: str
    description: str
    required_seeds: RequiredSeeds
    fallbacks: List[Fallback]
    trigger_window: TriggerWindow
    canonical: bool
    consequence: Consequence
    completion_flag: str
    validation: Validation
    notes: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payoff":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            required_seeds=RequiredSeeds(
                mode=data["required_seeds"]["mode"],
                seeds=[RequiredSeed(**seed_data) for seed_data in data["required_seeds"]["seeds"]],
            ),
            fallbacks=[Fallback(**fallback_data) for fallback_data in data["fallbacks"]],
            trigger_window=TriggerWindow(**data["trigger_window"]),
            canonical=data["canonical"],
            consequence=Consequence(**data["consequence"]),
            completion_flag=data["completion_flag"],
            validation=Validation(**data["validation"]),
            notes=data["notes"],
        )