import random

class Ability:
    """
    Represents a single ability that a combatant can use.
    """
    def __init__(self, ability_data):
        self.id = ability_data["id"]
        self.name = ability_data["name"]
        self.power = ability_data["power"]

class Combatant:
    """
    Represents a participant in combat, either a player character or a monster.
    """
    def __init__(self, combatant_data, all_abilities):
        self.id = combatant_data["id"]
        self.name = combatant_data["name"]
        self.hp = combatant_data["hp"]
        self.max_hp = combatant_data["hp"]
        self.attack = combatant_data["attack"]
        self.defense = combatant_data["defense"]
        self.abilities = [
            all_abilities[ability_id] for ability_id in combatant_data["abilities"]
            if ability_id in all_abilities
        ]

    def is_defeated(self):
        """
        Checks if the combatant has been defeated.

        Returns:
            bool: True if HP is 0 or less, False otherwise.
        """
        return self.hp <= 0

    def take_damage(self, damage):
        """
        Reduces the combatant's HP by a given amount.

        Args:
            damage (int): The amount of damage to take.
        """
        self.hp = max(0, self.hp - damage)
        print(f"{self.name} takes {damage} damage!")

class CombatLoop:
    """
    Manages a single combat encounter.
    """
    def __init__(self, player_party, enemy_party):
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.turn_order = self.player_party + self.enemy_party  # Simple turn order for now
        random.seed(0) # Deterministic RNG for prototype

    def run(self):
        """
        Executes the main combat loop.
        """
        print("\n" + "="*10 + " COMBAT START " + "="*10 + "\n")
        while not self.is_combat_over():
            for combatant in self.turn_order:
                if not combatant.is_defeated():
                    self.take_turn(combatant)
                    if self.is_combat_over():
                        break
        self.print_combat_result()

    def take_turn(self, combatant):
        """
        Manages a single combatant's turn.
        """
        print(f"\n--- {combatant.name}'s Turn (HP: {combatant.hp}/{combatant.max_hp}) ---")
        if combatant in self.player_party:
            self.player_turn(combatant)
        else:
            self.enemy_turn(combatant)

    def player_turn(self, player):
        """
        Handles the player's actions for a turn.
        """
        print("Choose an ability:")
        for i, ability in enumerate(player.abilities):
            print(f"{i + 1}. {ability.name}")

        choice = -1
        while choice < 1 or choice > len(player.abilities):
            try:
                choice_input = input(f"Choose an option (1-{len(player.abilities)}): ")
                choice = int(choice_input)
            except ValueError:
                print("Invalid input. Please enter a number.")

        ability = player.abilities[choice - 1]
        target = self.select_target(self.enemy_party)
        if target:
            self.use_ability(player, ability, target)

    def enemy_turn(self, enemy):
        """
        Handles an enemy's actions for a turn (simple AI).
        """
        ability = enemy.abilities[0]  # Simple AI: always use the first ability
        target = self.select_target(self.player_party)
        if target:
            print(f"{enemy.name} uses {ability.name}!")
            self.use_ability(enemy, ability, target)

    def use_ability(self, user, ability, target):
        """
        Applies an ability's effect from a user to a target.
        """
        damage = max(1, user.attack + ability.power - target.defense)
        target.take_damage(damage)

    def select_target(self, party):
        """
        Selects a valid target from a party.

        Args:
            party (list): The party to select a target from.

        Returns:
            Combatant or None: The selected target, or None if no valid targets exist.
        """
        valid_targets = [c for c in party if not c.is_defeated()]
        if not valid_targets:
            return None
        # For now, player always targets first enemy, and vice-versa
        return valid_targets[0]

    def is_combat_over(self):
        """
        Checks if the combat has ended.

        Returns:
            bool: True if either party is fully defeated, False otherwise.
        """
        return all(c.is_defeated() for c in self.player_party) or \
               all(c.is_defeated() for c in self.enemy_party)

    def print_combat_result(self):
        """
        Prints the result of the combat.
        """
        if all(c.is_defeated() for c in self.enemy_party):
            print("\n" + "="*10 + " VICTORY! " + "="*10 + "\n")
        else:
            print("\n" + "="*10 + " DEFEAT! " + "="*10 + "\n")