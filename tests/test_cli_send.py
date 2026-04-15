from anki_telegram import cli


class FakeTelegramClient:
    messages: list[str] = []

    def __init__(self, *, bot_token: str, chat_id: str, thread_id: str | None = None) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.thread_id = thread_id

    def send_message(self, text: str) -> None:
        self.messages.append(text)


def test_report_send_uses_telegram_client(tmp_path, monkeypatch, capsys) -> None:
    FakeTelegramClient.messages = []
    monkeypatch.setattr(cli, "TelegramClient", FakeTelegramClient)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    result = cli.main(
        [
            "report",
            "--source",
            "mock",
            "--date",
            "2026-04-15",
            "--send",
        ]
    )

    assert result == 2
    assert FakeTelegramClient.messages == []
    assert "TELEGRAM_BOT_TOKEN" in capsys.readouterr().err


def test_report_send_succeeds_with_env(monkeypatch, capsys) -> None:
    FakeTelegramClient.messages = []
    monkeypatch.setattr(cli, "TelegramClient", FakeTelegramClient)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100123")

    result = cli.main(
        [
            "report",
            "--source",
            "mock",
            "--date",
            "2026-04-15",
            "--send",
        ]
    )

    assert result == 0
    assert len(FakeTelegramClient.messages) == 1
    assert "會考倒數 32 天" in FakeTelegramClient.messages[0]
    assert "Telegram report sent." in capsys.readouterr().out
