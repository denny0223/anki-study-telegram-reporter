from datetime import date

import pytest

from anki_telegram.config import ConfigError, build_config


def test_mock_dry_run_does_not_require_secrets() -> None:
    config = build_config(
        source="mock",
        dry_run=True,
        send=False,
        report_date=date(2026, 4, 15),
        env={},
        dotenv={},
    )

    assert config.source == "mock"
    assert config.dry_run is True
    assert config.report_date == date(2026, 4, 15)


def test_send_requires_telegram_secrets() -> None:
    with pytest.raises(ConfigError, match="TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID"):
        build_config(source="mock", dry_run=None, send=True, report_date=None, env={}, dotenv={})


def test_ankiweb_requires_anki_credentials() -> None:
    with pytest.raises(ConfigError, match="ANKI_USERNAME, ANKI_PASSWORD"):
        build_config(source="ankiweb", dry_run=True, send=False, report_date=None, env={}, dotenv={})


def test_env_values_are_used() -> None:
    config = build_config(
        source=None,
        dry_run=None,
        send=False,
        report_date=None,
        env={
            "SOURCE": "mock",
            "DRY_RUN": "true",
            "DAILY_GOAL_REVIEWS": "42",
            "TARGET_DECKS": "Japanese, English",
        },
        dotenv={},
    )

    assert config.daily_goal_reviews == 42
    assert config.target_decks == ("Japanese", "English")
