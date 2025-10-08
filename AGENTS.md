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