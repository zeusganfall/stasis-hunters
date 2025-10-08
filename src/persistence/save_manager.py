import json
import logging
import os
import tempfile
from typing import Dict, Any

from src.models.chronicle import Chronicle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_game(state: Dict[str, Any], path: str) -> None:
    """
    Saves the game state to a JSON file atomically.

    Args:
        state: The game state to save, expected to contain a 'chronicle' key.
        path: The path to save the file to.
    """
    try:
        # Atomic write: write to a temporary file then rename it.
        # This prevents save file corruption if the process is interrupted.
        temp_dir = os.path.dirname(path)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, dir=temp_dir, suffix=".tmp") as tmp_file:
            # The `state` should contain a `Chronicle` object that needs serialization
            if "chronicle" in state and isinstance(state["chronicle"], Chronicle):
                # Create a serializable copy of the state
                serializable_state = state.copy()
                serializable_state["chronicle"] = state["chronicle"].to_dict()
                json.dump(serializable_state, tmp_file, indent=4)
            else:
                 json.dump(state, tmp_file, indent=4)

            temp_path = tmp_file.name

        # On POSIX systems, rename is atomic. On Windows, it may not be.
        # os.replace() is a good cross-platform choice for this.
        os.replace(temp_path, path)
        logger.info(f"Game state saved successfully to {path}")

    except Exception as e:
        logger.error(f"Failed to save game state to {path}: {e}")
        # Clean up the temporary file if it still exists
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def load_game(path: str) -> Dict[str, Any]:
    """
    Loads game state from a JSON file.

    Args:
        path: The path to the save file.

    Returns:
        The loaded game state.
    """
    try:
        with open(path, "r") as f:
            state = json.load(f)
            # The `state` should contain a chronicle that needs deserialization
            if "chronicle" in state:
                state["chronicle"] = Chronicle.from_dict(state["chronicle"])
            return state
    except FileNotFoundError:
        logger.error(f"Save file not found at {path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in save file at {path}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load game state from {path}: {e}")
        return {}


def delete_fragment(fragment_id: str, state: Dict[str, Any]) -> bool:
    """
    Deletes a data fragment from the game state, but only if it is not
    protected in the chronicle.

    Args:
        fragment_id: The ID of the fragment to delete (e.g., a seed ID).
        state: The current game state, containing the chronicle.

    Returns:
        True if the fragment was deleted, False otherwise.
    """
    chronicle: Chronicle = state.get("chronicle")
    if not chronicle:
        logger.warning("No chronicle found in game state. Deletion is not protected.")
        # Decide if deletion should proceed. For now, we assume it can.
        # Depending on game logic, you might want to prevent this.
    elif chronicle.has(fragment_id):
        logger.error(
            f"Attempted to delete fragment '{fragment_id}' which is protected by the chronicle."
        )
        return False

    # Assuming fragments are stored in a dictionary in the state, e.g., state['world_items']
    # This part is an example and depends on the actual state structure.
    if "world_items" in state and fragment_id in state["world_items"]:
        del state["world_items"][fragment_id]
        logger.info(f"Fragment '{fragment_id}' deleted from the game state.")
        return True

    logger.warning(f"Fragment '{fragment_id}' not found in game state.")
    return False


def validate_save(state: Dict[str, Any]) -> bool:
    """
    Validates the integrity of the save state, specifically that all
    chronicle entries remain write-once.

    This function is more of a conceptual placeholder. True validation would
    involve comparing the current chronicle against a previously known-good
    version to ensure no protected entries were removed or altered. Without
    a history, we can only check for internal consistency.

    For now, this function can just check if the chronicle data is well-formed.
    """
    if "chronicle" not in state:
        logger.error("Validation failed: 'chronicle' not found in save state.")
        return False

    chronicle = state.get("chronicle")
    if not isinstance(chronicle, Chronicle):
        logger.error("Validation failed: 'chronicle' is not a Chronicle object.")
        return False

    # All entries in a valid chronicle are protected by definition.
    # We could add more complex checks here if needed, e.g., against a schema.
    for entry in chronicle.list_entries():
        if not entry.protected:
            logger.error(f"Validation failed: Chronicle entry '{entry.id}' is not protected.")
            return False

    logger.info("Save state validation successful.")
    return True