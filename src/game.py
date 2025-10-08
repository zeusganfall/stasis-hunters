# src/game.py
import os
from typing import Dict

from src.data_loader import load_seeds, load_scene
from src.models.chronicle import Chronicle
from src.models.scene import Scene, Choice
from src.models.seed import Seed
from src.scene_engine import SceneEngine
from src.ui import console_ui as ui


class Game:
    """Manages the main game loop and state."""

    def __init__(self):
        self.data_path = "src/data"
        self.all_seeds = self._load_data()
        self.chronicle = Chronicle()
        # Start with S01 in inventory for the demo
        self.inventory = ["S01"]
        self.scene_engine = SceneEngine(self.all_seeds, self.chronicle, self.inventory)
        self.is_running = True

    def _load_data(self) -> Dict[str, Seed]:
        """Loads all seed data from the data directory."""
        seeds_path = os.path.join(self.data_path, "seeds.json")
        return load_seeds(seeds_path)

    def run(self):
        """Starts the main game loop."""
        print("Stasis Hunters - Console Mode")
        print("=" * 30)

        # Run the interactive festival scene.
        self.run_scene("scene_ch01_festival")

        # Demonstrate inventory and chronicle after the scene.
        print("\n--- Post-Scene State ---")
        ui.render_inventory(self.inventory, self.all_seeds, self.chronicle)

        # Demonstrate memory cost UI.
        self.run_memory_cost_demo()

        print("\nEnd of demo. Thank you for playing!")

    def run_scene(self, scene_id: str):
        """Loads and runs a single interactive scene."""
        scene_path = os.path.join(self.data_path, "scenes", f"{scene_id}.json")
        try:
            scene = load_scene(scene_path)
            if not scene:
                # The loader already logs the error, so we can just exit.
                return

            ui.render_scene(scene)

            # Process top-level effects for scenes without choices
            if scene.effects:
                self.scene_engine.process_effects(scene.effects)

            # Handle choices if they exist
            if scene.choices:
                self._handle_choices(scene)

            # In a full game, you might have a "continue" choice or auto-transition.
            # For this demo, we'll just end the scene here.
            print(f"\n--- End of Scene: {scene.title} ---")
            # input("Press Enter to continue...") # Removed for non-interactive execution

        except FileNotFoundError:
            print(f"Error: Scene file not found at '{scene_path}'")
        except Exception as e:
            print(f"An error occurred while running scene '{scene_id}': {e}")

    def _handle_choices(self, scene: Scene):
        """Renders choices and processes the user's selection."""
        print("\nChoose an option:")
        for i, choice in enumerate(scene.choices):
            print(f"  {i + 1}: {choice.text}")

        # --- Automated choice for non-interactive environment ---
        # In a real game, this would be `input()`. We'll simulate choosing option 1.
        selection = 0
        selected_choice = scene.choices[selection]
        print(f"\nSimulating choice (1): '{selected_choice.text}'")
        self.scene_engine.process_effects(selected_choice.effects)
        # --- End of automated choice ---

    def run_memory_cost_demo(self):
        """
        A scenario to demonstrate the memory cost UI functionality.
        This runs *after* the main scene has been played.
        """
        print("\n" + "*" * 40)
        print("| DEMONSTRATING MEMORY COST INTERFACE |")
        print("*" * 40)

        # Add a non-chronicle seed to the inventory for the demo.
        if "S_OPTIONAL_01" not in self.inventory:
            self.inventory.append("S_OPTIONAL_01")
        if "S_OPTIONAL_01" not in self.all_seeds:
            self.all_seeds["S_OPTIONAL_01"] = Seed(id="S_OPTIONAL_01", title="Fading Echo of a Forgotten Song", payoff="", essential_for_payoff=False, mirrored_to_chronicle_on_pickup=False, chapter=1, meta={})

        print("\nSCENARIO: Player must choose to forget an optional memory.")
        ui.render_inventory(self.inventory, self.all_seeds, self.chronicle)

        chronicle_ids = {entry.id for entry in self.chronicle.list_entries()}
        inventory_ids = set(self.inventory)
        optional_fragments = inventory_ids - chronicle_ids

        # --- Test Case 1: Valid removal ---
        print("\n[Test Case 1: Simulating a valid memory removal...]")
        ui.confirm_memory_cost(optional_fragments, chronicle_ids, self.all_seeds)

        # --- Test Case 2: Invalid removal (attempting to remove a chronicle item) ---
        print("\n[Test Case 2: Simulating an invalid memory removal...]")
        # We'll pretend the game logic wrongly tries to remove a chronicle item.
        # Let's use 'S05' if it was picked up, otherwise 'S01' which we added initially.
        item_to_protect = "S05" if "S05" in chronicle_ids else "S01"

        # To make sure S01 is in chronicle for the test case
        if not self.chronicle.has("S01"):
            self.chronicle.mirror(self.all_seeds["S01"])
            chronicle_ids.add("S01")


        invalid_optional_fragments = optional_fragments | {item_to_protect}
        ui.confirm_memory_cost(invalid_optional_fragments, chronicle_ids, self.all_seeds)


if __name__ == "__main__":
    game = Game()
    game.run()