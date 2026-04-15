"""Study data sources."""

from __future__ import annotations

from dataclasses import replace
from contextlib import nullcontext
from tempfile import TemporaryDirectory
from pathlib import Path

from .ankiweb import fetch_collection_to_path
from .collection import extract_daily_metrics
from .config import AppConfig
from .metrics import StudyMetrics


class SourceError(RuntimeError):
    """Raised when a study source cannot provide data."""


def load_metrics(config: AppConfig) -> StudyMetrics:
    if config.source == "mock":
        return mock_metrics(config)
    if config.source == "ankiweb":
        return ankiweb_metrics(config)
    raise SourceError(f"Unsupported source: {config.source}")


def mock_metrics(config: AppConfig) -> StudyMetrics:
    base = StudyMetrics(
        report_date=config.report_date,
        review_count=132,
        new_count=18,
        learning_count=24,
        review_card_count=90,
        again_count=9,
        hard_count=16,
        good_count=82,
        easy_count=25,
        daily_goal_reviews=config.daily_goal_reviews,
    )

    return replace(base, daily_goal_reviews=config.daily_goal_reviews)


def ankiweb_metrics(config: AppConfig) -> StudyMetrics:
    try:
        workspace_context = (
            nullcontext(config.anki_collection_output_dir)
            if config.anki_collection_output_dir is not None
            else TemporaryDirectory(prefix="anki-telegram-")
        )
        with workspace_context as workspace:
            collection_path = fetch_collection_to_path(config=config, workspace=Path(workspace))
            return extract_daily_metrics(
                collection_path=collection_path,
                report_date=config.report_date,
                timezone_name=config.timezone,
                daily_goal_reviews=config.daily_goal_reviews,
                target_decks=config.target_decks,
                excluded_decks=config.excluded_decks,
            )
    except Exception as exc:
        if isinstance(exc, SourceError):
            raise
        raise SourceError(str(exc)) from exc
