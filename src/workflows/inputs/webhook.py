"""Webhook input type for processing generic HTTP webhook events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .base import NormalizedInput


@dataclass
class WebhookInput:
    """Represents a generic webhook/HTTP request input."""

    method: str
    path: str
    body: str
    source_ip: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    query_params: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def matches(cls, event: dict[str, Any]) -> bool:
        """Check if event is an API Gateway/webhook event."""
        # Check for API Gateway v2 (HTTP API) format
        if "requestContext" in event and "http" in event.get("requestContext", {}):
            return True
        # Check for API Gateway v1 (REST API) format
        if "httpMethod" in event and "path" in event:
            return True
        # Check for direct webhook format
        return "method" in event and "body" in event

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> WebhookInput:
        """Parse an event into WebhookInput."""
        # Handle API Gateway v2 (HTTP API) format
        if "requestContext" in event and "http" in event.get("requestContext", {}):
            http_context = event["requestContext"]["http"]
            return cls(
                method=http_context.get("method", ""),
                path=http_context.get("path", ""),
                body=event.get("body", ""),
                source_ip=http_context.get("sourceIp", ""),
                headers=event.get("headers", {}),
                query_params=event.get("queryStringParameters", {}) or {},
                timestamp=datetime.now(UTC),
                raw=event,
            )

        # Handle API Gateway v1 (REST API) format
        if "httpMethod" in event:
            request_context = event.get("requestContext", {})
            identity = request_context.get("identity", {})
            return cls(
                method=event.get("httpMethod", ""),
                path=event.get("path", ""),
                body=event.get("body", ""),
                source_ip=identity.get("sourceIp", ""),
                headers=event.get("headers", {}),
                query_params=event.get("queryStringParameters", {}) or {},
                timestamp=datetime.now(UTC),
                raw=event,
            )

        # Handle direct webhook format
        timestamp = event.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        elif timestamp is None:
            timestamp = datetime.now(UTC)

        return cls(
            method=event.get("method", "GET"),
            path=event.get("path", "/"),
            body=event.get("body", ""),
            source_ip=event.get("source_ip", ""),
            headers=event.get("headers", {}),
            query_params=event.get("query_params", {}),
            timestamp=timestamp,
            raw=event,
        )

    def to_normalized(self) -> NormalizedInput:
        """Convert to normalized input format."""
        return NormalizedInput(
            input_type="webhook",
            source=self.source_ip,
            content=self.body,
            metadata={
                "method": self.method,
                "path": self.path,
                "headers": self.headers,
                "query_params": self.query_params,
            },
            timestamp=self.timestamp,
            raw=self.raw,
        )
