# Scene JSON Specification

This document outlines the structure of a scene JSON file used in Stasis-Hunters.

## Root Object

A scene file is a single JSON object with the following properties:

-   `id` (string, required): A unique identifier for the scene (e.g., `ch1_festival`).
-   `title` (string, required): The title of the scene, which may be displayed to the player.
-   `content` (string, required): The main descriptive text of the scene.
-   `choices` (array of `Choice` objects, optional): A list of interactive options for the player. If present, this is the primary way a scene progresses.
-   `effects` (array of `Effect` objects, optional): A list of actions that are triggered automatically when the scene loads. This is typically used for scenes without player interaction.

## The `Choice` Object

The `Choice` object defines an interactive option available to the player.

-   `id` (string, required): A unique identifier for the choice (e.g., `accept_charm`).
-   `text` (string, required): The text displayed to the player for this choice.
-   `effects` (array of `Effect` objects, required): A list of effects that are triggered if the player selects this choice.

## The `Effect` Object

The `Effect` object defines a specific event or action.

-   `type` (string, required): The type of the effect, which determines the action to be taken.
-   All other keys in the object are treated as parameters for the effect handler.

### Example with Choices

```json
{
  "id": "ch1_festival",
  "title": "Festival Awakening",
  "content": "The harbor festival hums with lanterns and paper stalls...",
  "choices": [
    {
      "id": "pickup_charm",
      "text": "Accept Hana's charm",
      "effects": [
        { "type": "pickup_seed", "seed_id": "S05" },
        { "type": "add_rel_points", "target": "Hana", "amount": 5 }
      ]
    },
    {
      "id": "read_pamphlet",
      "text": "Examine the city pamphlet...",
      "effects": [{ "type": "examine_seed", "seed_id": "S02" }]
    }
  ]
}
```

### Supported Effect Types

#### `pickup_seed`

Adds a specified seed to the player's inventory.

-   **`seed_id`** (string, required): The unique ID of the seed to be picked up.

#### `add_rel_points`

Adds relationship points to a character.

-   **`target`** (string, required): The ID of the character.
-   **`amount`** (integer, required): The number of points to add.

#### Other Effect Types (Placeholder)

-   `trigger_combat`
-   `give_item`
-   `examine_seed`
-   `transition_chapter`