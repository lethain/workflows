"""Input types for workflow processing."""

from .base import Input, NormalizedInput
from .email import EmailInput
from .slack import SlackInput
from .webhook import WebhookInput

__all__ = [
    "Input",
    "NormalizedInput",
    "EmailInput",
    "SlackInput",
    "WebhookInput",
]
