"""Skill type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SkillProperties:
    """Properties parsed from a skill's SKILL.md file."""

    name: str
    description: str = ""
    version: str = "1.0"
    author: str = ""
    tags: list[str] = field(default_factory=list)
    parameters: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "tags": self.tags,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "path": str(self.path) if self.path else None,
        }


@dataclass
class SkillFilter:
    """Filter for skills based on workflow configuration.

    Workflows can specify:
    - required: Skills that must be loaded (added to system prompt automatically)
    - allowed: Skills that can be used (shown in available_skills)
    - denied: Skills that cannot be used (excluded from available_skills)

    If allowed is empty, all skills except denied are available.
    If allowed is non-empty, only those skills are available (minus denied).
    """

    required: list[str] = field(default_factory=list)
    allowed: list[str] = field(default_factory=list)
    denied: list[str] = field(default_factory=list)

    def filter_skills(self, all_skills: dict[str, SkillProperties]) -> dict[str, SkillProperties]:
        """Filter skills based on this configuration.

        Returns skills that should be shown in available_skills.
        Does NOT include required skills (those go directly to system prompt).

        Args:
            all_skills: All loaded skills

        Returns:
            Filtered dict of available skills
        """
        result: dict[str, SkillProperties] = {}

        for name, skill in all_skills.items():
            # Skip required skills (they're loaded separately)
            if name in self.required:
                continue

            # Skip denied skills
            if name in self.denied:
                continue

            # If allowed list is specified, only include those
            if self.allowed and name not in self.allowed:
                continue

            result[name] = skill

        return result

    def get_required_skills(
        self, all_skills: dict[str, SkillProperties]
    ) -> dict[str, SkillProperties]:
        """Get skills that are required and should be in system prompt.

        Args:
            all_skills: All loaded skills

        Returns:
            Dict of required skills
        """
        return {name: all_skills[name] for name in self.required if name in all_skills}


@dataclass
class ValidationProblem:
    """A validation problem found in a skill."""

    level: str  # "error" or "warning"
    message: str
    path: str | None = None

    def __str__(self) -> str:
        if self.path:
            return f"[{self.level}] {self.path}: {self.message}"
        return f"[{self.level}] {self.message}"
