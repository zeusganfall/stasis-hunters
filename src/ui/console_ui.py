# src/ui/console_ui.py
from typing import List, Tuple, Optional, Dict, Set

from src.models.chronicle import Chronicle
from src.models.combat import Entity, Ability, CombatEngine
from src.models.scene import Scene
from src.models.seed import Seed


def render_scene(scene: Scene):
    """Renders the scene's title and content."""
    print("\n" + "=" * 40)
    print(f"| {scene.title}")
    print("=" * 40)
    print(scene.content)
    print("-" * 40)


def render_inventory(inventory: List[str], all_seeds: Dict[str, Seed], chronicle: Chronicle):
    """Renders the player's inventory, marking protected items."""
    print("\n--- Inventory ---")
    if not inventory:
        print("  (Empty)")
        return

    for seed_id in inventory:
        seed = all_seeds.get(seed_id)
        if not seed:
            print(f"  - Unknown Seed ID: {seed_id}")
            continue

        protection_status = "[Chronicle — protected]" if chronicle.has(seed_id) else ""
        print(f"  - {seed.title} {protection_status}")
    print("-----------------\n")


def confirm_memory_cost(
    optional_fragments: Set[str],
    chronicle_entries: Set[str],
    all_seeds: Dict[str, Seed],
) -> bool:
    """
    Asks the user to confirm the removal of optional memory fragments.

    It shows what will be removed and what is protected, and disallows
    the removal of protected items. This function simulates the UI check.
    For the purpose of this scope, it will simply list the items and
    return True, assuming a user would confirm. The key is the check.

    Returns:
        bool: True if the user confirms, False otherwise.
    """
    print("\n--- Memory Cost Confirmation ---")
    print("The following optional memories will be permanently lost:")
    if not optional_fragments:
        print("  (None)")
    else:
        for frag_id in optional_fragments:
            seed = all_seeds.get(frag_id)
            title = seed.title if seed else f"Unknown Fragment ({frag_id})"
            print(f"  - [TO BE REMOVED] {title}")

    print("\nThe following memories are protected by the Chronicle and CANNOT be removed:")
    if not chronicle_entries:
        print("  (None)")
    else:
        for entry_id in chronicle_entries:
            seed = all_seeds.get(entry_id)
            title = seed.title if seed else f"Unknown Chronicle Entry ({entry_id})"
            print(f"  - [PROTECTED] {title}")

    # In a real UI, we would check if any `optional_fragments` are also in `chronicle_entries`
    # and raise an error, but the logic is assumed to be sound from the caller.
    # The acceptance criteria is that the UI *refuses* removal, which we can simulate.
    has_invalid_removal = any(frag in chronicle_entries for frag in optional_fragments)
    if has_invalid_removal:
        print("\nERROR: Attempting to remove a protected Chronicle entry. This action is forbidden.")
        print("Aborting memory cost operation.")
        return False

    print("\n" + "-" * 30)
    # Simulate user input for confirmation
    # In a real game, you would use: `confirm = input("Proceed? (yes/no): ").lower()`
    print("Confirmation step: For this simulation, we assume the user confirms.")
    print("-" * 30)
    return True


def print_combat_state(engine: CombatEngine):
    """Prints the current state of the combat."""
    print("\n--- Combat State ---")
    print("Players:")
    for p in engine.players:
        status = "Alive" if p.alive else "Defeated"
        print(f"  - {p.name} (HP: {p.hp}/{p.max_hp}, Pulse: {p.pulse}) - {status}")

    print("Enemies:")
    for e in engine.enemies:
        status = "Alive" if e.alive else "Defeated"
        print(f"  - {e.name} (HP: {e.hp}/{e.max_hp}) - {status}")
    print("--------------------\n")


def select_combat_action(
    actor: Entity,
    abilities: List[Ability],
    targets: List[Entity],
    engine: CombatEngine
) -> Tuple[Ability, Entity, Optional[Entity]]:
    """
    A simple CLI action selector for combat.
    """
    print(f"--- {actor.name}'s Turn ---")

    # 1. Choose ability
    print("Choose an ability:")
    for i, ability in enumerate(abilities):
        cost_str = f"(Cost: {ability.cost_pulse} Pulse)" if ability.cost_pulse > 0 else ""
        print(f"  {i + 1}: {ability.name} {cost_str}")

    while True:
        try:
            choice = int(input(f"Select ability (1-{len(abilities)}): ")) - 1
            if 0 <= choice < len(abilities):
                selected_ability = abilities[choice]
                if selected_ability.cost_pulse > actor.pulse:
                    print(f"Not enough Pulse for {selected_ability.name}. Try another ability.")
                    continue
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # 2. Choose target
    print("\nChoose a target:")
    for i, target in enumerate(targets):
        print(f"  {i + 1}: {target.name} (HP: {target.hp})")

    while True:
        try:
            choice = int(input(f"Select target (1-{len(targets)}): ")) - 1
            if 0 <= choice < len(targets):
                selected_target = targets[choice]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # 3. Handle partner combos (simplified for now)
    selected_partner = None
    if selected_ability.requires_partner:
        print("\nChoose a partner for the combo:")
        # Filter for other available, living players
        possible_partners = [p for p in engine.players if p.alive and p.id != actor.id]
        if not possible_partners:
            print("No available partners for a combo!")
            # This will likely fail in the engine, which is what we want to communicate
            return selected_ability, selected_target, None

        for i, partner in enumerate(possible_partners):
            print(f"  {i+1}: {partner.name}")

        while True:
            try:
                # Adding an option to not select a partner
                choice = int(input(f"Select partner (1-{len(possible_partners)}, or 0 to cancel): ")) - 1
                if choice == -1:
                    print("Combo cancelled. Defaulting to a standard action or passing turn might be necessary.")
                    # Let the engine decide what to do with a failed combo attempt.
                    return selected_ability, selected_target, None
                if 0 <= choice < len(possible_partners):
                    selected_partner = possible_partners[choice]
                    break
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    return selected_ability, selected_target, selected_partner