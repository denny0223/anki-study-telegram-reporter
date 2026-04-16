"""Study metric structures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class StudyComparison:
    review_count: int
    new_count: int
    started_card_count: int
    again_count: int


@dataclass(frozen=True)
class StudyMetrics:
    report_date: date
    review_count: int
    distinct_card_count: int
    new_count: int
    learning_count: int
    review_card_count: int
    relearn_count: int
    total_card_count: int
    started_card_count: int
    again_count: int
    hard_count: int
    good_count: int
    easy_count: int
    daily_goal_reviews: int
    comparison: StudyComparison | None = None

    @property
    def goal_met(self) -> bool:
        return self.review_count >= self.daily_goal_reviews

    @property
    def performance_band(self) -> str:
        if self.review_count == 0:
            return "zero"
        if self.review_count < self.daily_goal_reviews:
            return "low"
        if self.review_count >= self.daily_goal_reviews * 2:
            return "strong"
        return "met"
