"""
Cache management functions for storing and loading data.
"""

import json
from pathlib import Path
from typing import Any

__all__ = ["load_json_cache", "save_json_cache"]


def load_json_cache(cache_file: Path) -> dict[str, Any]:
    """
    Load cached data from a JSON file

    Args:
        cache_file: Path to the cache file

    Returns:
        Dict containing cached data, or empty dict if file doesn't exist
    """
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json_cache(cache: dict[str, Any], cache_file: Path) -> None:
    """
    Save data to a JSON cache file

    Args:
        cache: Data to save
        cache_file: Path to the cache file
    """
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
