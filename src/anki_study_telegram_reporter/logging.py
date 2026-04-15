"""Small logging helpers for command output."""

from __future__ import annotations


def redact(text: str, secrets: list[str | None]) -> str:
    redacted = text
    for secret in secrets:
        if secret and len(secret) >= 4:
            redacted = redacted.replace(secret, "[REDACTED]")
    return redacted
