from typing import Dict, List, Callable, Any

from src.models.chronicle import Chronicle
from src.models.scene import Effect
from src.models.seed import Seed


class SceneEngine:
    """
    Manages effect processing based on game events.
    """

    def __init__(
        self,
        all_seeds: Dict[str, Seed],
        chronicle: Chronicle,
        inventory: List[str],
    ):
        self.all_seeds = all_seeds
        self.chronicle = chronicle
        self.inventory = inventory
        self.event_handlers: Dict[str, Callable[[Any], None]] = {
            "pickup_seed": self._handle_pickup_seed,
            # Add other handlers here as needed, e.g., "add_rel_points"
        }

    def process_effects(self, effects: List[Effect]) -> None:
        """Processes a list of effects."""
        for effect in effects:
            handler = self.event_handlers.get(effect.type)
            if handler:
                # The `from_dict` in the model now expects params to be a dictionary
                handler(effect.params)
            else:
                print(f"Warning: No handler for effect type '{effect.type}'")

    def _handle_pickup_seed(self, params: Dict[str, Any]) -> None:
        """Handles the 'pickup_seed' effect."""
        # The scene JSON uses "seed_id", but our model normalizes it.
        # Let's be flexible and check for both.
        seed_id = params.get("seed_id") or params.get("id")
        if not seed_id:
            print("Error: 'pickup_seed' effect requires a 'seed_id'.")
            return

        seed = self.all_seeds.get(seed_id)
        if not seed:
            print(f"Error: Seed '{seed_id}' not found.")
            return

        if seed_id not in self.inventory:
            self.inventory.append(seed_id)
            print(f"Picked up seed: '{seed.title}'")

        if seed.mirrored_to_chronicle_on_pickup or seed.essential_for_payoff:
            if self.chronicle.mirror(seed):
                print(f"Seed '{seed_id}' mirrored to Chronicle.")
            else:
                print(f"Seed '{seed_id}' was already in Chronicle.")