import json

class Scene:
    """
    Manages a single scene in the game, including its text, choices, and navigation.
    """
    def __init__(self, scene_data):
        """
        Initializes a Scene object from a dictionary of scene data.

        Args:
            scene_data (dict): A dictionary containing the scene's properties,
                               loaded from a JSON file.
        """
        self.id = scene_data.get("id")
        self.text = scene_data.get("text")
        self.seeds = scene_data.get("seeds", [])
        self.choices = scene_data.get("choices", [])

    def display(self):
        """
        Displays the scene's text and available choices to the player.
        """
        print(self.text)
        print("\n" + "="*20 + "\n")
        for i, choice in enumerate(self.choices):
            print(f"{i + 1}. {choice['text']}")
        print("\n")

    def get_next_scene(self, choice_index):
        """
        Determines the ID of the next scene based on the player's choice.

        Args:
            choice_index (int): The 1-based index of the choice made by the player.

        Returns:
            str or None: The ID of the next scene, or None if the choice is invalid
                         or leads to the end of the game.
        """
        if 0 <= choice_index < len(self.choices):
            return self.choices[choice_index]["next_scene"]
        return None