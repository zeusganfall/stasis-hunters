from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Effect:
    """Represents an action that occurs in a scene."""
    type: str
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Scene:
    """Represents a single scene in the game."""
    id: str
    title: str
    content: str
    effects: List[Effect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        """Creates a Scene from a dictionary."""
        effects_data = data.get("effects", [])
        effects = [Effect(type=e["type"], params=e.get("params", {})) for e in effects_data]
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            effects=effects,
        )