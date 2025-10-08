# src/tests/test_combat_engine.py
import unittest
import random
from typing import List, Tuple, Optional

from src.models.combat import Entity, Ability, CombatEngine


def fixed_action_selector(
    actor: Entity,
    abilities: List[Ability],
    targets: List[Entity],
    engine: CombatEngine
) -> Tuple[Ability, Entity, Optional[Entity]]:
    """A deterministic action selector for testing."""
    # Always choose the first available ability and the first available target.
    # This is simple and predictable for testing purposes.

    # Prioritize non-partner abilities to avoid complexity in this simple selector
    selected_ability = next((a for a in abilities if not a.requires_partner), abilities[0])

    # Find the target with the lowest HP
    target = min(targets, key=lambda t: t.hp)

    return selected_ability, target, None


class TestCombatEngine(unittest.TestCase):

    def setUp(self):
        """Set up a standard combat scenario."""
        self.players = [
            Entity(id="p1", name="Hero", hp=100, max_hp=100, speed=10, pulse=3, is_player=True),
            Entity(id="p2", name="Sidekick", hp=80, max_hp=80, speed=8, pulse=5, is_player=True),
        ]
        self.enemies = [
            Entity(id="e1", name="Goblin", hp=50, max_hp=50, speed=5, is_player=False),
            Entity(id="e2", name="Orc", hp=70, max_hp=70, speed=3, is_player=False),
        ]

    def test_deterministic_combat_outcome(self):
        """
        Verify that with a fixed seed, the combat outcome is always the same.
        """
        # --- Run 1 ---
        rng1 = random.Random(12345)
        engine1 = CombatEngine(
            players=[p for p in self.players],  # Use copies
            enemies=[e for e in self.enemies],
            rng=rng1
        )
        result1 = engine1.run(action_selector=fixed_action_selector)

        # --- Reset and Run 2 ---
        # Re-create entities to reset their state (hp, etc.)
        players_2 = [
            Entity(id="p1", name="Hero", hp=100, max_hp=100, speed=10, pulse=3, is_player=True),
            Entity(id="p2", name="Sidekick", hp=80, max_hp=80, speed=8, pulse=5, is_player=True),
        ]
        enemies_2 = [
            Entity(id="e1", name="Goblin", hp=50, max_hp=50, speed=5, is_player=False),
            Entity(id="e2", name="Orc", hp=70, max_hp=70, speed=3, is_player=False),
        ]
        rng2 = random.Random(12345) # Same seed
        engine2 = CombatEngine(
            players=players_2,
            enemies=enemies_2,
            rng=rng2
        )
        result2 = engine2.run(action_selector=fixed_action_selector)

        # --- Assertions ---
        self.assertEqual(result1["victory"], result2["victory"])
        self.assertEqual(result1["defeat"], result2["defeat"])
        self.assertEqual(result1["turn_count"], result2["turn_count"])

        # Check final HP states are identical
        self.assertEqual(result1["players"], result2["players"])
        self.assertEqual(result1["enemies"], result2["enemies"])

        # Also check the logs for good measure
        self.assertEqual(result1["log"], result2["log"])

    def test_victory_condition(self):
        """Test that combat correctly identifies a player victory."""
        rng = random.Random(1)
        # Make enemies very weak
        weak_enemies = [Entity(id="e1", name="Weakling", hp=1, max_hp=1, speed=1, is_player=False)]
        engine = CombatEngine(self.players, weak_enemies, rng=rng)
        result = engine.run(action_selector=fixed_action_selector)

        self.assertTrue(result["victory"])
        self.assertFalse(result["defeat"])

    def test_defeat_condition(self):
        """Test that combat correctly identifies a player defeat."""
        rng = random.Random(1)
        # Make players very weak
        weak_players = [Entity(id="p1", name="Fodder", hp=1, max_hp=1, speed=1, is_player=True)]
        engine = CombatEngine(weak_players, self.enemies, rng=rng)
        result = engine.run(action_selector=fixed_action_selector)

        self.assertFalse(result["victory"])
        self.assertTrue(result["defeat"])


if __name__ == "__main__":
    unittest.main()