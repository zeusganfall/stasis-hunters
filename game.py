import argparse
import json
import os
from engine.scene import Scene
from engine.chronicle import ChronicleManager
from engine.save import SaveManager
from engine.combat import Ability, Combatant, CombatLoop

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

def run_combat_demo():
    """
    Sets up and runs a demonstration combat encounter.
    """
    abilities_data = load_json_file(os.path.join("data", "abilities.json")) or []
    characters_data = load_json_file(os.path.join("data", "characters.json")) or []
    monsters_data = load_json_file(os.path.join("data", "monsters.json")) or []

    if not all([abilities_data, characters_data, monsters_data]):
        print("Error: Missing required data files for combat (abilities, characters, or monsters).")
        return

    all_abilities = {data['id']: Ability(data) for data in abilities_data}

    player_character_data = next((c for c in characters_data if c['id'] == 'PLAYER_AKI'), None)
    enemy_data = next((m for m in monsters_data if m['id'] == 'MONSTER_GOBLIN'), None)

    if not player_character_data or not enemy_data:
        print("Error: Could not load character or monster data for combat demo.")
        return

    player_party = [Combatant(player_character_data, all_abilities)]
    enemy_party = [Combatant(enemy_data, all_abilities)]

    combat = CombatLoop(player_party, enemy_party)
    combat.run()

def main():
    """
    The main game loop.
    """
    parser = argparse.ArgumentParser(description="A text-based narrative game.")
    parser.add_argument("--scene", default="scene_festival", help="The starting scene ID.")
    parser.add_argument("--choice", type=int, help="The choice to make in the scene.")
    parser.add_argument("--combat", help="Run a combat encounter by ID (e.g., 'demo').")
    args = parser.parse_args()

    if args.combat:
        if args.combat == 'demo':
            run_combat_demo()
        else:
            print(f"Error: Unknown combat encounter '{args.combat}'.")
        return

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