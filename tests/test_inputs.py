"""Tests for input type parsing."""

from __future__ import annotations

from typing import Any

from workflows.inputs import EmailInput, NormalizedInput, SlackInput, WebhookInput


class TestEmailInput:
    """Tests for EmailInput parsing."""

    def test_matches_ses_event(self, sample_email_event: dict[str, Any]) -> None:
        """Test that SES events are correctly identified."""
        assert EmailInput.matches(sample_email_event)

    def test_matches_direct_email(self, sample_direct_email_event: dict[str, Any]) -> None:
        """Test that direct email format is identified."""
        assert EmailInput.matches(sample_direct_email_event)

    def test_does_not_match_slack(self, sample_slack_event: dict[str, Any]) -> None:
        """Test that Slack events are not matched."""
        assert not EmailInput.matches(sample_slack_event)

    def test_from_ses_event(self, sample_email_event: dict[str, Any]) -> None:
        """Test parsing SES event."""
        email = EmailInput.from_event(sample_email_event)
        assert email.sender == "sender@example.com"
        assert email.recipient == "recipient@example.com"
        assert email.subject == "Test Email"

    def test_from_direct_event(self, sample_direct_email_event: dict[str, Any]) -> None:
        """Test parsing direct email format."""
        email = EmailInput.from_event(sample_direct_email_event)
        assert email.sender == "sender@example.com"
        assert email.recipient == "recipient@example.com"
        assert email.subject == "Test Email"
        assert email.body == "This is a test email body."

    def test_to_normalized(self, sample_direct_email_event: dict[str, Any]) -> None:
        """Test converting to normalized input."""
        email = EmailInput.from_event(sample_direct_email_event)
        normalized = email.to_normalized()

        assert isinstance(normalized, NormalizedInput)
        assert normalized.input_type == "email"
        assert normalized.source == "sender@example.com"
        assert normalized.content == "This is a test email body."
        assert normalized.metadata["subject"] == "Test Email"


class TestSlackInput:
    """Tests for SlackInput parsing."""

    def test_matches_slack_event(self, sample_slack_event: dict[str, Any]) -> None:
        """Test that Slack events are correctly identified."""
        assert SlackInput.matches(sample_slack_event)

    def test_does_not_match_email(self, sample_email_event: dict[str, Any]) -> None:
        """Test that email events are not matched."""
        assert not SlackInput.matches(sample_email_event)

    def test_from_event(self, sample_slack_event: dict[str, Any]) -> None:
        """Test parsing Slack event."""
        slack = SlackInput.from_event(sample_slack_event)
        assert slack.user_id == "U123456"
        assert slack.channel_id == "C123456"
        assert slack.text == "Hello from Slack!"
        assert slack.team_id == "T123456"

    def test_to_normalized(self, sample_slack_event: dict[str, Any]) -> None:
        """Test converting to normalized input."""
        slack = SlackInput.from_event(sample_slack_event)
        normalized = slack.to_normalized()

        assert isinstance(normalized, NormalizedInput)
        assert normalized.input_type == "slack"
        assert normalized.source == "U123456"
        assert normalized.content == "Hello from Slack!"
        assert normalized.metadata["channel_id"] == "C123456"


class TestWebhookInput:
    """Tests for WebhookInput parsing."""

    def test_matches_apigw_v2(self, sample_webhook_event: dict[str, Any]) -> None:
        """Test that API Gateway v2 events are identified."""
        assert WebhookInput.matches(sample_webhook_event)

    def test_matches_apigw_v1(self, sample_apigw_v1_event: dict[str, Any]) -> None:
        """Test that API Gateway v1 events are identified."""
        assert WebhookInput.matches(sample_apigw_v1_event)

    def test_from_apigw_v2(self, sample_webhook_event: dict[str, Any]) -> None:
        """Test parsing API Gateway v2 event."""
        webhook = WebhookInput.from_event(sample_webhook_event)
        assert webhook.method == "POST"
        assert webhook.path == "/webhook"
        assert webhook.source_ip == "192.168.1.1"
        assert webhook.body == '{"action": "test"}'

    def test_from_apigw_v1(self, sample_apigw_v1_event: dict[str, Any]) -> None:
        """Test parsing API Gateway v1 event."""
        webhook = WebhookInput.from_event(sample_apigw_v1_event)
        assert webhook.method == "POST"
        assert webhook.path == "/webhook"
        assert webhook.source_ip == "192.168.1.1"

    def test_to_normalized(self, sample_webhook_event: dict[str, Any]) -> None:
        """Test converting to normalized input."""
        webhook = WebhookInput.from_event(sample_webhook_event)
        normalized = webhook.to_normalized()

        assert isinstance(normalized, NormalizedInput)
        assert normalized.input_type == "webhook"
        assert normalized.source == "192.168.1.1"
        assert normalized.metadata["method"] == "POST"
        assert normalized.metadata["path"] == "/webhook"
