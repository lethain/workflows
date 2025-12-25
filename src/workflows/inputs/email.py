"""Email input type for processing email events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .base import NormalizedInput


@dataclass
class EmailInput:
    """Represents an email input from SES or similar services."""

    sender: str
    recipient: str
    subject: str
    body: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    headers: dict[str, str] = field(default_factory=dict)
    attachments: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def matches(cls, event: dict[str, Any]) -> bool:
        """Check if event is an email event (SES format)."""
        # Check for SES event structure
        if "Records" in event:
            records = event.get("Records", [])
            if records and records[0].get("eventSource") == "aws:ses":
                return True
        # Check for direct email format
        return all(k in event for k in ("sender", "recipient", "body"))

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> EmailInput:
        """Parse an event into EmailInput."""
        # Handle SES event format
        if "Records" in event:
            record = event["Records"][0]
            ses = record.get("ses", {})
            mail = ses.get("mail", {})
            common_headers = mail.get("commonHeaders", {})

            return cls(
                sender=common_headers.get("from", [""])[0] if common_headers.get("from") else "",
                recipient=common_headers.get("to", [""])[0] if common_headers.get("to") else "",
                subject=common_headers.get("subject", ""),
                body="",  # Body would need to be fetched from S3 in real implementation
                timestamp=datetime.fromisoformat(
                    mail.get("timestamp", datetime.now(UTC).isoformat()).replace("Z", "+00:00")
                ),
                headers=dict(mail.get("headers", [])),
                raw=event,
            )

        # Handle direct email format
        timestamp = event.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        elif timestamp is None:
            timestamp = datetime.now(UTC)

        return cls(
            sender=event.get("sender", ""),
            recipient=event.get("recipient", ""),
            subject=event.get("subject", ""),
            body=event.get("body", ""),
            timestamp=timestamp,
            headers=event.get("headers", {}),
            attachments=event.get("attachments", []),
            raw=event,
        )

    def to_normalized(self) -> NormalizedInput:
        """Convert to normalized input format."""
        return NormalizedInput(
            input_type="email",
            source=self.sender,
            content=self.body,
            metadata={
                "recipient": self.recipient,
                "subject": self.subject,
                "headers": self.headers,
                "attachments": self.attachments,
            },
            timestamp=self.timestamp,
            raw=self.raw,
        )
