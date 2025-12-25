"""Workflow registry loaded from YAML configuration."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .skills import SkillFilter
from .tools import Tool


@dataclass
class WorkflowConfig:
    """Configuration for a registered workflow."""

    name: str
    module: str
    function: str
    input_types: list[str]
    tools: list[str] = field(default_factory=list)
    skills: SkillFilter = field(default_factory=SkillFilter)
    enabled: bool = True

    @property
    def handler(self) -> Callable[..., Any]:
        """Dynamically load and return the workflow handler function."""
        mod = importlib.import_module(self.module)
        func: Callable[..., Any] = getattr(mod, self.function)
        return func


class Registry:
    """Registry of workflows loaded from YAML configuration."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowConfig] = {}
        self._tools: dict[str, Tool] = {}

    def load_from_yaml(self, path: Path) -> None:
        """Load workflow configurations from a YAML file.

        Expected format:
            workflows:
              - name: my_workflow
                module: my_module.handlers
                function: handle_email
                input_types:
                  - email
                  - slack
                tools:
                  - fetch_url
                enabled: true
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        for wf_data in data.get("workflows", []):
            # Parse skill filter configuration
            skills_data = wf_data.get("skills", {})
            skill_filter = SkillFilter(
                required=skills_data.get("required", []),
                allowed=skills_data.get("allowed", []),
                denied=skills_data.get("denied", []),
            )

            config = WorkflowConfig(
                name=wf_data["name"],
                module=wf_data["module"],
                function=wf_data["function"],
                input_types=wf_data.get("input_types", []),
                tools=wf_data.get("tools", []),
                skills=skill_filter,
                enabled=wf_data.get("enabled", True),
            )
            self._workflows[config.name] = config

    def register_workflow(self, config: WorkflowConfig) -> None:
        """Register a workflow configuration."""
        self._workflows[config.name] = config

    def register_tool(self, tool: Tool) -> None:
        """Register a tool that can be used by workflows."""
        self._tools[tool.name] = tool

    def get_workflow(self, name: str) -> WorkflowConfig | None:
        """Get a workflow by name."""
        return self._workflows.get(name)

    def get_workflows_for_input(self, input_type: str) -> list[WorkflowConfig]:
        """Get all workflows that handle a given input type."""
        return [
            wf for wf in self._workflows.values() if wf.enabled and input_type in wf.input_types
        ]

    def get_tool(self, name: str) -> Tool | None:
        """Get a registered tool by name."""
        return self._tools.get(name)

    def get_tools_for_workflow(self, workflow_name: str) -> list[Tool]:
        """Get all tools configured for a workflow."""
        wf = self._workflows.get(workflow_name)
        if not wf:
            return []
        return [self._tools[name] for name in wf.tools if name in self._tools]

    @property
    def workflows(self) -> list[WorkflowConfig]:
        """Get all registered workflows."""
        return list(self._workflows.values())

    @property
    def tools(self) -> list[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())


# Global registry instance
_registry: Registry | None = None


def get_registry() -> Registry:
    """Get the global registry instance."""
    global _registry
    if _registry is None:
        _registry = Registry()
    return _registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _registry
    _registry = None
