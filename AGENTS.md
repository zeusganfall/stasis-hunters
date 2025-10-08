### AGENTS 

## Data layer & models
- [ ] `models/__init__.py`
    - Export dataclasses and convenience loaders.
- [ ] `models/seed.py`
    - Dataclass `Seed(id: str, title: str, payoff: str, essential_for_payoff: bool, mirrored_to_chronicle_on_pickup: bool, chapter: int, meta: dict)`.
    - `from_dict()` factory.
- [ ] `models/payoff.py`
    - Dataclass `Payoff(id: str, description: str, required_seeds: List[str], canonical: bool)`.
    - `from_dict()` factory.
- [ ] `data_loader.py`
    - Functions: `load_seeds(path) -> Dict[str, Seed]`, `load_payoffs(path) -> Dict[str, Payoff]`, `load_scene(path)`.
    - Add logging for malformed entries (fail loudly in dev).

**Acceptance:** JSON files parse into typed objects and validation runs (`required_seeds` must reference known seeds).

---

## Chronicle & SaveManager (write-once enforcement)
- [ ] `models/chronicle.py`
    - `Chronicle` class with methods:
        - `mirror(seed: Seed) -> bool` — add protected entry if not present.
        - `has(seed_id: str) -> bool`.
        - `list_entries() -> List[ChronicleEntry]`.
    - `ChronicleEntry` dataclass: `{id, data, protected: True, mirrored_at}`.
- [ ] `persistence/save_manager.py`
    - JSON-based save/load API:
        - `save_game(state: dict, path: str)`.
        - `load_game(path: str) -> dict`.
        - `delete_fragment(fragment_id: str)` — should refuse if fragment is present in `chronicle.entries`.
    - Implement atomic write (write-to-temp + rename) to avoid corrupt saves.
    - Add `validate_save()` that ensures all `chronicle.entries` remain write-once.

**Acceptance:** Attempting to delete a chronicle-mirrored seed returns an error and leaves save unchanged.