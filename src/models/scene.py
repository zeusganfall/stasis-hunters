from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Effect:
    """Represents an action that occurs in a scene."""
    type: str
    params: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        """Creates an Effect from a dictionary, treating all keys except 'type' as params."""
        params = {k: v for k, v in data.items() if k != "type"}
        return cls(type=data["type"], params=params)


@dataclass
class Choice:
    """Represents a player choice in a scene."""
    id: str
    text: str
    effects: List[Effect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Choice":
        effects = [Effect.from_dict(e) for e in data.get("effects", [])]
        return cls(id=data["id"], text=data["text"], effects=effects)


@dataclass
class Scene:
    """Represents a single scene in the game."""
    id: str
    title: str
    content: str
    choices: List[Choice] = field(default_factory=list)
    # Optional top-level effects for scenes without choices
    effects: List[Effect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        """Creates a Scene from a dictionary."""
        choices = [Choice.from_dict(c) for c in data.get("choices", [])]
        effects = [Effect.from_dict(e) for e in data.get("effects", [])]
        return cls(
            id=data.get("id", "unknown_scene"),
            title=data.get("title", "Untitled Scene"),
            content=data.get("content", ""),
            choices=choices,
            effects=effects,
        )