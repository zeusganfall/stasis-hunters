# Scene JSON Specification

This document outlines the structure of a scene JSON file used in Stasis-Hunters.

## Root Object

A scene file is a single JSON object with the following properties:

-   `id` (string, required): A unique identifier for the scene (e.g., `ch1_festival_intro`).
-   `title` (string, required): The title of the scene, which may be displayed to the player.
-   `content` (string, required): The main descriptive text of the scene.
-   `effects` (array of `Effect` objects, optional): A list of actions that are triggered when the scene is processed.

### Example

```json
{
  "id": "ch1_festival_start",
  "title": "The Festival Begins",
  "content": "You arrive at the town square, bustling with people celebrating the annual harvest festival. Banners of every color flutter in the wind.",
  "effects": [
    {
      "type": "pickup_seed",
      "params": {
        "id": "S05"
      }
    }
  ]
}
```

## The `Effect` Object

The `Effect` object defines a specific event or action that occurs within the scene.

-   `type` (string, required): The type of the effect. This determines the action to be taken.
-   `params` (object, optional): A dictionary of key-value pairs that provide data for the effect handler.

### Supported Effect Types

#### `pickup_seed`

Adds a specified seed to the player's inventory.

-   **`params.id`** (string, required): The unique ID of the seed to be picked up.

#### Other Effect Types (Placeholder)

The following effect types are planned but not yet implemented:

-   `trigger_combat`
-   `give_item`
-   `add_rel_points`
-   `transition_chapter`