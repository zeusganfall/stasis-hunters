import argparse
import json
import os
from engine.scene import Scene

def load_scene_data(scene_id):
    """
    Loads scene data from a JSON file.

    Args:
        scene_id (str): The ID of the scene to load.

    Returns:
        dict or None: A dictionary containing the scene data, or None if the file
                      is not found or is invalid.
    """
    scene_path = os.path.join("data", "scenes", f"{scene_id}.json")
    try:
        with open(scene_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def main():
    """
    The main game loop.
    """
    parser = argparse.ArgumentParser(description="A text-based narrative game.")
    parser.add_argument("--scene", default="scene_festival",
                        help="The starting scene ID.")
    parser.add_argument("--choice", type=int, help="The choice to make in the scene.")
    args = parser.parse_args()

    current_scene_id = args.scene

    scene_data = load_scene_data(current_scene_id)
    if not scene_data:
        print(f"Error: Scene '{current_scene_id}' not found or is invalid.")
        return

    scene = Scene(scene_data)
    scene.display()

    if not scene.choices:
        print("The story ends here.")
        return

    if args.choice is not None:
        choice = args.choice
        if 1 <= choice <= len(scene.choices):
            next_scene_id = scene.get_next_scene(choice - 1)
            if next_scene_id:
                print(f"\nMoving to scene: {next_scene_id}")
            else:
                print("The story ends here.")
        else:
            print("Invalid choice.")
    else:
        # This part will not be hit in the automated tests, but is kept for local running.
        choice = -1
        while choice < 1 or choice > len(scene.choices):
            try:
                choice_input = input(f"Choose an option (1-{len(scene.choices)}): ")
                choice = int(choice_input)
            except ValueError:
                print("Invalid input. Please enter a number.")

        next_scene_id = scene.get_next_scene(choice - 1)
        if next_scene_id:
            print(f"\nMoving to scene: {next_scene_id}")
        else:
            print("The story ends here.")


if __name__ == "__main__":
    main()