# src/ui/console_ui.py
from typing import List, Tuple, Optional, Dict

from src.models.combat import Entity, Ability, CombatEngine


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