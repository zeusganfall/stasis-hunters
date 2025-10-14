# High-level architecture

Minimal, clear, testable OOP model (JSON-driven):
- JSON config files (data/):
    - `chapters.json` (scene order, chapters)
    - `scenes/<scene_id>.json` (text, choices, seed placements)
    - `seeds.json` (seed metadata incl. `essential_for_payoff`, `date`, fallback)
    - `payoffs.json` (payoff definitions and gating flags)
    - `monsters.json`, `items.json`, `abilities.json`
    - `characters.json` (relationship thresholds, arcs)

- Python modules:
    - `game.py` — Game loop & CLI runner
    - `engine/scene.py` — Scene engine (choices, triggers, plant seeds)
    - `engine/chronicle.py` — Chronicle manager & save protection
    - `engine/save.py` — Save / load abstraction with protected region
    - `engine/combat.py` — Turn-based combat engine + AI behaviors
    - `engine/party.py` — Party & relationship manager
    - `engine/seed_tracker.py` — Seed → payoff validation + mirroring
    - `engine/ui.py` — Console UI helpers (menus, toasts)
    - `tests/` — pytest unit/integration tests

- Storage: JSON + single save file (pickled dict or JSON save) with clear protected sections; use human-readable JSON for saves to ease QA.

---

# Project timeline (phased by milestone)

Phases: Prototype → MVP → Alpha → Beta → Post-Beta. Each phase below is split into actionable stages; each stage has Acceptance Criteria (how you know it’s done), Technical Approach (developer / AI agent instructions), and Testing Steps (manual QA).

---

## PHASE: Prototype — prove the core loop & data-driven idea

Goal: Minimal playable loop (one scene → one combat → pickup seed → mirror to Chronicle → simple payoff gate).

### Stage P1 — Data model + minimal runner

- **Acceptance Criteria**
    - `seeds.json`, `scenes.json`, `payoffs.json` loadable.
    - CLI can run a single scene from JSON and show text + choices.

- **Technical Approach**
    - Define JSON schemas for `seed` and `scene` (see small example below).
    - Implement `engine/scene.py` to parse scene JSON and render text + choices.
    - Minimal `game.py` that loads config and runs one scene.

- **Testing Steps**
    - Run `python -m game --scene scene_festival` and verify scene text appears and choices accept input.
    - Manually check that seed entries referenced exist in `seeds.json`.

*Sample JSON snippet (seed):*
```json
{
  "id": "S05",
  "description": "Small shrine charm Hana gives Aki",
  "essential_for_payoff": true,
  "chapter_planted": 1
}
```

*Sample scene snippet (scene_festival.json):*
```json
{
  "id": "scene_festival",
  "text": "Lanterns float. Hana gives you a charm.",
  "seeds": ["S05"],
  "choices": [{"id":"take_charm","text":"Accept charm","next_scene":"scene_after_festival"}]
}
```

### Stage P2 — Chronicle mirroring + save flag basics

- **Acceptance Criteria**
    - Picking up an essential seed sets `flag_seed_<id>_found` and `flag_seed_<id>_mirrored_to_chronicle = true`.
    - Chronicle list shows protected badge in console.

- **Technical Approach**
    - Implement `engine/chronicle.py` with add(seed) that sets `protected: true` for seeds where `essential_for_payoff==true`.
    - Implement `save` with `chronicle_entries` area that is write-once (on save, refuse to remove entries).
    - Expose `ui.show_toast()` that prints `Protected in Chronicle`.

- **Testing Steps**
    - Play festival scene: pick up S05 → run `python inspect_chronicle.py` and verify S05 present + protected flag.

### Stage P3 — Very simple combat loop

- **Acceptance Criteria**
    - Menu-based, turn-based combat works for small infantry vs single enemy.
    - Basic initiative and one attack ability implemented.

- **Technical Approach**
    - Create `engine/combat.py` with `Combatant`, `Ability`, `CombatLoop`. Abilities are data-driven from `abilities.json`.
    - Use deterministic RNG seed for prototype runs for repeatability.

- **Testing Steps**
    - Start a combat via `python -m game --combat demo`; select attack; confirm enemy HP reduces and turn advances.

---

## PHASE: MVP — playable vertical slice (1–3 chapters) with core systems

Goal: A coherent, short playable chunk demonstrating seeds→payoff, relationship points, party, combat combos, and one payoff resolution.

### Stage M1 — Scene & branching engine + seed fallback enforcement

- **Acceptance Criteria**
    - Branching choices change available later scenes and fallback seeds appear if main seeds missed by the specified chapter.
    - The mid-boss fallback (e.g., S22) can drop if earlier seeds not found.

- **Technical Approach**
    - Implement `SceneState` with flags propagation to save and `scene_manager` that can evaluate conditions like `if not flag_seed_S01_found and chapter>=5 then spawn S22_fallback_scene`.
    - Encode fallbacks in seeds.json with `fallback_chapter` and `fallback_trigger`.

- **Testing Steps**
    - Play without picking S01 → reach fallback chapter → confirm fallback seed appears and payoffs still reachable.

### Stage M2 — Party & relationship system

- **Acceptance Criteria**
    - Party of up to 4 works; relationship points updated by choices; needed thresholds unlock simple partner combo in combat.

- **Technical Approach**
    - `engine/party.py` maintains `relationship_X_points`. Use characters.json to define thresholds (Friend/Confidant/Lover/Partner).
    - Implement partner combo as `Ability` unlocked when `relationship_points >= 60`.- **

- **Testing Steps**
    - Simulate actions that grant +points and verify combo ability appears in combat menu.

### Stage M3 — Memory-cost & Chronicle protection UI

- **Acceptance Criteria**
    - Player can trigger a Memory Cost action; a confirmation lists optional fragments to be removed and greys-out Chronicle-protected entries.
    - Attempting to remove protected item is blocked.

- **Technical Approach**
    - Memory Cost dialog built in `engine/ui.py`: show `chronicle_entries` first (grey, non-selectable), then optional fragments selectable.
    - Save code prevents changing `chronicle_entries` array contents.

- **Testing Steps**
    - Trigger a Memory Cost event; ensure protected seeds not selectable; perform removal and check non-protected fragments decrement.

### Stage M4 — Payoff gating & validation

- **Acceptance Criteria**
    - Reaching payoff P01 only happens if required Chronicle flags present (mirrored seeds found), otherwise fallback method triggers.

- **Technical Approach**
    - Implement `seed_tracker.check_payoff(payoff_id)` which validates required flags (`flag_seed_S01_mirrored_to_chronicle OR flag_seed_S03_mirrored_to_chronicle OR flag_seed_S22_mirrored_to_chronicle` for P01).

- **Testing Steps**
    - Create three runs: (a) all seeds found → payoff triggered; (b) none found → fallback payoff triggered; (c) some found → partial payoff path.

---

## PHASE: Alpha — full core feature set (complete combat, all chapters ingest, QA)

Goal: Ingest full content and implement combat depth, catalog monsters, relationships, romance rules incl. Festival punishment, S22 & S23 mirroring, and QA tests.

### Stage A1 — Content importer & JSON authoring tools

- **Acceptance Criteria**
    - All `scenes.json`, `seeds.json`, `payoffs.json`, `monsters.json`, `characters.json` imported and pass schema validation.

- **Technical Approach**
    - Write an `importer.py` that converts the design doc’s CSV/Markdown inputs into the canonical JSON schema; include schema validation (use `jsonschema`).

- **Testing Steps**
    - Run importer, check that every seed has `date`, `essential_for_payoff` field, fallback fields; run `pytest` schema validation.

### Stage A2 — Full combat engine + partner combos + enemy behaviors

- **Acceptance Criteria**
    - Multi-party (4) combats work; partner combos scale with relationship rank; enemy behaviors (stages/phases) function, including Engine Heart multi-phase.

- **Technical Approach**
    - Expand `engine/combat.py` with phase system, timed events, status effects (memory drain), tech pulse resource. Provide data-driven enemy AI scripts in `monsters.json`.
    - Provide a `CombatScenario` runner for scripted boss phases.

- **Testing Steps**
    - Play Finale scenario; confirm phases trigger and memory-drain works as specified.

### Stage A3 — Romance system + Festival-of-Lanterns punishment

- **Acceptance Criteria**
    - Romance points and states persist; festival multi-romance check at Chapter 8 downgrades romance→friendship and deducts memory fragment; flags set `flag_romance_multi_punishment_triggered` and `flag_romance_locked_until_rebuild`.

- **Technical Approach**
    - Implement relationship state machine with states and rank metadata. Add festival checkpoint runner that checks `count_active_romances >= 2` and executes pseudocode from doc.

- **Testing Steps**
    - Build save with 2 active romances, fast-forward to Ch8 → observe downgrade + memory fragment deduction + journal entry + autosave.

### Stage A4 — Full QA harness & tests for all payoffs

- **Acceptance Criteria**
    - Automated tests exist for every payoff’s Test A/B/C scenarios described in the document.

- **Technical Approach**
    - Create `tests/test_payoffs.py` using pytest to run scenario engine with different seed presences and assert payoff states and flags.

- **Testing Steps**
    - Run `pytest` and verify all payoff tests pass.

---

## PHASE: Beta — polishing, UX, localization, performance and broad playtests

Goal: polish UX, ensure localization readiness, fix pacing issues (Ch11–13), ensure no timeline contradictions, prepare release candidate.

### Stage B1 — UX polish & console ergonomics

- **Acceptance Criteria**
    - Menus look consistent; toasts and journal entries clearly show and are localizable; save/load robust.

- **Technical Approach**
    - Improve `engine/ui.py` with paginated text, clear choice keyboard mapping, and localization layers (strings in `lang/en.json`), and apply format placeholders.

- **Testing Steps**
    - Manual playthrough 3 different difficulty & branch runs; QA checklist for readability and save reliability.

### Stage B2 — Performance & stability

- **Acceptance Criteria**
    - No major memory leaks; load times for JSON < acceptable threshold on target machine.

- **Technical Approach**
    - Use lazy-loading for big assets; profile with cProfile if needed.

- **Testing Steps**
    - Long-play 6+ hour simulated automated run, confirm no crashes, and check save integrity after many saves.

### Stage B3 — External playtests & instrumented telemetry

- **Acceptance Criteria**
    - Playtest report from 10 players with bug list and pacing feedback addressing Ch11–13.

- **Technical Approach**
    - Add opt-in telemetry (local logfiles only) for choices leading to missing seeds/payoffs; collect logs to refine fallback timing and pain points.

- **Testing Steps**
    - Run a closed beta, collect logs, triage top 20 issues and verify resolution.

---

## PHASE: Post-Beta (release prep + post-launch)

Goal: finalize docs, package, add mod/data editing tools, create hotfix pipeline and roadmap for expansions.

### Stage PB1 — Packaging & installer

- **Acceptance Criteria**
    - Releaseable package (pip-installable CLI or standalone exe via PyInstaller) and a README with run instructions.

- **Technical Approach**
    - Create `setup.py` or `pyproject.toml`, PyInstaller spec for exe, create cross-platform run scripts.

- **Testing Steps**
    - Install on fresh VM and run follow-up playthrough; verify files and saves behave.

### Stage PB2 — Post-launch hotfix & mod tools

- **Acceptance Criteria**
    - Hotfix workflow documented and small update pushed; simple JSON editor or seed author tool shipped.

- **Technical Approach**
    - Add `tools/seed_editor.py` to edit seeds/payoffs safely; validate that edited files pass schema and tests.

- **Testing Steps**
    - Edit a seed with the tool, run schema validation and a smoke test playthrough.

---

# Technical details: schemas, core classes, and dev checklist (developer-friendly)

### Suggested minimal JSON schemas

- **Seed**
```json
{
  "id": "S05",
  "description": "Small shrine charm",
  "type": "item",
  "location": "Festival Shrine",
  "chapter_planted": 1,
  "discover_method": "pickup",
  "essential_for_payoff": true,
  "date": "2016-03-15",
  "fallback": null
}
```

- **Payoff**
```json
{
  "id": "P01",
  "required_mirrored_seeds": ["S01","S03","S22"],
  "chapter": 12,
  "canonical": true
}
```

### Core Python classes (sketch)
- `class Game`: load JSON, manage chapters and main loop.
- `class Scene`: text, seeds, choices, effects (flag ops).
- `class Seed`: metadata + `mirror_to_chronicle()` method.
- `class Chronicle`: `entries`, `add(seed)`, protect write-once.
- `class SaveManager`: `save()`, `load()`, `protect_chronicle_region()`.
- `class CombatEngine`: manage turn order, abilities, partner combos, enemy phases.
- `class PartyManager`: characters, relationship points, romance state machine.
- `class QAEngine`: scenario runner for automated payoff tests.

### Important implementation invariants (must enforce)
- `chronicle_entries` are write-once; any action that attempts to change them except `add` must throw an exception.
- Memory-cost UI must enumerate protected entries and block removal of chronicle entries.
- Payoff gating checks `flag_seed_<id>_mirrored_to_chronicle` exactly as the doc specifies to guarantee canonical payoffs.
- `flag_romance_multi_punishment_triggered` and `flag_romance_locked_until_rebuild` are set atomically during festival punishment with an autosave after toast.

---

# QA checklist (copy to CI / manual playtest)
- Schema validation: all JSON files validate with `jsonschema`.
- Seed mirroring tests: Acquire S22 & S23 via both normal and fallback paths; confirm chronicle flags set and protected.
- Payoff tests A/B/C for P01..P05 (as documented).
- Festival-punishment test: set up active romance flags >=2 by Ch8 and run festival, confirm downgrade and memory fragment deduction.
- Memory-cost test: attempt removal of protected item — must be blocked.
- Final boss (Engine Heart) multi-phase runs: confirm scripted narrative branches available depending on S23 presence.

---

# Final practical checklist (first files to create)
- `data/schema/*` (JSON schemas)
- `data/characters.json`, `data/seeds.json`, `data/payoffs.json`
- `engine/scene.py`, `engine/chronicle.py`, `engine/save.py`
- `game.py` simple runner + CLI
- `tests/test_payoffs.py` (pytest)