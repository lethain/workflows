"""YAML file storage utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def get_config_dir() -> Path:
    """Get the configuration directory path.

    Uses WORKFLOWS_CONFIG_DIR environment variable if set,
    otherwise defaults to 'config' relative to the current directory.
    """
    config_dir = os.environ.get("WORKFLOWS_CONFIG_DIR", "config")
    return Path(config_dir)


def get_data_dir() -> Path:
    """Get the data directory path.

    Uses WORKFLOWS_DATA_DIR environment variable if set,
    otherwise defaults to 'data' relative to the current directory.
    """
    data_dir = os.environ.get("WORKFLOWS_DATA_DIR", "data")
    return Path(data_dir)


def read_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML file and return its contents.

    Args:
        path: Path to the YAML file

    Returns:
        Parsed YAML contents as a dictionary

    Raises:
        FileNotFoundError: If file does not exist
        yaml.YAMLError: If file contains invalid YAML
    """
    with open(path) as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    """Write data to a YAML file.

    Creates parent directories if they don't exist.

    Args:
        path: Path to write the YAML file
        data: Data to serialize to YAML
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def append_yaml_list(path: Path, item: dict[str, Any], list_key: str = "items") -> None:
    """Append an item to a list in a YAML file.

    Creates the file if it doesn't exist.

    Args:
        path: Path to the YAML file
        item: Item to append to the list
        list_key: Key of the list in the YAML structure
    """
    data = {}
    if path.exists():
        data = read_yaml(path)

    if list_key not in data:
        data[list_key] = []

    data[list_key].append(item)
    write_yaml(path, data)


def list_yaml_files(directory: Path, pattern: str = "*.yaml") -> list[Path]:
    """List all YAML files in a directory.

    Args:
        directory: Directory to search
        pattern: Glob pattern for YAML files

    Returns:
        List of paths to YAML files
    """
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern))
