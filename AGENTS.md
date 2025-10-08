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
- [x] `models/chronicle.py`
    - `Chronicle` class with methods:
        - `mirror(seed: Seed) -> bool` — add protected entry if not present.
        - `has(seed_id: str) -> bool`.
        - `list_entries() -> List[ChronicleEntry]`.
    - `ChronicleEntry` dataclass: `{id, data, protected: True, mirrored_at}`.
- [x] `persistence/save_manager.py`
    - JSON-based save/load API:
        - `save_game(state: dict, path: str)`.
        - `load_game(path: str) -> dict`.
        - `delete_fragment(fragment_id: str)` — should refuse if fragment is present in `chronicle.entries`.
    - Implement atomic write (write-to-temp + rename) to avoid corrupt saves.
    - Add `validate_save()` that ensures all `chronicle.entries` remain write-once.

**Acceptance:** Attempting to delete a chronicle-mirrored seed returns an error and leaves save unchanged.

---

## SceneEngine & seed pickup flow
- [x] `scene_engine.py`
    - `SceneEngine` loads scene JSON, renders content via UI, processes `effects` array (e.g., `pickup_seed`).
    - On `pickup_seed`:
        - Add seed to player inventory/flags.
        - If `seed.mirrored_to_chronicle_on_pickup` OR `seed.essential_for_payoff` → call `Chronicle.mirror(seed)`.
    - Emit events/logs for triggers (use simple EventBus or callback hooks).
- [x] **Scene JSON spec doc**
    - Document allowed effect types: `pickup_seed`, `trigger_combat`, `give_item`, `add_rel_points`, `transition_chapter`.

**Acceptance:** Picking S05 in ch1_festival results in `chronicle.has("S05") == True` immediately.

---

## CombatEngine (minimal deterministic system)
- [x] `models/combat.py`
    - Implement classes: `Entity`, `Ability`, `CombatEngine`.
    - Abilities: `attack`, `ritual` (requires warm-up), `tech` (consumes pulse).
    - Relationship-based combos: `if relationship.rank >= X` → unlock `partner_combo`.
    - Deterministic RNG: `CombatEngine(seed)` parameterized.
- [x] **Combat CLI hooks**
    - Command-line choices: attack, ritual, tech, use-item, pass.
- [x] **Combat tests**
    - Deterministic scenarios (seeded RNG) assert exact HP changes.

**Acceptance:** A scripted combat scenario with RNG seed yields stable results across runs.

---

## RelationshipManager & festival mechanics
- [x] `models/relationship.py`
    - Track per-character `points`, compute `rank` (thresholds).
    - API to `add_points(char_id, amount, reason)`.
- [x] Festival interaction
    - Implement festival timeline hook that can change relationship ranks and optionally apply downgrade flags (but do not auto-run major punishments in MVP).
- [x] UI display
    - Relationship panel showing points and rank.

**Acceptance:** Relationship points change from specific events and are readable in UI.