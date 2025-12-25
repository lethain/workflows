"""Base input type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Input(Protocol):
    """Protocol for input types that can be normalized."""

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> Input:
        """Parse an event into this input type."""
        ...

    @classmethod
    def matches(cls, event: dict[str, Any]) -> bool:
        """Check if this input type can handle the given event."""
        ...

    def to_normalized(self) -> NormalizedInput:
        """Convert to normalized input format."""
        ...


@dataclass
class NormalizedInput:
    """Common normalized representation of all input types."""

    input_type: str
    source: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "input_type": self.input_type,
            "source": self.source,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "raw": self.raw,
        }
