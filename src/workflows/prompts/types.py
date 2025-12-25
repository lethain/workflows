"""Prompt type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Prompt:
    """A prompt loaded from a markdown file with YAML frontmatter."""

    name: str
    description: str = ""
    version: str = "1.0"
    workflow: str | None = None
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    path: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "workflow": self.workflow,
            "content": self.content,
            "metadata": self.metadata,
            "path": self.path,
        }
