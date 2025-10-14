import json
import os

class SaveManager:
    """
    Manages saving and loading the game state.
    """
    def __init__(self, save_file="save.json"):
        """
        Initializes the SaveManager.

        Args:
            save_file (str, optional): The name of the save file.
                                       Defaults to "save.json".
        """
        self.save_file = save_file
        self.protected_chronicle_region = []

    def save(self, game_state):
        """
        Saves the current game state to a file.

        The chronicle entries in the save file are write-once. Any attempt
        to modify existing protected entries will be prevented.

        Args:
            game_state (dict): The game state to save.
        """
        if "chronicle_entries" in game_state:
            # Prevent modification of the protected chronicle region
            if any(entry not in game_state["chronicle_entries"] for entry in self.protected_chronicle_region):
                raise ValueError("Cannot remove entries from the protected chronicle region.")
            self.protected_chronicle_region = [
                entry for entry in game_state["chronicle_entries"] if entry.get("protected")
            ]

        with open(self.save_file, 'w') as f:
            json.dump(game_state, f, indent=4)

    def load(self):
        """
        Loads the game state from a file.

        Returns:
            dict or None: The loaded game state, or None if the save file
                          does not exist.
        """
        if not os.path.exists(self.save_file):
            return None

        with open(self.save_file, 'r') as f:
            game_state = json.load(f)
            if "chronicle_entries" in game_state:
                self.protected_chronicle_region = [
                    entry for entry in game_state["chronicle_entries"] if entry.get("protected")
                ]
            return game_state