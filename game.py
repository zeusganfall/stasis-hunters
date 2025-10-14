import argparse
import json
import os
from engine.scene import Scene
from engine.chronicle import ChronicleManager
from engine.save import SaveManager

def load_json_file(file_path):
    """
    Loads data from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or None: A dictionary containing the JSON data, or None if the
                      file is not found or is invalid.
    """
    try:
        with open(file_path, 'r') as f:
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

    save_manager = SaveManager()
    game_state = save_manager.load() or {}

    chronicle_manager = ChronicleManager(game_state.get("chronicle_entries", []))

    current_scene_id = game_state.get("current_scene_id", args.scene)

    scene_data = load_json_file(os.path.join("data", "scenes", f"{current_scene_id}.json"))
    if not scene_data:
        print(f"Error: Scene '{current_scene_id}' not found or is invalid.")
        return

    scene = Scene(scene_data)
    scene.display()

    # Process seeds from the current scene
    if scene.seeds:
        all_seeds_list = load_json_file(os.path.join("data", "seeds.json")) or []
        all_seeds_dict = {seed['id']: seed for seed in all_seeds_list}
        for seed_id in scene.seeds:
            if seed_id in all_seeds_dict:
                chronicle_manager.add(all_seeds_dict[seed_id])

    # Update and save game state
    game_state["current_scene_id"] = current_scene_id
    game_state["chronicle_entries"] = chronicle_manager.get_entries()
    save_manager.save(game_state)

    if not scene.choices:
        print("The story ends here.")
        return

    if args.choice is not None:
        choice = args.choice
        if 1 <= choice <= len(scene.choices):
            next_scene_id = scene.get_next_scene(choice - 1)
            if next_scene_id:
                print(f"\nMoving to scene: {next_scene_id}")
                game_state["current_scene_id"] = next_scene_id
                save_manager.save(game_state)
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
            game_state["current_scene_id"] = next_scene_id
            save_manager.save(game_state)
        else:
            print("The story ends here.")


if __name__ == "__main__":
    main()