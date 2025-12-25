# workflows

Python agent workflow library for AWS Lambda. Processes events from various sources (email, Slack, webhooks) through configurable workflows with skill integration.

## Installation

### Using uv (Recommended)

```bash
uv sync
source .venv/bin/activate
```

For development dependencies (ruff, pytest):

```bash
uv sync --all-extras
source .venv/bin/activate
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Running

### Local Testing

```python
from workflows import normalize, get_registry, run_all
from pathlib import Path

# Load workflow configuration
registry = get_registry()
registry.load_from_yaml(Path("config/workflows.yaml"))

# Process an event
event = {
    "sender": "user@example.com",
    "recipient": "app@example.com",
    "subject": "Test",
    "body": "Hello world"
}

normalized = normalize(event)
result = run_all(normalized)
print(result.to_dict())
```

### AWS Lambda

Set the handler to `workflows.handler`:

```python
# The Lambda entry point
from workflows import handler

def lambda_handler(event, context):
    return handler(event, context)
```

Environment variables:
- `WORKFLOWS_CONFIG` - Path to workflows.yaml (default: `config/workflows.yaml`)
- `WORKFLOWS_CONFIG_DIR` - Config directory (default: `config`)
- `WORKFLOWS_DATA_DIR` - Data directory (default: `data`)

## Linting

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Check for issues
ruff check src tests

# Auto-fix issues
ruff check src tests --fix

# Format code
ruff format src tests

# Check and format in one command
ruff format src tests && ruff check src tests --fix
```

## Testing

This project uses [pytest](https://docs.pytest.org/) for testing.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=workflows --cov-report=term-missing

# Run specific test file
pytest tests/test_inputs.py

# Run specific test class
pytest tests/test_inputs.py::TestEmailInput

# Run specific test
pytest tests/test_inputs.py::TestEmailInput::test_matches_ses_event

# Run tests matching a pattern
pytest -k "email"
```

## Type Checking

The project uses strict mypy type checking. Mypy is included in dev dependencies.

```bash
# Run type checking
mypy src
```

All code must pass mypy with strict settings. Configuration is in `pyproject.toml`.

## Quick Start

### 1. Define a Workflow Handler

Create a workflow handler in your module:

```python
# my_workflows/email.py
from workflows import WorkflowContext

def process_email(ctx: WorkflowContext) -> dict:
    """Handle incoming emails."""
    print(f"Processing email from: {ctx.input.source}")
    print(f"Subject: {ctx.input.metadata.get('subject')}")
    print(f"Content: {ctx.input.content}")

    # Access tools if configured
    if "fetch_url" in ctx.available_tools:
        result = ctx.call_tool("fetch_url", "https://api.example.com/data")

    return {"status": "processed", "source": ctx.input.source}
```

### 2. Configure Workflows

Edit `config/workflows.yaml`:

```yaml
workflows:
  - name: email_processor
    module: my_workflows.email
    function: process_email
    input_types:
      - email
    tools:
      - fetch_url
    skills:
      required:
        - email_response
      allowed:
        - web_search
      denied: []
    enabled: true

  - name: slack_handler
    module: my_workflows.slack
    function: handle_message
    input_types:
      - slack
    skills:
      allowed:
        - summarize
    enabled: true
```

### 3. Register Tools

```python
from workflows import get_registry, Tool, ToolParameter, url_domain_constraint

registry = get_registry()

# Register a tool with URL validation
fetch_tool = Tool(
    name="fetch_url",
    description="Fetch content from allowed domains",
    handler=lambda url: requests.get(url).text,
    parameters=[
        ToolParameter(
            name="url",
            constraint=url_domain_constraint({"api.example.com", "docs.example.com"})
        )
    ]
)
registry.register_tool(fetch_tool)
```

### 4. Create Skills

Create a skill directory with a `SKILL.md` file:

```
skills/
└── web_search/
    └── SKILL.md
```

`skills/web_search/SKILL.md`:

```markdown
---
name: web_search
description: Search the web for information
version: "1.0"
author: your-team
tags:
  - search
  - web
---

# Web Search Skill

Use this skill to search the web for information.

## Usage

Call the web search with a query string to find relevant results.
```

### 5. Create Prompts

Create prompt files in `prompts/`:

```markdown
---
name: email_processor
description: Process incoming emails
workflow: email_processor
version: "1.0"
---

# Email Processor

You are an email processing assistant. Your task is to:

1. Analyze the incoming email
2. Identify key action items
3. Generate an appropriate response
```

## Features

### Input Normalization

All inputs are normalized to a common `NormalizedInput` format:

```python
from workflows import normalize, detect_input_type

# Auto-detect and normalize
normalized = normalize(event)
print(normalized.input_type)  # "email", "slack", or "webhook"
print(normalized.source)       # sender/user/IP
print(normalized.content)      # message body
print(normalized.metadata)     # type-specific fields
print(normalized.timestamp)    # when received
print(normalized.raw)          # original event

# Just detect type
input_type = detect_input_type(event)
```

### Supported Input Types

**Email** (AWS SES or direct format):
```python
# SES format
{"Records": [{"eventSource": "aws:ses", "ses": {...}}]}

# Direct format
{"sender": "...", "recipient": "...", "subject": "...", "body": "..."}
```

**Slack** (Event API format):
```python
{"api_app_id": "...", "event": {"type": "message", "user": "...", "text": "..."}}
```

**Webhook** (API Gateway v1/v2):
```python
# API Gateway v2
{"requestContext": {"http": {"method": "POST", "path": "/webhook"}}, "body": "..."}

# API Gateway v1
{"httpMethod": "POST", "path": "/webhook", "body": "..."}
```

### Tool Parameter Validation

Define constraints using sets, regex patterns, or custom validators:

```python
from workflows import Tool, ToolParameter, ParameterConstraint, url_domain_constraint, url_prefix_constraint

# Set of allowed values
ParameterConstraint(allowed_values={"GET", "POST", "PUT"})

# Regex pattern
ParameterConstraint(pattern=r"^https://.*")

# Custom validator
ParameterConstraint(validator=lambda x: x > 0)

# URL domain constraint helper
url_domain_constraint({"api.example.com", "cdn.example.com"})

# URL prefix constraint helper
url_prefix_constraint("https://api.example.com/v1/")
```

### Skills System

Skills are loaded dynamically and filtered per workflow:

```python
from workflows import load_all_skills, build_system_prompt, SkillFilter
from pathlib import Path

# Load all skills
skills = load_all_skills(Path("skills"))

# Filter for a specific workflow
skill_filter = SkillFilter(
    required=["email_response"],  # Loaded into system prompt
    allowed=["web_search"],       # Shown in <available_skills>
    denied=["admin_tools"]        # Excluded entirely
)

# Build system prompt with skills
prompt = build_system_prompt(
    base_prompt="You are a helpful assistant.",
    all_skills=skills,
    skill_filter=skill_filter
)
```

### Prompts

Load prompts from markdown files:

```python
from workflows import load_prompt, load_prompts, get_prompt_for_workflow
from pathlib import Path

# Load single prompt
prompt = load_prompt(Path("prompts/email.md"))
print(prompt.name, prompt.description, prompt.content)

# Load all prompts
prompts = load_prompts(Path("prompts"))

# Get prompt for a workflow
prompt = get_prompt_for_workflow("email_processor", Path("prompts"))
```

## Project Structure

```
workflows/
├── pyproject.toml           # Package configuration
├── README.md                # This file
├── AGENTS.md                # Developer guide
├── CLAUDE.md                # Points to AGENTS.md
├── config/
│   └── workflows.yaml       # Workflow definitions
├── prompts/
│   └── example.md           # Example prompt
├── src/workflows/
│   ├── __init__.py          # Public API
│   ├── handler.py           # Lambda handler
│   ├── normalize.py         # Input normalization
│   ├── registry.py          # Workflow registry
│   ├── runner.py            # Workflow execution
│   ├── storage.py           # YAML utilities
│   ├── tools.py             # Tool definitions
│   ├── inputs/              # Input types
│   │   ├── base.py          # NormalizedInput
│   │   ├── email.py         # EmailInput
│   │   ├── slack.py         # SlackInput
│   │   └── webhook.py       # WebhookInput
│   ├── prompts/             # Prompt loading
│   │   ├── loader.py        # Load from markdown
│   │   └── types.py         # Prompt dataclass
│   └── skills/              # Skills system
│       ├── loader.py        # Load/validate skills
│       └── types.py         # SkillProperties, SkillFilter
└── tests/                   # Unit tests (86 tests)
```

## API Reference

### Core Exports

```python
from workflows import (
    # Handler
    handler,

    # Inputs
    normalize, normalize_with_type, detect_input_type,
    NormalizedInput, EmailInput, SlackInput, WebhookInput,

    # Registry
    Registry, WorkflowConfig, get_registry, reset_registry,

    # Runner
    run_workflow, run_all, WorkflowContext, WorkflowResult, ExecutionResult,

    # Tools
    Tool, ToolParameter, ParameterConstraint,
    url_domain_constraint, url_prefix_constraint,

    # Prompts
    Prompt, load_prompt, load_prompts, get_prompt_for_workflow,

    # Skills
    SkillProperties, SkillFilter, ValidationProblem,
    validate, read_properties, load_all_skills, to_prompt, build_system_prompt,

    # Storage
    read_yaml, write_yaml, get_config_dir, get_data_dir,
)
```

## Development

See [AGENTS.md](AGENTS.md) for detailed development instructions.

Quick reference:

```bash
# Install with dev dependencies
uv sync --all-extras

# Lint, type check, and test (required before any PR)
ruff check src tests && mypy src && pytest

# Format
ruff format src tests
```

## CI

This project uses GitHub Actions for continuous integration. On every push and pull request:

- **Lint**: ruff check and format verification
- **Type Check**: mypy with strict settings
- **Test**: pytest on Python 3.11, 3.12, and 3.13

## License

MIT
