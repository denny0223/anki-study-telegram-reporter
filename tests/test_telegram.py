import pytest

from anki_telegram.telegram import TelegramClient, TelegramError


def test_send_message_posts_expected_payload() -> None:
    calls = []

    def fake_post(url: str, payload: dict[str, object]) -> dict[str, object]:
        calls.append((url, payload))
        return {"ok": True}

    client = TelegramClient(
        bot_token="token",
        chat_id="-100123",
        thread_id="456",
        http_post=fake_post,
    )

    client.send_message("hello")

    assert calls == [
        (
            "https://api.telegram.org/bottoken/sendMessage",
            {
                "chat_id": "-100123",
                "text": "hello",
                "disable_web_page_preview": True,
                "message_thread_id": "456",
            },
        )
    ]


def test_send_message_raises_on_ok_false() -> None:
    def fake_post(url: str, payload: dict[str, object]) -> dict[str, object]:
        return {"ok": False, "description": "chat not found"}

    client = TelegramClient(bot_token="token", chat_id="-100123", http_post=fake_post)

    with pytest.raises(TelegramError, match="chat not found"):
        client.send_message("hello")
