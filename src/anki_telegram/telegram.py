"""Telegram Bot API delivery."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TelegramError(RuntimeError):
    """Raised when Telegram delivery fails."""


class HttpPost(Protocol):
    def __call__(self, url: str, payload: dict[str, object]) -> dict[str, object]:
        ...


@dataclass(frozen=True)
class TelegramClient:
    bot_token: str
    chat_id: str
    thread_id: str | None = None
    http_post: HttpPost | None = None

    def send_message(self, text: str) -> None:
        payload: dict[str, object] = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        if self.thread_id:
            payload["message_thread_id"] = self.thread_id

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        response = (self.http_post or _post_json)(url, payload)

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
        raise TelegramError(f"Telegram HTTP {exc.code}: {details}") from exc
    except URLError as exc:
        raise TelegramError(f"Telegram request failed: {exc.reason}") from exc

    try:
        parsed = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise TelegramError("Telegram returned invalid JSON.") from exc

    if not isinstance(parsed, dict):
        raise TelegramError("Telegram returned an unexpected response.")
    return parsed
