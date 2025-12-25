"""Tool definitions with parameter validation."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParameterConstraint:
    """Constraint for a tool parameter.

    Can validate using:
    - allowed_values: Set of exact allowed values
    - pattern: Regex pattern the value must match
    - validator: Custom validation function
    """

    allowed_values: set[str] | None = None
    pattern: str | None = None
    validator: Callable[[Any], bool] | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        """Compile regex pattern if provided."""
        self._compiled_pattern: re.Pattern[str] | None = None
        if self.pattern:
            self._compiled_pattern = re.compile(self.pattern)

    def validate(self, value: Any) -> tuple[bool, str | None]:
        """Validate a value against this constraint.

        Returns:
            Tuple of (is_valid, error_message)
        """
        str_value = str(value)

        if self.allowed_values is not None and str_value not in self.allowed_values:
            msg = self.error_message or f"Value '{str_value}' not in allowed values"
            return False, msg

        if self._compiled_pattern is not None and not self._compiled_pattern.match(str_value):
            msg = (
                self.error_message or f"Value '{str_value}' does not match pattern '{self.pattern}'"
            )
            return False, msg

        if self.validator is not None and not self.validator(value):
            msg = self.error_message or f"Value '{value}' failed custom validation"
            return False, msg

        return True, None


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""

    name: str
    description: str = ""
    required: bool = True
    default: Any = None
    constraint: ParameterConstraint | None = None

    def validate(self, value: Any) -> tuple[bool, str | None]:
        """Validate a value for this parameter."""
        if value is None:
            if self.required and self.default is None:
                return False, f"Required parameter '{self.name}' is missing"
            return True, None

        if self.constraint:
            return self.constraint.validate(value)

        return True, None


@dataclass
class Tool:
    """A tool that can be used by workflows.

    Supports parameter validation with sets and regex patterns.
    """

    name: str
    description: str
    handler: Callable[..., Any]
    parameters: list[ToolParameter] = field(default_factory=list)

    def validate_args(self, *args: Any, **kwargs: Any) -> list[str]:
        """Validate arguments against parameter constraints.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors: list[str] = []

        # Validate positional args
        for i, (param, value) in enumerate(zip(self.parameters, args, strict=False)):
            is_valid, error = param.validate(value)
            if not is_valid:
                errors.append(f"Parameter {i} ({param.name}): {error}")

        # Validate keyword args
        param_map = {p.name: p for p in self.parameters}
        for name, value in kwargs.items():
            if name in param_map:
                is_valid, error = param_map[name].validate(value)
                if not is_valid:
                    errors.append(f"Parameter '{name}': {error}")

        # Check for missing required parameters
        provided = set(kwargs.keys()) | {p.name for p in self.parameters[: len(args)]}
        for param in self.parameters:
            if param.required and param.name not in provided and param.default is None:
                errors.append(f"Missing required parameter: {param.name}")

        return errors

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the tool with validation.

        Raises:
            ValueError: If parameter validation fails
        """
        errors = self.validate_args(*args, **kwargs)
        if errors:
            raise ValueError(f"Tool '{self.name}' validation failed: {'; '.join(errors)}")

        return self.handler(*args, **kwargs)


def url_domain_constraint(allowed_domains: set[str]) -> ParameterConstraint:
    """Create a constraint that only allows URLs from specific domains.

    Example:
        constraint = url_domain_constraint({"example.com", "api.example.com"})
    """
    pattern = "|".join(re.escape(d) for d in allowed_domains)
    return ParameterConstraint(
        pattern=rf"^https?://({pattern})/.*",
        error_message=f"URL must be from one of: {', '.join(allowed_domains)}",
    )


def url_prefix_constraint(prefix: str) -> ParameterConstraint:
    """Create a constraint that only allows URLs starting with a prefix.

    Example:
        constraint = url_prefix_constraint("https://api.example.com/v1/")
    """
    return ParameterConstraint(
        pattern=rf"^{re.escape(prefix)}.*",
        error_message=f"URL must start with: {prefix}",
    )
