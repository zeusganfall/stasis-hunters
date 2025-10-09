from typing import Dict, List
from src.models.payoff import Payoff, RequiredSeed
from src.models.chronicle import Chronicle

class PayoffManager:
    def __init__(self, payoffs: Dict[str, Payoff]):
        self.payoffs = payoffs

    def _check_seeds(self, required: List[RequiredSeed], chronicle: Chronicle) -> List[str]:
        """Checks for presence of required seeds in the chronicle, returns missing seed IDs."""
        missing = []
        for seed_req in required:
            # All required seeds for payoffs must be mirrored.
            if not chronicle.has(seed_req.id):
                missing.append(seed_req.id)
        return missing

    def can_trigger_payoff(self, payoff_id: str, chronicle: Chronicle, current_chapter: int, game_flags: Dict[str, bool] = None) -> bool:
        """
        Determines if a payoff's conditions have been met, including fallbacks.
        """
        if game_flags is None:
            game_flags = {}

        payoff = self.payoffs.get(payoff_id)
        if not payoff:
            return False

        # 1. Check if payoff is already completed
        if game_flags.get(payoff.completion_flag, False):
            return False

        # 2. Check if within the trigger window
        if not (payoff.trigger_window.earliest_chapter <= current_chapter <= payoff.trigger_window.latest_chapter):
            return False

        # 3. Check primary seed requirements
        required_seeds = payoff.required_seeds.seeds
        mode = payoff.required_seeds.mode

        missing_seeds = self._check_seeds(required_seeds, chronicle)

        primary_satisfied = False
        if mode == "any_of" and len(missing_seeds) < len(required_seeds):
            primary_satisfied = True
        elif mode == "all_of" and not missing_seeds:
            primary_satisfied = True

        if primary_satisfied:
            return True

        # 4. If primary requirements are not met, check fallbacks
        if not missing_seeds: # Should not happen if primary_satisfied is False, but as a safeguard
             return False

        for fallback in payoff.fallbacks:
            # Is this fallback rule relevant for one of the seeds we are missing?
            if fallback.missing_seed in missing_seeds:
                # Is it still timely?
                if current_chapter <= fallback.deadline_chapter:
                    # Do we have any of the alternative seeds?
                    for alt_seed_id in fallback.alternatives:
                        if chronicle.has(alt_seed_id):
                            # Found a valid fallback path
                            return True

        return False