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
    assert config.vocabulary_target_count == 1600
    assert config.exam_date == date(2026, 5, 17)
    assert config.report_slot == "auto"
    assert config.supervisor_usernames == ()


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
            "VOCABULARY_TARGET_COUNT": "1200",
            "EXAM_DATE": "2026-05-01",
            "REPORT_SLOT": "evening",
            "SUPERVISOR_USERNAMES": "alice, @bob",
            "TARGET_DECKS": "Japanese, English",
        },
        dotenv={},
    )

    assert config.daily_goal_reviews == 42
    assert config.vocabulary_target_count == 1200
    assert config.exam_date == date(2026, 5, 1)
    assert config.report_slot == "evening"
    assert config.supervisor_usernames == ("@alice", "@bob")
    assert config.target_decks == ("Japanese", "English")


def test_optional_collection_output_dir_is_parsed() -> None:
    config = build_config(
        source="mock",
        dry_run=True,
        send=False,
        report_date=None,
        env={"ANKI_COLLECTION_OUTPUT_DIR": "~/anki-debug"},
        dotenv={},
    )

    assert config.anki_collection_output_dir is not None
    assert str(config.anki_collection_output_dir).endswith("anki-debug")
