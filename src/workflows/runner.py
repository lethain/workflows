"""Workflow execution runner."""

from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from typing import Any

from .inputs import NormalizedInput
from .registry import Registry, WorkflowConfig, get_registry
from .tools import Tool


@dataclass
class WorkflowResult:
    """Result from executing a single workflow."""

    workflow_name: str
    success: bool
    result: Any = None
    error: str | None = None
    traceback: str | None = None


@dataclass
class ExecutionResult:
    """Result from executing all matching workflows."""

    input_type: str
    workflow_results: list[WorkflowResult] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """True if all workflows succeeded."""
        return all(r.success for r in self.workflow_results)

    @property
    def errors(self) -> list[str]:
        """List of error messages from failed workflows."""
        return [r.error for r in self.workflow_results if r.error]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "input_type": self.input_type,
            "success": self.success,
            "workflow_results": [
                {
                    "workflow_name": r.workflow_name,
                    "success": r.success,
                    "result": r.result,
                    "error": r.error,
                }
                for r in self.workflow_results
            ],
        }


class WorkflowContext:
    """Context passed to workflow handlers during execution."""

    def __init__(
        self,
        normalized_input: NormalizedInput,
        tools: dict[str, Tool],
        config: WorkflowConfig,
    ) -> None:
        self.input = normalized_input
        self._tools = tools
        self.config = config

    def get_tool(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def call_tool(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Call a tool with the given arguments.

        Raises:
            ValueError: If tool not found or validation fails
        """
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found")
        return tool(*args, **kwargs)

    @property
    def available_tools(self) -> list[str]:
        """List of available tool names."""
        return list(self._tools.keys())


def run_workflow(
    config: WorkflowConfig,
    normalized_input: NormalizedInput,
    registry: Registry | None = None,
) -> WorkflowResult:
    """Execute a single workflow.

    Args:
        config: Workflow configuration
        normalized_input: Normalized input data
        registry: Registry to get tools from (uses global if not provided)

    Returns:
        WorkflowResult with success/failure info
    """
    if registry is None:
        registry = get_registry()

    # Get tools for this workflow
    tools = {t.name: t for t in registry.get_tools_for_workflow(config.name)}

    # Create context
    context = WorkflowContext(normalized_input, tools, config)

    try:
        handler = config.handler
        result = handler(context)
        return WorkflowResult(
            workflow_name=config.name,
            success=True,
            result=result,
        )
    except Exception as e:
        return WorkflowResult(
            workflow_name=config.name,
            success=False,
            error=str(e),
            traceback=traceback.format_exc(),
        )


def run_all(
    normalized_input: NormalizedInput,
    registry: Registry | None = None,
) -> ExecutionResult:
    """Execute all workflows matching the input type.

    Args:
        normalized_input: Normalized input data
        registry: Registry to use (uses global if not provided)

    Returns:
        ExecutionResult with results from all workflows
    """
    if registry is None:
        registry = get_registry()

    workflows = registry.get_workflows_for_input(normalized_input.input_type)
    results = ExecutionResult(input_type=normalized_input.input_type)

    for config in workflows:
        result = run_workflow(config, normalized_input, registry)
        results.workflow_results.append(result)

    return results
