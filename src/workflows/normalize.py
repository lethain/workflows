"""Input normalization logic."""

from __future__ import annotations

from typing import Any

from .inputs import EmailInput, NormalizedInput, SlackInput, WebhookInput

# Ordered list of input types to check (most specific first)
INPUT_TYPES = [
    EmailInput,
    SlackInput,
    WebhookInput,  # Webhook is most generic, check last
]


def detect_input_type(event: dict[str, Any]) -> str:
    """Detect the type of input from an event.

    Returns the input type name (email, slack, webhook) or 'unknown'.
    """
    for input_cls in INPUT_TYPES:
        if input_cls.matches(event):
            return input_cls.__name__.lower().replace("input", "")
    return "unknown"


def normalize(event: dict[str, Any]) -> NormalizedInput:
    """Normalize any event into a common NormalizedInput format.

    Automatically detects the input type and parses accordingly.

    Args:
        event: Raw event from Lambda trigger

    Returns:
        NormalizedInput with consistent structure

    Raises:
        ValueError: If event type cannot be determined
    """
    for input_cls in INPUT_TYPES:
        if input_cls.matches(event):
            parsed = input_cls.from_event(event)
            return parsed.to_normalized()

    raise ValueError(f"Unable to determine input type for event: {list(event.keys())}")


def normalize_with_type(event: dict[str, Any], input_type: str) -> NormalizedInput:
    """Normalize an event with an explicitly specified type.

    Args:
        event: Raw event from Lambda trigger
        input_type: The input type name (email, slack, webhook)

    Returns:
        NormalizedInput with consistent structure

    Raises:
        ValueError: If input_type is not recognized
    """
    type_map = {
        "email": EmailInput,
        "slack": SlackInput,
        "webhook": WebhookInput,
    }

    input_cls = type_map.get(input_type.lower())
    if input_cls is None:
        raise ValueError(f"Unknown input type: {input_type}")

    parsed = input_cls.from_event(event)
    return parsed.to_normalized()
