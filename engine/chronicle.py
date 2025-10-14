from engine.ui import show_toast

class ChronicleManager:
    """
    Manages the game's chronicle, which records important player
    achievements and story milestones (seeds).
    """
    def __init__(self, entries=None):
        """
        Initializes the ChronicleManager.

        Args:
            entries (list, optional): A list of existing chronicle entries,
                                      typically loaded from a save file.
                                      Defaults to None.
        """
        self.entries = entries if entries is not None else []

    def add(self, seed):
        """
        Adds a new seed to the chronicle.

        If the seed is marked as essential for a payoff, it will be
        protected in the chronicle.

        Args:
            seed (dict): The seed to add, loaded from a JSON file.
        """
        is_protected = seed.get("essential_for_payoff", False)
        entry = {
            "seed_id": seed["id"],
            "description": seed["description"],
            "protected": is_protected,
        }
        self.entries.append(entry)
        show_toast(f"Seed acquired: {seed['description']}", protected=is_protected)

    def get_entries(self):
        """
        Returns the list of all chronicle entries.

        Returns:
            list: The chronicle entries.
        """
        return self.entries