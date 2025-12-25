"""Tests for input normalization."""

from __future__ import annotations

from typing import Any

import pytest

from workflows.normalize import detect_input_type, normalize, normalize_with_type


class TestDetectInputType:
    """Tests for input type detection."""

    def test_detect_email(self, sample_email_event: dict[str, Any]) -> None:
        """Test detecting email events."""
        assert detect_input_type(sample_email_event) == "email"

    def test_detect_slack(self, sample_slack_event: dict[str, Any]) -> None:
        """Test detecting Slack events."""
        assert detect_input_type(sample_slack_event) == "slack"

    def test_detect_webhook(self, sample_webhook_event: dict[str, Any]) -> None:
        """Test detecting webhook events."""
        assert detect_input_type(sample_webhook_event) == "webhook"

    def test_detect_unknown(self) -> None:
        """Test unknown event type."""
        assert detect_input_type({"unknown": "event"}) == "unknown"


class TestNormalize:
    """Tests for the normalize function."""

    def test_normalize_email(self, sample_direct_email_event: dict[str, Any]) -> None:
        """Test normalizing email event."""
        normalized = normalize(sample_direct_email_event)
        assert normalized.input_type == "email"
        assert normalized.source == "sender@example.com"
        assert normalized.content == "This is a test email body."

    def test_normalize_slack(self, sample_slack_event: dict[str, Any]) -> None:
        """Test normalizing Slack event."""
        normalized = normalize(sample_slack_event)
        assert normalized.input_type == "slack"
        assert normalized.source == "U123456"
        assert normalized.content == "Hello from Slack!"

    def test_normalize_webhook(self, sample_webhook_event: dict[str, Any]) -> None:
        """Test normalizing webhook event."""
        normalized = normalize(sample_webhook_event)
        assert normalized.input_type == "webhook"
        assert normalized.source == "192.168.1.1"

    def test_normalize_unknown_raises(self) -> None:
        """Test that unknown events raise ValueError."""
        with pytest.raises(ValueError, match="Unable to determine input type"):
            normalize({"unknown": "event"})


class TestNormalizeWithType:
    """Tests for explicit type normalization."""

    def test_normalize_with_email_type(self, sample_direct_email_event: dict[str, Any]) -> None:
        """Test normalizing with explicit email type."""
        normalized = normalize_with_type(sample_direct_email_event, "email")
        assert normalized.input_type == "email"

    def test_normalize_with_invalid_type(self) -> None:
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown input type"):
            normalize_with_type({}, "invalid")
