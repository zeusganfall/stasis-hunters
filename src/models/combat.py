# src/models/combat.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional, Tuple
import random
import math

# --- Basic dataclasses -----------------------------------------------------

@dataclass
class Entity:
    id: str
    name: str
    hp: int
    max_hp: int
    speed: int
    pulse: int = 0            # tech resource
    is_player: bool = True
    rel_id: Optional[str] = None  # relationship key for partner combos
    alive: bool = True
    # optional custom payload (loot, seed drops)
    meta: Dict = field(default_factory=dict)

    def take_damage(self, amount: int):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

@dataclass
class Ability:
    id: str
    name: str
    base_power: int
    cost_pulse: int = 0
    kind: str = "attack"  # "attack", "ritual", "tech", "support"
    charge_turns: int = 0  # for ritual-style abilities
    requires_partner: bool = False

# --- CombatEngine ---------------------------------------------------------

class CombatEngine:
    """
    Minimal deterministic turn-based combat engine.
    Usage:
      rng = random.Random(12345)
      engine = CombatEngine(players, enemies, rng=rng, relationship_lookup=...)
      engine.run(auto_action_selector=some_fn)
    """

    def __init__(
        self,
        players: List[Entity],
        enemies: List[Entity],
        rng: Optional[random.Random] = None,
        relationship_lookup: Optional[Callable[[str], int]] = None,
        on_enemy_defeat: Optional[Callable[[Entity], None]] = None,
    ):
        self.players = players
        self.enemies = enemies
        self.rng = rng if rng is not None else random.Random(0)
        # mapping rel_id -> rank int (0..N)
        self.relationship_lookup = relationship_lookup or (lambda rel_id: 0)
        self.on_enemy_defeat = on_enemy_defeat
        self.turn_count = 0
        self._charge_counters: Dict[Tuple[str, str], int] = {}  # (actor_id, ability_id) -> remaining turns

    # Convenience views
    @property
    def participants(self) -> List[Entity]:
        return [e for e in (self.players + self.enemies) if e.alive]

    def _initiative_order(self) -> List[Entity]:
        # sort by speed desc; ties use rng.choice deterministic via shuffle with rng
        bucket = sorted(self.participants, key=lambda e: e.speed, reverse=True)
        # resolve exact ties deterministically: stable sort by id seeded shuffle
        # we'll group by speed, then shuffle each group deterministically
        groups: Dict[int, List[Entity]] = {}
        for e in bucket:
            groups.setdefault(e.speed, []).append(e)
        ordered = []
        for speed in sorted(groups.keys(), reverse=True):
            group = groups[speed][:]
            # deterministic shuffle using engine rng
            self.rng.shuffle(group)
            ordered.extend(group)
        return ordered

    # --- Abilities / action resolution -----------------------------------

    def _calc_damage(self, attacker: Entity, target: Entity, ability: Ability) -> int:
        # core formula: base_power * (1 + pulse_factor) +/- small rng variance
        pulse_factor = (attacker.pulse / 10) if attacker.pulse > 0 else 0
        raw = ability.base_power * (1.0 + pulse_factor)
        # small deterministic variance: rng.random() in [0, 1)
        variance = (self.rng.random() - 0.5) * 0.1  # +/-5%
        dmg = math.floor(max(0, raw * (1.0 + variance)))
        return int(dmg)

    def _apply_ability(self, actor: Entity, target: Entity, ability: Ability) -> Dict:
        # check costs
        if ability.cost_pulse and actor.pulse < ability.cost_pulse:
            return {"success": False, "reason": "not_enough_pulse"}

        if ability.charge_turns > 0:
            # start charge counter
            self._charge_counters[(actor.id, ability.id)] = ability.charge_turns
            return {"success": True, "action": "charging", "turns": ability.charge_turns}

        # if it's a partner ability requiring partner, caller must ensure partner performed partner action
        damage = 0
        if ability.kind in ("attack", "tech", "ritual"):
            damage = self._calc_damage(actor, target, ability)
            target.take_damage(damage)
        # consume pulse if any
        if ability.cost_pulse:
            actor.pulse -= ability.cost_pulse
            if actor.pulse < 0:
                actor.pulse = 0

        return {"success": True, "damage": damage}

    # call every turn to decrement charge counters and resolve if zero
    def _tick_charges(self):
        to_resolve = []
        keys = list(self._charge_counters.keys())
        for k in keys:
            self._charge_counters[k] -= 1
            if self._charge_counters[k] <= 0:
                to_resolve.append(k)
                del self._charge_counters[k]
        return to_resolve  # list of (actor_id, ability_id) ready to resolve by engine user

    # --- Public API -------------------------------------------------------

    def is_victory(self) -> bool:
        # players win when all enemies dead
        return all(not e.alive for e in self.enemies)

    def is_defeat(self) -> bool:
        # defeat when all players dead
        return all(not p.alive for p in self.players)

    def available_targets(self, actor: Entity) -> List[Entity]:
        if actor.is_player:
            return [e for e in self.enemies if e.alive]
        else:
            return [p for p in self.players if p.alive]

    def run(
        self,
        action_selector: Callable[[Entity, List[Ability], List[Entity], "CombatEngine"], Tuple[Ability, Entity, Optional[Entity]]],
        max_turns: int = 100,
    ) -> Dict:
        """
        action_selector(actor, abilities, targets, engine) -> (ability, target, partner_entity_or_none)
        - abilities: caller can supply a small list of standard abilities, or build per-actor logic
        """
        # small register of standard abilities; real system should be data-driven
        default_abilities = {
            "attack": Ability("A_attack", "Strike", base_power=10, cost_pulse=0, kind="attack"),
            "ritual": Ability("A_ritual", "Ritual Strike", base_power=6, cost_pulse=0, kind="ritual", charge_turns=1),
            "tech": Ability("A_tech", "Pulse Blast", base_power=12, cost_pulse=2, kind="tech"),
            "partner_combo": Ability("A_combo", "Partner Combo", base_power=20, cost_pulse=1, kind="tech", requires_partner=True),
        }

        log = {"turns": []}
        while max_turns > 0 and not (self.is_victory() or self.is_defeat()):
            self.turn_count += 1
            order = self._initiative_order()
            # tick charges at start of turn (actors may resolve charged abilities)
            resolved_charges = self._tick_charges()
            if resolved_charges:
                for (actor_id, ability_id) in resolved_charges:
                    # naive resolution: apply a default ritual resolution to a random enemy/player
                    actor = next((x for x in self.participants if x.id == actor_id), None)
                    if actor is None or not actor.alive:
                        continue
                    # find target group
                    targets = self.available_targets(actor)
                    if not targets:
                        continue
                    target = self.rng.choice(targets)
                    ability = default_abilities.get("ritual")
                    res = self._apply_ability(actor, target, ability)
                    log["turns"].append({"event": "charge_resolve", "actor": actor.id, "ability": ability.id, "result": res})

            for actor in order:
                if not actor.alive:
                    continue
                abilities = list(default_abilities.values())
                targets = self.available_targets(actor)
                if not targets:
                    continue
                ability, target, partner = action_selector(actor, abilities, targets, self)
                # Handle partner combo: if ability.requires_partner, check partner availability and relationship rank
                if ability.requires_partner:
                    if partner is None:
                        log["turns"].append({"actor": actor.id, "action": "failed_partner_missing"})
                        continue
                    # check relationship rank
                    if actor.rel_id is None or partner.rel_id is None:
                        log["turns"].append({"actor": actor.id, "action": "failed_partner_no_rel_id"})
                        continue
                    rank = self.relationship_lookup(actor.rel_id)
                    if rank < 2:  # simple threshold for MVP
                        log["turns"].append({"actor": actor.id, "action": "failed_partner_rank_too_low", "rank": rank})
                        continue
                    # both actors perform a combined resolution: apply combined damage to target
                    combined_power = ability.base_power + (partner.pulse // 2)
                    # deterministic small variation
                    variance = (self.rng.random() - 0.5) * 0.05
                    dmg = math.floor(max(0, combined_power * (1.0 + variance)))
                    target.take_damage(dmg)
                    partner.pulse = max(0, partner.pulse - ability.cost_pulse)
                    actor.pulse = max(0, actor.pulse - ability.cost_pulse)
                    log["turns"].append({"actor": actor.id, "partner": partner.id, "ability": ability.id, "damage": dmg})
                else:
                    res = self._apply_ability(actor, target, ability)
                    log["turns"].append({"actor": actor.id, "ability": ability.id, "target": target.id, "result": res})
                    # if target died, call on_enemy_defeat hook for enemies
                    if not target.alive and target in self.enemies:
                        if self.on_enemy_defeat:
                            self.on_enemy_defeat(target)

            max_turns -= 1

        result = {
            "victory": self.is_victory(),
            "defeat": self.is_defeat(),
            "turn_count": self.turn_count,
            "log": log,
            "players": [{ "id": p.id, "hp": p.hp, "alive": p.alive } for p in self.players],
            "enemies": [{ "id": e.id, "hp": e.hp, "alive": e.alive } for e in self.enemies],
        }
        return result
