import unittest
from src.models.relationship import RelationshipManager, RelationshipEvent, CharacterRelationship

class TestRelationshipManager(unittest.TestCase):

    def setUp(self):
        """Set up a new RelationshipManager for each test."""
        self.rm = RelationshipManager()

    def test_add_points_and_get_points(self):
        """Test adding points to a character."""
        self.rm.add_points("char1", 10, "test reason")
        self.assertEqual(self.rm.get_points("char1"), 10)
        self.rm.add_points("char1", -5, "test reason 2")
        self.assertEqual(self.rm.get_points("char1"), 5)
        self.assertEqual(self.rm.get_points("char2"), 0)

    def test_get_rank(self):
        """Test rank calculation based on points."""
        self.assertEqual(self.rm.get_rank("char1"), 0)
        self.rm.add_points("char1", 9, "test")
        self.assertEqual(self.rm.get_rank("char1"), 0)
        self.rm.add_points("char1", 1, "test")
        self.assertEqual(self.rm.get_rank("char1"), 1) # 10 points -> Rank 1
        self.rm.add_points("char1", 15, "test")
        self.assertEqual(self.rm.get_rank("char1"), 2) # 25 points -> Rank 2
        self.rm.add_points("char1", 25, "test")
        self.assertEqual(self.rm.get_rank("char1"), 3) # 50 points -> Rank 3

    def test_get_rank_name(self):
        """Test rank name retrieval."""
        self.assertEqual(self.rm.get_rank_name("char1"), "Neutral")
        self.rm.add_points("char1", 10, "test")
        self.assertEqual(self.rm.get_rank_name("char1"), "Friend")
        self.rm.add_points("char1", 15, "test")
        self.assertEqual(self.rm.get_rank_name("char1"), "Confidant")
        self.rm.add_points("char1", 25, "test")
        self.assertEqual(self.rm.get_rank_name("char1"), "Partner")

    def test_festival_interaction_simple(self):
        """Test the festival interaction hook with simple actions."""
        actions = [
            {"actor": "player", "target": "char1", "action_type": "give_charm"},
            {"actor": "player", "target": "char2", "action_type": "insult"},
        ]
        summary = self.rm.festival_interaction("festival1", actions)

        self.assertEqual(self.rm.get_points("char1"), 5)
        self.assertEqual(self.rm.get_points("char2"), -6)
        self.assertIn("processed", summary)
        self.assertEqual(len(summary["processed"]), 2)
        self.assertEqual(summary["points_changes"]["char1"], 5)
        self.assertEqual(summary["points_changes"]["char2"], -6)

    def test_festival_interaction_flags(self):
        """Test that festival interactions correctly set flags."""
        self.rm.add_points("char1", 25, "initial points") # Rank 2
        actions = [
            {"actor": "player", "target": "char1", "action_type": "insult"},
            {"actor": "player", "target": "char2", "action_type": "give_charm"},
        ]
        summary = self.rm.festival_interaction("festival2", actions)

        self.assertIn("festival_downgrade_warning:festival2:char1", summary["flags_set"])
        self.assertIn("festival_romance_interest:festival2:char2", summary["flags_set"])
        self.assertIn("festival_downgrade_warning:festival2:char1", self.rm.flags)

    def test_relationship_panel(self):
        """Test the structure of the relationship panel data."""
        self.rm.add_points("char1", 15, "reason")
        panel = self.rm.relationship_panel()

        self.assertIn("relationships", panel)
        self.assertIn("flags", panel)
        self.assertEqual(len(panel["relationships"]), 1)

        char1_data = panel["relationships"][0]
        self.assertEqual(char1_data["char_id"], "char1")
        self.assertEqual(char1_data["points"], 15)
        self.assertEqual(char1_data["rank"], 1)
        self.assertEqual(char1_data["rank_name"], "Friend")