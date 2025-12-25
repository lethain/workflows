"""Tests for tools and parameter validation."""

from __future__ import annotations

import pytest

from workflows.tools import (
    ParameterConstraint,
    Tool,
    ToolParameter,
    url_domain_constraint,
    url_prefix_constraint,
)


class TestParameterConstraint:
    """Tests for ParameterConstraint."""

    def test_allowed_values_valid(self) -> None:
        """Test validation with allowed values - valid case."""
        constraint = ParameterConstraint(allowed_values={"a", "b", "c"})
        is_valid, error = constraint.validate("a")
        assert is_valid
        assert error is None

    def test_allowed_values_invalid(self) -> None:
        """Test validation with allowed values - invalid case."""
        constraint = ParameterConstraint(allowed_values={"a", "b", "c"})
        is_valid, error = constraint.validate("d")
        assert not is_valid
        assert "not in allowed values" in error

    def test_pattern_valid(self) -> None:
        """Test validation with regex pattern - valid case."""
        constraint = ParameterConstraint(pattern=r"^https://.*")
        is_valid, error = constraint.validate("https://example.com")
        assert is_valid

    def test_pattern_invalid(self) -> None:
        """Test validation with regex pattern - invalid case."""
        constraint = ParameterConstraint(pattern=r"^https://.*")
        is_valid, error = constraint.validate("http://example.com")
        assert not is_valid
        assert "does not match pattern" in error

    def test_custom_validator(self) -> None:
        """Test validation with custom function."""
        constraint = ParameterConstraint(validator=lambda x: x > 0)
        assert constraint.validate(5)[0]
        assert not constraint.validate(-1)[0]

    def test_custom_error_message(self) -> None:
        """Test custom error message."""
        constraint = ParameterConstraint(
            allowed_values={"yes"},
            error_message="Only 'yes' is allowed",
        )
        is_valid, error = constraint.validate("no")
        assert error == "Only 'yes' is allowed"


class TestUrlConstraints:
    """Tests for URL constraint helpers."""

    def test_domain_constraint_valid(self) -> None:
        """Test domain constraint with valid URL."""
        constraint = url_domain_constraint({"example.com", "api.example.com"})
        is_valid, _ = constraint.validate("https://example.com/path")
        assert is_valid

    def test_domain_constraint_invalid(self) -> None:
        """Test domain constraint with invalid URL."""
        constraint = url_domain_constraint({"example.com"})
        is_valid, error = constraint.validate("https://evil.com/path")
        assert not is_valid
        assert "must be from one of" in error

    def test_prefix_constraint_valid(self) -> None:
        """Test prefix constraint with valid URL."""
        constraint = url_prefix_constraint("https://api.example.com/v1/")
        is_valid, _ = constraint.validate("https://api.example.com/v1/users")
        assert is_valid

    def test_prefix_constraint_invalid(self) -> None:
        """Test prefix constraint with invalid URL."""
        constraint = url_prefix_constraint("https://api.example.com/v1/")
        is_valid, error = constraint.validate("https://api.example.com/v2/users")
        assert not is_valid


class TestToolParameter:
    """Tests for ToolParameter."""

    def test_required_parameter_missing(self) -> None:
        """Test required parameter that is missing."""
        param = ToolParameter(name="url", required=True)
        is_valid, error = param.validate(None)
        assert not is_valid
        assert "Required parameter" in error

    def test_required_parameter_present(self) -> None:
        """Test required parameter that is present."""
        param = ToolParameter(name="url", required=True)
        is_valid, _ = param.validate("https://example.com")
        assert is_valid

    def test_optional_parameter_missing(self) -> None:
        """Test optional parameter that is missing."""
        param = ToolParameter(name="timeout", required=False)
        is_valid, _ = param.validate(None)
        assert is_valid

    def test_parameter_with_constraint(self) -> None:
        """Test parameter with constraint."""
        param = ToolParameter(
            name="url",
            constraint=ParameterConstraint(pattern=r"^https://.*"),
        )
        is_valid, _ = param.validate("https://example.com")
        assert is_valid

        is_valid, _ = param.validate("http://example.com")
        assert not is_valid


class TestTool:
    """Tests for Tool."""

    def test_tool_execution(self) -> None:
        """Test basic tool execution."""

        def handler(x: int, y: int) -> int:
            return x + y

        tool = Tool(name="add", description="Add numbers", handler=handler)
        result = tool(1, 2)
        assert result == 3

    def test_tool_validation_fails(self) -> None:
        """Test tool validation failure."""

        def handler(url: str) -> str:
            return url

        tool = Tool(
            name="fetch",
            description="Fetch URL",
            handler=handler,
            parameters=[
                ToolParameter(
                    name="url",
                    constraint=ParameterConstraint(pattern=r"^https://example\.com/.*"),
                )
            ],
        )

        with pytest.raises(ValueError, match="validation failed"):
            tool("https://evil.com/hack")

    def test_tool_validation_succeeds(self) -> None:
        """Test tool validation success."""

        def handler(url: str) -> str:
            return f"Fetched: {url}"

        tool = Tool(
            name="fetch",
            description="Fetch URL",
            handler=handler,
            parameters=[
                ToolParameter(
                    name="url",
                    constraint=ParameterConstraint(pattern=r"^https://example\.com/.*"),
                )
            ],
        )

        result = tool("https://example.com/api")
        assert result == "Fetched: https://example.com/api"

    def test_missing_required_parameter(self) -> None:
        """Test missing required parameter."""

        def handler(url: str, _timeout: int = 30) -> str:
            return url

        tool = Tool(
            name="fetch",
            description="Fetch URL",
            handler=handler,
            parameters=[
                ToolParameter(name="url", required=True),
                ToolParameter(name="timeout", required=False, default=30),
            ],
        )

        errors = tool.validate_args()
        assert any("Missing required parameter: url" in e for e in errors)
