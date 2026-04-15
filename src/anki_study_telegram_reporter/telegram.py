"""Telegram Bot API delivery."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .retry import retry


class TelegramError(RuntimeError):
    """Raised when Telegram delivery fails."""


class HttpPost(Protocol):
    def __call__(self, url: str, payload: dict[str, object]) -> dict[str, object]:
        ...


class TelegramHttpError(TelegramError):
    """Raised when Telegram returns a retryable HTTP status."""

    def __init__(self, status_code: int, details: str) -> None:
        super().__init__(f"Telegram HTTP {status_code}: {details}")
        self.status_code = status_code


class TelegramTransportError(TelegramError):
    """Raised when Telegram cannot be reached."""


@dataclass(frozen=True)
class TelegramClient:
    bot_token: str
    chat_id: str
    thread_id: str | None = None
    http_post: HttpPost | None = None
    sleeper: Callable[[float], None] | None = None

    def send_message(self, text: str) -> None:
        payload: dict[str, object] = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        if self.thread_id:
            payload["message_thread_id"] = self.thread_id

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        post = self.http_post or _post_json
        response = retry(
            lambda: post(url, payload),
            sleeper=self.sleeper or _sleep,
            retryable=_is_retryable_telegram_error,
        )

        if response.get("ok") is not True:
            description = response.get("description") or "Telegram API returned ok=false."
            raise TelegramError(str(description))


def _post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise TelegramHttpError(exc.code, details) from exc
    except URLError as exc:
        raise TelegramTransportError(f"Telegram request failed: {exc.reason}") from exc

    try:
        parsed = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise TelegramError("Telegram returned invalid JSON.") from exc

    if not isinstance(parsed, dict):
        raise TelegramError("Telegram returned an unexpected response.")
    return parsed


def _is_retryable_telegram_error(exc: Exception) -> bool:
    if isinstance(exc, TelegramTransportError):
        return True
    if isinstance(exc, TelegramHttpError):
        return exc.status_code == 429 or exc.status_code >= 500
    return False


def _sleep(seconds: float) -> None:
    import time

    time.sleep(seconds)
