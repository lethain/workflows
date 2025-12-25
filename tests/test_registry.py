"""Tests for workflow registry."""

from __future__ import annotations

from pathlib import Path

from workflows.registry import Registry, WorkflowConfig, get_registry, reset_registry
from workflows.skills import SkillFilter
from workflows.tools import Tool


class TestWorkflowConfig:
    """Tests for WorkflowConfig."""

    def test_create_config(self) -> None:
        """Test creating a workflow config."""
        config = WorkflowConfig(
            name="test_workflow",
            module="test_module",
            function="test_function",
            input_types=["email", "slack"],
        )
        assert config.name == "test_workflow"
        assert config.input_types == ["email", "slack"]
        assert config.enabled is True

    def test_config_with_skill_filter(self) -> None:
        """Test config with skill filter."""
        skill_filter = SkillFilter(
            required=["req_skill"],
            allowed=["allowed_skill"],
            denied=["denied_skill"],
        )
        config = WorkflowConfig(
            name="test",
            module="test",
            function="test",
            input_types=[],
            skills=skill_filter,
        )
        assert config.skills.required == ["req_skill"]
        assert config.skills.allowed == ["allowed_skill"]


class TestRegistry:
    """Tests for Registry."""

    def test_register_workflow(self) -> None:
        """Test registering a workflow."""
        registry = Registry()
        config = WorkflowConfig(
            name="test",
            module="test",
            function="test",
            input_types=["email"],
        )
        registry.register_workflow(config)
        assert registry.get_workflow("test") == config

    def test_get_workflows_for_input(self) -> None:
        """Test getting workflows by input type."""
        registry = Registry()

        # Register email workflow
        email_wf = WorkflowConfig(
            name="email_wf",
            module="test",
            function="test",
            input_types=["email"],
        )
        registry.register_workflow(email_wf)

        # Register slack workflow
        slack_wf = WorkflowConfig(
            name="slack_wf",
            module="test",
            function="test",
            input_types=["slack"],
        )
        registry.register_workflow(slack_wf)

        # Register multi-input workflow
        multi_wf = WorkflowConfig(
            name="multi_wf",
            module="test",
            function="test",
            input_types=["email", "slack"],
        )
        registry.register_workflow(multi_wf)

        email_workflows = registry.get_workflows_for_input("email")
        assert len(email_workflows) == 2
        assert email_wf in email_workflows
        assert multi_wf in email_workflows

    def test_disabled_workflow_not_returned(self) -> None:
        """Test that disabled workflows are not returned."""
        registry = Registry()
        config = WorkflowConfig(
            name="disabled",
            module="test",
            function="test",
            input_types=["email"],
            enabled=False,
        )
        registry.register_workflow(config)

        assert registry.get_workflows_for_input("email") == []

    def test_register_tool(self) -> None:
        """Test registering a tool."""
        registry = Registry()

        def dummy_handler(x: str) -> str:
            return x

        tool = Tool(name="test_tool", description="Test", handler=dummy_handler)
        registry.register_tool(tool)
        assert registry.get_tool("test_tool") == tool

    def test_load_from_yaml(self, tmp_config_dir: Path) -> None:
        """Test loading from YAML config."""
        config_file = tmp_config_dir / "workflows.yaml"
        config_file.write_text(
            """
workflows:
  - name: test_workflow
    module: test_module
    function: handle
    input_types:
      - email
    skills:
      required:
        - skill_a
      allowed:
        - skill_b
      denied:
        - skill_c
"""
        )

        registry = Registry()
        registry.load_from_yaml(config_file)

        wf = registry.get_workflow("test_workflow")
        assert wf is not None
        assert wf.name == "test_workflow"
        assert wf.input_types == ["email"]
        assert wf.skills.required == ["skill_a"]
        assert wf.skills.allowed == ["skill_b"]
        assert wf.skills.denied == ["skill_c"]


class TestGlobalRegistry:
    """Tests for global registry functions."""

    def test_get_registry_singleton(self) -> None:
        """Test that get_registry returns the same instance."""
        reset_registry()
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_reset_registry(self) -> None:
        """Test resetting the global registry."""
        reset_registry()
        r1 = get_registry()
        reset_registry()
        r2 = get_registry()
        assert r1 is not r2
