"""Pytest fixtures for workflow tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from workflows import reset_registry


@pytest.fixture(autouse=True)
def reset_global_registry() -> None:
    """Reset the global registry before each test."""
    reset_registry()


@pytest.fixture
def sample_email_event() -> dict[str, Any]:
    """Sample SES email event."""
    return {
        "Records": [
            {
                "eventSource": "aws:ses",
                "ses": {
                    "mail": {
                        "timestamp": "2024-01-15T10:30:00Z",
                        "source": "sender@example.com",
                        "commonHeaders": {
                            "from": ["sender@example.com"],
                            "to": ["recipient@example.com"],
                            "subject": "Test Email",
                        },
                        "headers": [],
                    },
                },
            }
        ]
    }


@pytest.fixture
def sample_direct_email_event() -> dict[str, Any]:
    """Sample direct email event format."""
    return {
        "sender": "sender@example.com",
        "recipient": "recipient@example.com",
        "subject": "Test Email",
        "body": "This is a test email body.",
        "timestamp": "2024-01-15T10:30:00+00:00",
    }


@pytest.fixture
def sample_slack_event() -> dict[str, Any]:
    """Sample Slack event API payload."""
    return {
        "api_app_id": "A123456",
        "team_id": "T123456",
        "event": {
            "type": "message",
            "user": "U123456",
            "channel": "C123456",
            "text": "Hello from Slack!",
            "ts": "1705315800.000000",
        },
    }


@pytest.fixture
def sample_webhook_event() -> dict[str, Any]:
    """Sample API Gateway v2 (HTTP API) event."""
    return {
        "requestContext": {
            "http": {
                "method": "POST",
                "path": "/webhook",
                "sourceIp": "192.168.1.1",
            },
        },
        "headers": {
            "content-type": "application/json",
        },
        "body": '{"action": "test"}',
        "queryStringParameters": {
            "source": "external",
        },
    }


@pytest.fixture
def sample_apigw_v1_event() -> dict[str, Any]:
    """Sample API Gateway v1 (REST API) event."""
    return {
        "httpMethod": "POST",
        "path": "/webhook",
        "headers": {
            "Content-Type": "application/json",
        },
        "body": '{"action": "test"}',
        "queryStringParameters": {
            "source": "external",
        },
        "requestContext": {
            "identity": {
                "sourceIp": "192.168.1.1",
            },
        },
    }


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def tmp_skills_dir(tmp_path: Path) -> Path:
    """Create a temporary skills directory with sample skills."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # Create a sample skill
    skill_dir = skills_dir / "web_search"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: web_search
description: Search the web for information
version: "1.0"
author: test
tags:
  - search
  - web
---

# Web Search Skill

Use this skill to search the web for information.

## Usage

Call the web search with a query string.
"""
    )

    # Create another sample skill
    skill_dir2 = skills_dir / "summarize"
    skill_dir2.mkdir()
    (skill_dir2 / "SKILL.md").write_text(
        """---
name: summarize
description: Summarize text content
version: "1.0"
---

# Summarize Skill

Summarize long text into concise points.
"""
    )

    return skills_dir


@pytest.fixture
def tmp_prompts_dir(tmp_path: Path) -> Path:
    """Create a temporary prompts directory with sample prompts."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    (prompts_dir / "test_prompt.md").write_text(
        """---
name: test_prompt
description: A test prompt
version: "1.0"
workflow: test_workflow
---

# Test Prompt

This is test prompt content.
"""
    )

    return prompts_dir
