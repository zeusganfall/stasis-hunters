import json
import unittest
from unittest.mock import patch, mock_open

from src.models import Seed, Payoff
from src.data_loader import load_seeds, load_payoffs

class TestDataLoader(unittest.TestCase):

    def setUp(self):
        self.seeds_data = [
            {
                "id": "seed1",
                "title": "Seed 1",
                "payoff": "payoff1",
                "essential_for_payoff": True,
                "mirrored_to_chronicle_on_pickup": True,
                "chapter": 1,
                "meta": {}
            }
        ]
        self.payoffs_data = [
            {
                "id": "payoff1",
                "title": "Payoff 1 Title",
                "description": "Payoff 1",
                "required_seeds": {
                    "mode": "any_of",
                    "seeds": [{"id": "seed1", "must_be_mirrored": True, "priority": 1}]
                },
                "fallbacks": [],
                "trigger_window": {"earliest_chapter": 1, "latest_chapter": 9},
                "canonical": True,
                "consequence": {"type": "mechanic", "data": {}},
                "completion_flag": "payoff1_completed",
                "validation": {"strict": True, "error_on_violation": True},
                "notes": ""
            }
        ]

    def test_load_seeds_success(self):
        m = mock_open(read_data=json.dumps(self.seeds_data))
        with patch("builtins.open", m):
            seeds = load_seeds("dummy_path.json")
            self.assertIn("seed1", seeds)
            self.assertIsInstance(seeds["seed1"], Seed)
            self.assertEqual(seeds["seed1"].title, "Seed 1")
            self.assertEqual(len(seeds), 1)

    def test_load_payoffs_success(self):
        m_seeds = mock_open(read_data=json.dumps(self.seeds_data))
        m_payoffs = mock_open(read_data=json.dumps(self.payoffs_data))

        with patch("builtins.open", m_seeds):
            all_seeds = load_seeds("dummy_seeds.json")

        with patch("builtins.open", m_payoffs):
            payoffs = load_payoffs("dummy_payoffs.json", all_seeds)
            self.assertIn("payoff1", payoffs)
            self.assertIsInstance(payoffs["payoff1"], Payoff)
            self.assertEqual(payoffs["payoff1"].description, "Payoff 1")
            self.assertEqual(len(payoffs), 1)

    def test_load_payoffs_invalid_seed_ref(self):
        invalid_payoffs_data = [
            {
                "id": "payoff2",
                "title": "Payoff 2 Title",
                "description": "Payoff 2",
                "required_seeds": {
                    "mode": "any_of",
                    "seeds": [{"id": "non_existent_seed", "must_be_mirrored": True, "priority": 1}]
                },
                "fallbacks": [],
                "trigger_window": {"earliest_chapter": 1, "latest_chapter": 9},
                "canonical": False,
                "consequence": {"type": "mechanic", "data": {}},
                "completion_flag": "payoff2_completed",
                "validation": {"strict": True, "error_on_violation": True},
                "notes": ""
            }
        ]
        m_seeds = mock_open(read_data=json.dumps(self.seeds_data))
        m_payoffs = mock_open(read_data=json.dumps(invalid_payoffs_data))

        with patch("builtins.open", m_seeds):
            all_seeds = load_seeds("dummy_seeds.json")

        with patch("builtins.open", m_payoffs):
            with self.assertLogs("src.data_loader", level="ERROR") as cm:
                payoffs = load_payoffs("dummy_payoffs.json", all_seeds)
                self.assertEqual(len(payoffs), 0)
                self.assertIn(
                    "references an unknown seed 'non_existent_seed'",
                    cm.output[0],
                )

if __name__ == "__main__":
    unittest.main()