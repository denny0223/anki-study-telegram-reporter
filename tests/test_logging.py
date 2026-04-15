from anki_study_telegram_reporter.logging import redact


def test_redact_replaces_known_secrets() -> None:
    assert redact("token abc123 failed", ["abc123"]) == "token [REDACTED] failed"


def test_redact_ignores_short_values() -> None:
    assert redact("id 123 failed", ["123"]) == "id 123 failed"
