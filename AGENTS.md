# Development Guide

## IMPORTANT: Before Finishing Any Task

**ALWAYS run linting and tests before considering any task complete:**

```bash
# Required before finishing
ruff check src tests && pytest
```

If either command fails, fix the issues before finishing.

---

## Setup

Install dependencies with uv:

```bash
uv sync --all-extras
source .venv/bin/activate
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Linting

Run ruff to check for linting issues:

```bash
ruff check src tests
```

Auto-fix issues:

```bash
ruff check src tests --fix
```

Format code:

```bash
ruff format src tests
```

## Type Checking

This project uses type hints throughout. The `py.typed` marker is included for PEP 561 compliance.

To check types with mypy (if installed separately):

```bash
pip install mypy
mypy src
```

## Testing

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run with coverage:

```bash
pytest --cov=workflows --cov-report=term-missing
```

Run a specific test file:

```bash
pytest tests/test_inputs.py
```

Run a specific test:

```bash
pytest tests/test_inputs.py::TestEmailInput::test_matches_ses_event
```

## Project Structure

```
workflows/
├── src/workflows/           # Main package
│   ├── inputs/              # Input type definitions (email, slack, webhook)
│   ├── prompts/             # Prompt loading from markdown
│   ├── skills/              # Skills system with dynamic loading
│   ├── handler.py           # AWS Lambda handler
│   ├── normalize.py         # Input normalization
│   ├── registry.py          # Workflow registry (YAML-based)
│   ├── runner.py            # Workflow execution
│   ├── storage.py           # YAML storage utilities
│   └── tools.py             # Tool definitions with parameter validation
├── config/                  # Configuration files
│   └── workflows.yaml       # Workflow definitions
├── prompts/                 # Prompt markdown files
├── tests/                   # Unit tests
└── pyproject.toml           # Project configuration
```

## Quick Commands

```bash
# ALWAYS run this before finishing any task
ruff check src tests && pytest

# Format and lint
ruff format src tests && ruff check src tests --fix

# Full validation cycle
ruff format src tests && ruff check src tests && pytest -v
```

## Checklist Before Completing Any Task

1. [ ] Run `ruff check src tests` - all checks must pass
2. [ ] Run `pytest` - all tests must pass
3. [ ] If you added new code, add corresponding tests
4. [ ] If you modified existing code, ensure existing tests still pass
