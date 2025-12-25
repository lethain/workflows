"""Slack input type for processing Slack events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .base import NormalizedInput


@dataclass
class SlackInput:
    """Represents a Slack message or event."""

    user_id: str
    channel_id: str
    text: str
    team_id: str = ""
    thread_ts: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = "message"
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def matches(cls, event: dict[str, Any]) -> bool:
        """Check if event is a Slack event."""
        # Check for Slack event API format
        if event.get("type") == "url_verification":
            return True
        if "event" in event and event.get("api_app_id"):
            return True
        # Check for direct Slack message format
        return all(k in event for k in ("user_id", "channel_id", "text"))

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> SlackInput:
        """Parse an event into SlackInput."""
        # Handle Slack Event API format
        if "event" in event:
            slack_event = event["event"]
            ts = slack_event.get("ts", "")
            timestamp = datetime.fromtimestamp(float(ts), tz=UTC) if ts else datetime.now(UTC)

            return cls(
                user_id=slack_event.get("user", ""),
                channel_id=slack_event.get("channel", ""),
                text=slack_event.get("text", ""),
                team_id=event.get("team_id", ""),
                thread_ts=slack_event.get("thread_ts"),
                timestamp=timestamp,
                event_type=slack_event.get("type", "message"),
                raw=event,
            )

        # Handle direct format
        timestamp = event.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        elif isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp, tz=UTC)
        elif timestamp is None:
            timestamp = datetime.now(UTC)

        return cls(
            user_id=event.get("user_id", ""),
            channel_id=event.get("channel_id", ""),
            text=event.get("text", ""),
            team_id=event.get("team_id", ""),
            thread_ts=event.get("thread_ts"),
            timestamp=timestamp,
            event_type=event.get("event_type", "message"),
            raw=event,
        )

    def to_normalized(self) -> NormalizedInput:
        """Convert to normalized input format."""
        return NormalizedInput(
            input_type="slack",
            source=self.user_id,
            content=self.text,
            metadata={
                "channel_id": self.channel_id,
                "team_id": self.team_id,
                "thread_ts": self.thread_ts,
                "event_type": self.event_type,
            },
            timestamp=self.timestamp,
            raw=self.raw,
        )
