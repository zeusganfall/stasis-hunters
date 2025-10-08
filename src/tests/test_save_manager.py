import unittest
import os
import json
from typing import Dict, Any

from src.models.seed import Seed
from src.models.chronicle import Chronicle
from src.persistence.save_manager import save_game, load_game, delete_fragment, validate_save


class TestSaveManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for save files."""
        self.test_dir = "temp_test_saves"
        os.makedirs(self.test_dir, exist_ok=True)
        self.save_path = os.path.join(self.test_dir, "savegame.json")

        # Sample data
        self.seed1 = Seed.from_dict({
            "id": "S01", "title": "Protected Seed", "payoff": "P01",
            "essential_for_payoff": True, "mirrored_to_chronicle_on_pickup": True,
            "chapter": 1, "meta": {}
        })
        self.seed2 = Seed.from_dict({
            "id": "S02", "title": "Unprotected Seed", "payoff": "P01",
            "essential_for_payoff": False, "mirrored_to_chronicle_on_pickup": False,
            "chapter": 1, "meta": {}
        })

        self.chronicle = Chronicle()
        self.chronicle.mirror(self.seed1)

        self.game_state = {
            "player_name": "Jules",
            "chronicle": self.chronicle,
            "world_items": {
                "S01": self.seed1.__dict__,
                "S02": self.seed2.__dict__,
            },
        }

    def tearDown(self):
        """Clean up the temporary directory."""
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
        os.rmdir(self.test_dir)

    def test_save_and_load_game(self):
        """Test that saving and loading a game state works correctly."""
        save_game(self.game_state, self.save_path)
        self.assertTrue(os.path.exists(self.save_path))

        loaded_state = load_game(self.save_path)
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state["player_name"], "Jules")

        # Check that the chronicle was correctly deserialized
        loaded_chronicle = loaded_state.get("chronicle")
        self.assertIsInstance(loaded_chronicle, Chronicle)
        self.assertTrue(loaded_chronicle.has("S01"))
        self.assertFalse(loaded_chronicle.has("S02"))

    def test_atomic_save(self):
        """Test that the save is atomic (resists corruption)."""
        # This is hard to test directly without process interruption,
        # but we can check that a valid file is created.
        save_game(self.game_state, self.save_path)

        # Check if the file is valid JSON
        try:
            with open(self.save_path, "r") as f:
                json.load(f)
        except json.JSONDecodeError:
            self.fail("save_game produced invalid JSON.")

    def test_delete_unprotected_fragment(self):
        """Test deleting a fragment that is NOT in the chronicle."""
        self.assertTrue(delete_fragment("S02", self.game_state))
        self.assertNotIn("S02", self.game_state["world_items"])

    def test_delete_protected_fragment(self):
        """Test that deleting a fragment in the chronicle is prevented."""
        self.assertFalse(delete_fragment("S01", self.game_state))
        self.assertIn("S01", self.game_state["world_items"])

    def test_validate_save_valid(self):
        """Test that a valid save state passes validation."""
        self.assertTrue(validate_save(self.game_state))

    def test_validate_save_invalid(self):
        """Test that an invalid save state fails validation."""
        # Case 1: Missing chronicle
        invalid_state_1 = self.game_state.copy()
        del invalid_state_1["chronicle"]
        self.assertFalse(validate_save(invalid_state_1))

        # Case 2: Chronicle is not a Chronicle object
        invalid_state_2 = self.game_state.copy()
        invalid_state_2["chronicle"] = "not a chronicle"
        self.assertFalse(validate_save(invalid_state_2))

        # Case 3 (conceptual): A protected entry is not protected
        # This requires manually creating a malformed chronicle
        malformed_chronicle = self.game_state["chronicle"]
        # This is a bit of a hack since our current implementation doesn't
        # allow creating unprotected entries easily. We'd have to manipulate internal state.
        entry = malformed_chronicle.list_entries()[0]
        entry.protected = False # Manually override protection

        self.assertFalse(validate_save(self.game_state))
        entry.protected = True # Reset for other tests

if __name__ == "__main__":
    unittest.main()