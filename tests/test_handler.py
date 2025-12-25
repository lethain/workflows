"""Tests for Lambda handler."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from workflows import get_registry, handler, reset_registry
from workflows.registry import WorkflowConfig
from workflows.runner import WorkflowContext


def sample_workflow_handler(ctx: WorkflowContext) -> dict[str, Any]:
    """Sample workflow handler for testing."""
    return {
        "processed": True,
        "input_type": ctx.input.input_type,
        "source": ctx.input.source,
    }


def failing_workflow_handler(_ctx: WorkflowContext) -> None:
    """Sample workflow that always fails."""
    raise ValueError("Intentional failure")


class TestHandler:
    """Tests for Lambda handler."""

    def test_handler_success(self, sample_direct_email_event: dict[str, Any]) -> None:
        """Test successful handler execution."""
        reset_registry()
        registry = get_registry()

        # Register a test workflow
        config = WorkflowConfig(
            name="test_email",
            module="tests.test_handler",
            function="sample_workflow_handler",
            input_types=["email"],
        )
        registry.register_workflow(config)

        result = handler(sample_direct_email_event, None)
        assert result["statusCode"] == 200

        body = json.loads(result["body"])
        assert body["success"] is True
        assert body["input_type"] == "email"

    def test_handler_with_failing_workflow(self, sample_direct_email_event: dict[str, Any]) -> None:
        """Test handler with a failing workflow."""
        reset_registry()
        registry = get_registry()

        config = WorkflowConfig(
            name="failing_workflow",
            module="tests.test_handler",
            function="failing_workflow_handler",
            input_types=["email"],
        )
        registry.register_workflow(config)

        result = handler(sample_direct_email_event, None)
        assert result["statusCode"] == 500

        body = json.loads(result["body"])
        assert body["success"] is False

    def test_handler_invalid_input(self) -> None:
        """Test handler with invalid input."""
        reset_registry()

        result = handler({"unknown": "format"}, None)
        assert result["statusCode"] == 400

        body = json.loads(result["body"])
        assert "error" in body
        assert body["error"] == "Invalid input"

    def test_handler_no_matching_workflows(self, sample_slack_event: dict[str, Any]) -> None:
        """Test handler when no workflows match."""
        reset_registry()
        registry = get_registry()

        # Register email-only workflow
        config = WorkflowConfig(
            name="email_only",
            module="tests.test_handler",
            function="sample_workflow_handler",
            input_types=["email"],
        )
        registry.register_workflow(config)

        # Send slack event
        result = handler(sample_slack_event, None)
        assert result["statusCode"] == 200

        body = json.loads(result["body"])
        assert body["workflow_results"] == []


class TestWorkflowContext:
    """Tests for WorkflowContext."""

    def test_context_tool_access(self) -> None:
        """Test accessing tools from context."""
        from workflows.inputs import NormalizedInput
        from workflows.tools import Tool

        def dummy_tool(x: str) -> str:
            return f"processed: {x}"

        tool = Tool(name="dummy", description="Dummy tool", handler=dummy_tool)

        ctx = WorkflowContext(
            normalized_input=NormalizedInput(
                input_type="test",
                source="test",
                content="test content",
            ),
            tools={"dummy": tool},
            config=MagicMock(),
        )

        assert "dummy" in ctx.available_tools
        result = ctx.call_tool("dummy", "input")
        assert result == "processed: input"

    def test_context_missing_tool(self) -> None:
        """Test calling missing tool raises error."""
        from workflows.inputs import NormalizedInput

        ctx = WorkflowContext(
            normalized_input=NormalizedInput(
                input_type="test",
                source="test",
                content="test",
            ),
            tools={},
            config=MagicMock(),
        )

        with pytest.raises(ValueError, match="not found"):
            ctx.call_tool("nonexistent")
