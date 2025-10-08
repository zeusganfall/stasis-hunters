import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from src.models.seed import Seed


@dataclass
class ChronicleEntry:
    """Represents a write-once entry in the Chronicle, mirrored from a Seed."""

    id: str
    data: Dict[str, Any]
    protected: bool = True
    mirrored_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    @classmethod
    def from_seed(cls, seed: Seed) -> "ChronicleEntry":
        """Creates a ChronicleEntry from a Seed instance."""
        return cls(id=seed.id, data=seed.__dict__)


class Chronicle:
    """
    A write-once ledger for critical game events, ensuring that once a seed is
    mirrored, it cannot be removed or altered.
    """

    def __init__(self, entries: Optional[List[ChronicleEntry]] = None):
        self._entries: Dict[str, ChronicleEntry] = {e.id: e for e in entries} if entries else {}

    def mirror(self, seed: Seed) -> bool:
        """
        Adds a seed to the chronicle if it's not already present.

        Args:
            seed: The Seed to mirror.

        Returns:
            True if the seed was newly mirrored, False otherwise.
        """
        if not self.has(seed.id):
            entry = ChronicleEntry.from_seed(seed)
            self._entries[entry.id] = entry
            return True
        return False

    def has(self, seed_id: str) -> bool:
        """Checks if a seed with the given ID is in the chronicle."""
        return seed_id in self._entries

    def list_entries(self) -> List[ChronicleEntry]:
        """Returns a list of all entries in the chronicle."""
        return list(self._entries.values())

    def to_dict(self) -> List[Dict[str, Any]]:
        """Serializes the chronicle's entries to a list of dictionaries."""
        return [
            {
                "id": entry.id,
                "data": entry.data,
                "protected": entry.protected,
                "mirrored_at": entry.mirrored_at.isoformat(),
            }
            for entry in self.list_entries()
        ]

    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> "Chronicle":
        """Deserializes a list of dictionaries into a Chronicle instance."""
        entries = []
        for entry_data in data:
            entry_data["mirrored_at"] = datetime.datetime.fromisoformat(entry_data["mirrored_at"])
            # Reconstruct the ChronicleEntry object
            # Note: The 'data' field in the dictionary is the original Seed's dict.
            # We don't need to reconstruct the full Seed object here, just the entry.
            entries.append(ChronicleEntry(**entry_data))
        return cls(entries)