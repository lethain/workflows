"""AWS Lambda handler for workflow processing."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .normalize import normalize
from .registry import get_registry
from .runner import run_all


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    """AWS Lambda handler function.

    Processes incoming events through the workflow system:
    1. Normalizes the event to a common format
    2. Finds matching workflows from the registry
    3. Executes each matching workflow
    4. Returns aggregated results

    Args:
        event: Lambda event (from API Gateway, SES, EventBridge, etc.)
        context: Lambda context object

    Returns:
        Response with workflow execution results
    """
    # Load registry from config if not already loaded
    registry = get_registry()
    if not registry.workflows:
        config_path = os.environ.get("WORKFLOWS_CONFIG", "config/workflows.yaml")
        config_file = Path(config_path)
        if config_file.exists():
            registry.load_from_yaml(config_file)

    try:
        # Normalize the input
        normalized = normalize(event)

        # Run matching workflows
        result = run_all(normalized, registry)

        return {
            "statusCode": 200 if result.success else 500,
            "body": json.dumps(result.to_dict()),
            "headers": {
                "Content-Type": "application/json",
            },
        }

    except ValueError as e:
        # Input type detection failed
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Invalid input",
                "message": str(e),
            }),
            "headers": {
                "Content-Type": "application/json",
            },
        }

    except Exception as e:
        # Unexpected error
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal error",
                "message": str(e),
            }),
            "headers": {
                "Content-Type": "application/json",
            },
        }
