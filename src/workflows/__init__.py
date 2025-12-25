"""Workflows - Python agent workflow library for AWS Lambda."""

from .handler import handler
from .inputs import EmailInput, Input, NormalizedInput, SlackInput, WebhookInput
from .normalize import detect_input_type, normalize, normalize_with_type
from .prompts import Prompt, get_prompt_for_workflow, load_prompt, load_prompts
from .registry import Registry, WorkflowConfig, get_registry, reset_registry
from .runner import ExecutionResult, WorkflowContext, WorkflowResult, run_all, run_workflow
from .skills import (
    SkillFilter,
    SkillProperties,
    ValidationProblem,
    build_system_prompt,
    load_all_skills,
    read_properties,
    to_prompt,
    validate,
)
from .storage import get_config_dir, get_data_dir, read_yaml, write_yaml
from .tools import (
    ParameterConstraint,
    Tool,
    ToolParameter,
    url_domain_constraint,
    url_prefix_constraint,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Handler
    "handler",
    # Inputs
    "Input",
    "NormalizedInput",
    "EmailInput",
    "SlackInput",
    "WebhookInput",
    # Normalize
    "normalize",
    "normalize_with_type",
    "detect_input_type",
    # Registry
    "Registry",
    "WorkflowConfig",
    "get_registry",
    "reset_registry",
    # Runner
    "WorkflowResult",
    "ExecutionResult",
    "WorkflowContext",
    "run_workflow",
    "run_all",
    # Prompts
    "Prompt",
    "load_prompt",
    "load_prompts",
    "get_prompt_for_workflow",
    # Skills
    "SkillProperties",
    "SkillFilter",
    "ValidationProblem",
    "validate",
    "read_properties",
    "load_all_skills",
    "to_prompt",
    "build_system_prompt",
    # Storage
    "read_yaml",
    "write_yaml",
    "get_config_dir",
    "get_data_dir",
    # Tools
    "Tool",
    "ToolParameter",
    "ParameterConstraint",
    "url_domain_constraint",
    "url_prefix_constraint",
]
