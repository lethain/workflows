# Development Guide

## IMPORTANT: Before Finishing Any Task

**ALWAYS run linting, type checking, and tests before considering any task complete:**

```bash
# Required before finishing - ALL must pass
ruff format --check src tests
ruff check src tests
mypy src
pytest
```

Or as a single command:

```bash
ruff format --check src tests && ruff check src tests && mypy src && pytest
```

If any command fails, fix the issues before finishing.

To auto-fix formatting issues:

```bash
ruff format src tests
```

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

## Formatting

Check formatting:

```bash
ruff format --check src tests
```

Fix formatting:

```bash
ruff format src tests
```

## Type Checking

This project uses strict mypy type checking. **Type checking is required.**

```bash
mypy src
```

All code must pass mypy with no errors. The project is configured with strict settings in `pyproject.toml`.

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
ruff format --check src tests && ruff check src tests && mypy src && pytest

# Fix formatting, then lint, type check, and test
ruff format src tests && ruff check src tests --fix && mypy src && pytest -v
```

## Checklist Before Completing Any Task

1. [ ] Run `ruff format --check src tests` - formatting must be correct
2. [ ] Run `ruff check src tests` - all lint checks must pass
3. [ ] Run `mypy src` - all type checks must pass
4. [ ] Run `pytest` - all tests must pass
5. [ ] If you added new code, add corresponding tests
6. [ ] If you modified existing code, ensure existing tests still pass
