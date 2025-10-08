import json
import logging
from typing import Dict, Any

from src.models.payoff import Payoff
from src.models.seed import Seed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_seeds(path: str) -> Dict[str, Seed]:
    """Loads seeds from a JSON file."""
    seeds: Dict[str, Seed] = {}
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.error(f"Seed file at {path} should contain a JSON object.")
                return {}
            for item_id, item_data in data.items():
                try:
                    item_data["id"] = item_id
                    seeds[item_id] = Seed.from_dict(item_data)
                except KeyError as e:
                    logger.error(f"Malformed seed entry for {item_id}: missing key {e}")
                except Exception as e:
                    logger.error(f"Error parsing seed {item_id}: {e}")
    except FileNotFoundError:
        logger.error(f"Seed file not found at {path}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in seed file at {path}")
    return seeds


def load_payoffs(path: str, all_seeds: Dict[str, Seed]) -> Dict[str, Payoff]:
    """Loads payoffs from a JSON file and validates required_seeds."""
    payoffs: Dict[str, Payoff] = {}
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.error(f"Payoff file at {path} should contain a JSON object.")
                return {}
            for item_id, item_data in data.items():
                try:
                    for seed_id in item_data.get("required_seeds", []):
                        if seed_id not in all_seeds:
                            raise ValueError(
                                f"Payoff '{item_id}' references an unknown seed '{seed_id}'"
                            )

                    item_data["id"] = item_id
                    payoffs[item_id] = Payoff.from_dict(item_data)
                except (KeyError, ValueError) as e:
                    logger.error(f"Malformed payoff entry for {item_id}: {e}")
                except Exception as e:
                    logger.error(f"Error parsing payoff {item_id}: {e}")
    except FileNotFoundError:
        logger.error(f"Payoff file not found at {path}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in payoff file at {path}")
    return payoffs


def load_scene(path: str) -> None:
    """
    Loads scene data from a JSON file.
    (This is a placeholder as per AGENTS.md)
    """
    logger.info(f"Loading scene from {path} (not implemented).")
    pass