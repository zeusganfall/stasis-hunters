import unittest
from unittest.mock import Mock, MagicMock
from src.models.payoff import Payoff, RequiredSeeds, RequiredSeed, Fallback, TriggerWindow, Consequence, Validation
from src.payoff_manager import PayoffManager
from src.models.chronicle import Chronicle

class TestPayoffManager(unittest.TestCase):

    def setUp(self):
        # A mock payoff for testing
        self.payoff_P02 = Payoff(
            id="P02",
            title="Test Payoff",
            description="A test payoff.",
            required_seeds=RequiredSeeds(
                mode="any_of",
                seeds=[
                    RequiredSeed(id="S05", must_be_mirrored=True, priority=1),
                    RequiredSeed(id="S06", must_be_mirrored=True, priority=2)
                ]
            ),
            fallbacks=[
                Fallback(
                    missing_seed="S05",
                    alternatives=["S07"],
                    deadline_chapter=3,
                    priority=10,
                    note=""
                )
            ],
            trigger_window=TriggerWindow(earliest_chapter=1, latest_chapter=9),
            canonical=True,
            consequence=Consequence(type="mechanic", data={}),
            completion_flag="payoff_P02_completed",
            validation=Validation(strict=True, error_on_violation=True),
            notes=""
        )

        self.payoffs = {"P02": self.payoff_P02}
        self.payoff_manager = PayoffManager(self.payoffs)

    def test_can_trigger_payoff_primary_seed_present(self):
        """Payoff should trigger if a primary required seed is in the chronicle."""
        mock_chronicle = MagicMock(spec=Chronicle)
        mock_chronicle.has.side_effect = lambda seed_id: seed_id == "S05"

        result = self.payoff_manager.can_trigger_payoff("P02", mock_chronicle, current_chapter=2)
        self.assertTrue(result)
        mock_chronicle.has.assert_any_call("S05")

    def test_cannot_trigger_payoff_seeds_missing(self):
        """Payoff should NOT trigger if no required seeds are present."""
        mock_chronicle = MagicMock(spec=Chronicle)
        mock_chronicle.has.return_value = False

        result = self.payoff_manager.can_trigger_payoff("P02", mock_chronicle, current_chapter=2)
        self.assertFalse(result)

    def test_can_trigger_payoff_via_fallback(self):
        """Payoff should trigger if a fallback seed is present and within deadline."""
        mock_chronicle = MagicMock(spec=Chronicle)
        # S05 and S06 are missing, but fallback S07 is present.
        mock_chronicle.has.side_effect = lambda seed_id: seed_id == "S07"

        result = self.payoff_manager.can_trigger_payoff("P02", mock_chronicle, current_chapter=3)
        self.assertTrue(result)
        # S05 and S06 should be checked first
        mock_chronicle.has.assert_any_call("S05")
        mock_chronicle.has.assert_any_call("S06")
        # Then the fallback S07 should be checked
        mock_chronicle.has.assert_any_call("S07")

    def test_cannot_trigger_payoff_fallback_deadline_passed(self):
        """Payoff should NOT trigger if the fallback deadline has passed."""
        mock_chronicle = MagicMock(spec=Chronicle)
        mock_chronicle.has.side_effect = lambda seed_id: seed_id == "S07"

        # Chapter 4 is after the deadline of 3
        result = self.payoff_manager.can_trigger_payoff("P02", mock_chronicle, current_chapter=4)
        self.assertFalse(result)

    def test_cannot_trigger_payoff_already_completed(self):
        """Payoff should NOT trigger if its completion flag is already set."""
        mock_chronicle = MagicMock(spec=Chronicle)
        mock_chronicle.has.return_value = True # Assume seeds are present

        game_flags = {"payoff_P02_completed": True}
        result = self.payoff_manager.can_trigger_payoff("P02", mock_chronicle, current_chapter=2, game_flags=game_flags)
        self.assertFalse(result)

    def test_cannot_trigger_payoff_outside_trigger_window(self):
        """Payoff should NOT trigger if current chapter is outside the trigger window."""
        mock_chronicle = MagicMock(spec=Chronicle)
        mock_chronicle.has.return_value = True # Assume seeds are present

        # Before window
        result_before = self.payoff_manager.can_trigger_payoff("P02", mock_chronicle, current_chapter=0)
        self.assertFalse(result_before)

        # After window
        result_after = self.payoff_manager.can_trigger_payoff("P02", mock_chronicle, current_chapter=10)
        self.assertFalse(result_after)

if __name__ == "__main__":
    unittest.main()