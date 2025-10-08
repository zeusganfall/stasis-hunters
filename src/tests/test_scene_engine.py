import unittest
from typing import Dict, List

from src.models.chronicle import Chronicle
from src.models.scene import Scene, Effect
from src.models.seed import Seed
from src.scene_engine import SceneEngine


class TestSceneEngine(unittest.TestCase):
    def setUp(self):
        """Set up a common test environment."""
        self.all_seeds: Dict[str, Seed] = {
            "S01": Seed(
                id="S01",
                title="A Normal Seed",
                payoff="P01",
                essential_for_payoff=False,
                mirrored_to_chronicle_on_pickup=False,
                chapter=1,
                meta={},
            ),
            "S05": Seed(
                id="S05",
                title="A Mirrored Seed",
                payoff="P01",
                essential_for_payoff=False,
                mirrored_to_chronicle_on_pickup=True,
                chapter=1,
                meta={},
            ),
            "S08": Seed(
                id="S08",
                title="An Essential Seed",
                payoff="P02",
                essential_for_payoff=True,
                mirrored_to_chronicle_on_pickup=False,
                chapter=1,
                meta={},
            ),
        }
        self.chronicle = Chronicle()
        self.inventory: List[str] = []
        self.scene_engine = SceneEngine(
            all_seeds=self.all_seeds,
            chronicle=self.chronicle,
            inventory=self.inventory,
        )

    def test_pickup_seed_normal(self):
        """Verify picking up a standard seed adds it to inventory but not chronicle."""
        scene = Scene(
            id="test_scene_1",
            title="Test Scene",
            content="A scene for testing.",
            effects=[Effect(type="pickup_seed", params={"id": "S01"})],
        )
        self.scene_engine.process_effects(scene.effects)

        self.assertIn("S01", self.inventory)
        self.assertFalse(self.chronicle.has("S01"))

    def test_pickup_seed_mirrored(self):
        """Verify picking up a mirrored seed adds it to inventory and chronicle."""
        scene = Scene(
            id="test_scene_2",
            title="Mirrored Seed Test",
            content="A scene for testing mirrored seeds.",
            effects=[Effect(type="pickup_seed", params={"id": "S05"})],
        )
        self.scene_engine.process_effects(scene.effects)

        self.assertIn("S05", self.inventory)
        self.assertTrue(self.chronicle.has("S05"))

    def test_pickup_seed_essential(self):
        """Verify picking up an essential seed adds it to inventory and chronicle."""
        scene = Scene(
            id="test_scene_3",
            title="Essential Seed Test",
            content="A scene for testing essential seeds.",
            effects=[Effect(type="pickup_seed", params={"id": "S08"})],
        )
        self.scene_engine.process_effects(scene.effects)

        self.assertIn("S08", self.inventory)
        self.assertTrue(self.chronicle.has("S08"))

    def test_pickup_nonexistent_seed(self):
        """Verify that picking up a nonexistent seed does not change state."""
        scene = Scene(
            id="test_scene_4",
            title="Nonexistent Seed Test",
            content="A scene for testing nonexistent seeds.",
            effects=[Effect(type="pickup_seed", params={"id": "S99"})],
        )
        self.scene_engine.process_effects(scene.effects)

        self.assertEqual(len(self.inventory), 0)
        self.assertEqual(len(self.chronicle.list_entries()), 0)

    def test_process_scene_with_multiple_effects(self):
        """Verify correct processing of a scene with multiple effects."""
        scene = Scene(
            id="test_scene_5",
            title="Multi-effect Test",
            content="A scene for testing multiple effects.",
            effects=[
                Effect(type="pickup_seed", params={"id": "S01"}),
                Effect(type="pickup_seed", params={"id": "S05"}),
            ],
        )
        self.scene_engine.process_effects(scene.effects)

        self.assertIn("S01", self.inventory)
        self.assertIn("S05", self.inventory)
        self.assertFalse(self.chronicle.has("S01"))
        self.assertTrue(self.chronicle.has("S05"))


if __name__ == "__main__":
    unittest.main()