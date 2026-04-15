"""Study data sources."""

from __future__ import annotations

from dataclasses import replace

from .config import AppConfig
from .metrics import StudyMetrics


class SourceError(RuntimeError):
    """Raised when a study source cannot provide data."""


def load_metrics(config: AppConfig) -> StudyMetrics:
    if config.source == "mock":
        return mock_metrics(config)
    if config.source == "ankiweb":
        raise SourceError("AnkiWeb source is not implemented yet. Use --source mock for the current phase.")
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
