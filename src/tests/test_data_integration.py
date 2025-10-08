import unittest
from src.data_loader import load_seeds, load_payoffs

class TestDataIntegration(unittest.TestCase):

    def test_load_real_data_files(self):
        """
        Tests loading the actual data from seeds.json and payoffs.json.
        This test will drive the necessary refactoring of the data loaders.
        """
        seeds_path = "src/data/seeds.json"
        payoffs_path = "src/data/payoffs.json"

        all_seeds = load_seeds(seeds_path)
        self.assertTrue(len(all_seeds) > 0, "No seeds were loaded from the file.")

        all_payoffs = load_payoffs(payoffs_path, all_seeds)
        self.assertTrue(len(all_payoffs) > 0, "No payoffs were loaded from the file.")

        # Check a specific payoff to ensure data is parsed correctly.
        p02 = all_payoffs.get("P02")
        self.assertIsNotNone(p02, "Payoff P02 not found.")

        # Check that the required seed IDs can be extracted correctly.
        required_ids = p02.get_required_seed_ids()
        self.assertIn("S05", required_ids)
        self.assertIn("S06", required_ids)

if __name__ == '__main__':
    unittest.main()