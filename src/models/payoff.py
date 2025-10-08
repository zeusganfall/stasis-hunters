from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Payoff:
    id: str
    description: str
    required_seeds: Dict[str, Any]
    canonical: bool
    # The JSON files have more fields, but we only need these for now.
    # We can add them later if needed.

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payoff":
        return cls(
            id=data["id"],
            description=data["description"],
            required_seeds=data["required_seeds"],
            canonical=data["canonical"],
        )

    def get_required_seed_ids(self) -> List[str]:
        """Extracts seed IDs from the complex required_seeds object."""
        if "seeds" in self.required_seeds and isinstance(self.required_seeds["seeds"], list):
            return [seed.get("id") for seed in self.required_seeds["seeds"] if "id" in seed]
        return []