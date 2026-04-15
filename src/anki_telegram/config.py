"""Application configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import os


SUPPORTED_SOURCES = {"mock", "ankiweb"}
SUPPORTED_REPORT_SLOTS = {"auto", "morning", "evening"}


class ConfigError(ValueError):
    """Raised when configuration is missing or invalid."""


@dataclass(frozen=True)
class AppConfig:
    source: str
    dry_run: bool
    report_date: date
    timezone: ZoneInfo
    daily_goal_reviews: int
    vocabulary_target_count: int
    exam_date: date
    report_slot: str
    target_decks: tuple[str, ...]
    excluded_decks: tuple[str, ...]
    anki_username: str | None
    anki_password: str | None
    anki_collection_output_dir: Path | None
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    telegram_thread_id: str | None


def load_dotenv(path: Path = Path(".env")) -> dict[str, str]:
    """Load simple KEY=VALUE pairs from a dotenv file.

    This parser intentionally supports only the project needs. Existing
    environment variables win over `.env` values.
    """

    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value

    return values


def build_config(
    *,
    source: str | None,
    dry_run: bool | None,
    send: bool,
    report_date: date | None,
    env: dict[str, str] | None = None,
    dotenv: dict[str, str] | None = None,
) -> AppConfig:
    merged = _merged_env(env=env, dotenv=dotenv)

    selected_source = source or merged.get("SOURCE") or "mock"
    if selected_source not in SUPPORTED_SOURCES:
        raise ConfigError(
            f"Unsupported source '{selected_source}'. Expected one of: {', '.join(sorted(SUPPORTED_SOURCES))}."
        )

    selected_dry_run = _resolve_dry_run(dry_run=dry_run, send=send, env_value=merged.get("DRY_RUN"))

    timezone_name = merged.get("TIMEZONE", "Asia/Taipei")
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ConfigError(f"Unknown timezone '{timezone_name}'.") from exc

    daily_goal = _parse_positive_int(merged.get("DAILY_GOAL_REVIEWS", "100"), "DAILY_GOAL_REVIEWS")
    vocabulary_target = _parse_positive_int(
        merged.get("VOCABULARY_TARGET_COUNT", "1600"), "VOCABULARY_TARGET_COUNT"
    )
    exam_date = _parse_date(merged.get("EXAM_DATE", "2026-05-17"), "EXAM_DATE")
    report_slot = merged.get("REPORT_SLOT", "auto")
    if report_slot not in SUPPORTED_REPORT_SLOTS:
        raise ConfigError(
            f"Unsupported REPORT_SLOT '{report_slot}'. Expected one of: {', '.join(sorted(SUPPORTED_REPORT_SLOTS))}."
        )

    config = AppConfig(
        source=selected_source,
        dry_run=selected_dry_run,
        report_date=report_date or date.today(),
        timezone=timezone,
        daily_goal_reviews=daily_goal,
        vocabulary_target_count=vocabulary_target,
        exam_date=exam_date,
        report_slot=report_slot,
        target_decks=_parse_csv(merged.get("TARGET_DECKS", "")),
        excluded_decks=_parse_csv(merged.get("EXCLUDED_DECKS", "")),
        anki_username=_blank_to_none(merged.get("ANKI_USERNAME")),
        anki_password=_blank_to_none(merged.get("ANKI_PASSWORD")),
        anki_collection_output_dir=_parse_optional_path(merged.get("ANKI_COLLECTION_OUTPUT_DIR")),
        telegram_bot_token=_blank_to_none(merged.get("TELEGRAM_BOT_TOKEN")),
        telegram_chat_id=_blank_to_none(merged.get("TELEGRAM_CHAT_ID")),
        telegram_thread_id=_blank_to_none(merged.get("TELEGRAM_THREAD_ID")),
    )
    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    missing: list[str] = []

    if config.source == "ankiweb":
        if not config.anki_username:
            missing.append("ANKI_USERNAME")
        if not config.anki_password:
            missing.append("ANKI_PASSWORD")

    if not config.dry_run:
        if not config.telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not config.telegram_chat_id:
            missing.append("TELEGRAM_CHAT_ID")

    if missing:
        raise ConfigError("Missing required configuration: " + ", ".join(missing))


def _merged_env(env: dict[str, str] | None, dotenv: dict[str, str] | None) -> dict[str, str]:
    base = dict(dotenv if dotenv is not None else load_dotenv())
    base.update(env if env is not None else os.environ)
    return base


def _resolve_dry_run(*, dry_run: bool | None, send: bool, env_value: str | None) -> bool:
    if dry_run and send:
        raise ConfigError("Choose either --dry-run or --send, not both.")
    if send:
        return False
    if dry_run is not None:
        return dry_run
    if env_value is None:
        return True
    return _parse_bool(env_value)


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"Invalid boolean value '{value}'.")


def _parse_positive_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer.") from exc
    if parsed <= 0:
        raise ConfigError(f"{name} must be greater than zero.")
    return parsed


def _parse_date(value: str, name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a date in YYYY-MM-DD format.") from exc


def _parse_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _blank_to_none(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    return value


def _parse_optional_path(value: str | None) -> Path | None:
    value = _blank_to_none(value)
    if value is None:
        return None
    return Path(value).expanduser()
