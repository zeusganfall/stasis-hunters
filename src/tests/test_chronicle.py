import unittest
import datetime
from typing import Dict, Any

from src.models.seed import Seed
from src.models.chronicle import Chronicle, ChronicleEntry


class TestChronicle(unittest.TestCase):

    def setUp(self):
        """Set up some sample seeds for testing."""
        self.seed1_data = {
            "id": "S01", "title": "Test Seed 1", "payoff": "P01",
            "essential_for_payoff": True, "mirrored_to_chronicle_on_pickup": True,
            "chapter": 1, "meta": {}
        }
        self.seed2_data = {
            "id": "S02", "title": "Test Seed 2", "payoff": "P01",
            "essential_for_payoff": False, "mirrored_to_chronicle_on_pickup": False,
            "chapter": 1, "meta": {}
        }
        self.seed1 = Seed.from_dict(self.seed1_data)
        self.seed2 = Seed.from_dict(self.seed2_data)

    def test_chronicle_entry_from_seed(self):
        """Test creating a ChronicleEntry from a Seed."""
        entry = ChronicleEntry.from_seed(self.seed1)
        self.assertEqual(entry.id, self.seed1.id)
        self.assertEqual(entry.data, self.seed1.__dict__)
        self.assertTrue(entry.protected)
        self.assertIsInstance(entry.mirrored_at, datetime.datetime)

    def test_mirror_new_seed(self):
        """Test that mirroring a new seed adds it to the chronicle."""
        chronicle = Chronicle()
        self.assertTrue(chronicle.mirror(self.seed1))
        self.assertTrue(chronicle.has("S01"))
        self.assertEqual(len(chronicle.list_entries()), 1)

    def test_mirror_existing_seed(self):
        """Test that mirroring an existing seed does not change the chronicle."""
        chronicle = Chronicle()
        chronicle.mirror(self.seed1)
        self.assertFalse(chronicle.mirror(self.seed1))
        self.assertEqual(len(chronicle.list_entries()), 1)

    def test_has_seed(self):
        """Test the 'has' method for presence and absence of a seed."""
        chronicle = Chronicle()
        chronicle.mirror(self.seed1)
        self.assertTrue(chronicle.has("S01"))
        self.assertFalse(chronicle.has("S02"))

    def test_list_entries(self):
        """Test that list_entries returns the correct list of entries."""
        chronicle = Chronicle()
        chronicle.mirror(self.seed1)
        chronicle.mirror(self.seed2)
        entries = chronicle.list_entries()
        self.assertEqual(len(entries), 2)
        self.assertIsInstance(entries[0], ChronicleEntry)
        entry_ids = {entry.id for entry in entries}
        self.assertEqual(entry_ids, {"S01", "S02"})

    def test_serialization_deserialization(self):
        """Test that a chronicle can be serialized to a dict and back."""
        chronicle = Chronicle()
        chronicle.mirror(self.seed1)

        # Add a slight delay to ensure timestamp is distinct
        # This is not strictly necessary but good for robust testing
        import time
        time.sleep(0.001)

        chronicle.mirror(self.seed2)

        serialized_data = chronicle.to_dict()
        self.assertIsInstance(serialized_data, list)
        self.assertEqual(len(serialized_data), 2)
        self.assertEqual(serialized_data[0]["id"], self.seed1.id)
        self.assertIsInstance(serialized_data[0]["mirrored_at"], str)

        deserialized_chronicle = Chronicle.from_dict(serialized_data)
        self.assertIsInstance(deserialized_chronicle, Chronicle)
        self.assertTrue(deserialized_chronicle.has("S01"))
        self.assertTrue(deserialized_chronicle.has("S02"))

        # Verify that the objects are equal in content
        original_entries = sorted(chronicle.list_entries(), key=lambda e: e.id)
        new_entries = sorted(deserialized_chronicle.list_entries(), key=lambda e: e.id)

        self.assertEqual(len(original_entries), len(new_entries))
        for i in range(len(original_entries)):
            self.assertEqual(original_entries[i].id, new_entries[i].id)
            self.assertEqual(original_entries[i].data, new_entries[i].data)
            self.assertEqual(original_entries[i].protected, new_entries[i].protected)
            # Timestamps should be very close, allowing for float precision
            self.assertAlmostEqual(
                original_entries[i].mirrored_at.timestamp(),
                new_entries[i].mirrored_at.timestamp(),
                delta=0.001
            )

if __name__ == "__main__":
    unittest.main()