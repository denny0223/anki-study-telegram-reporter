from datetime import date

from anki_telegram.metrics import StudyMetrics
from anki_telegram.renderer import render_report


def _metrics(review_count: int, goal: int = 100) -> StudyMetrics:
    return StudyMetrics(
        report_date=date(2026, 4, 15),
        review_count=review_count,
        new_count=1,
        learning_count=2,
        review_card_count=3,
        again_count=1 if review_count else 0,
        hard_count=1 if review_count else 0,
        good_count=max(review_count - 2, 0),
        easy_count=0,
        daily_goal_reviews=goal,
    )


def test_render_zero_band() -> None:
    assert "安靜得像圖書館閉館" in render_report(_metrics(0))


def test_render_low_band() -> None:
    assert "暖機區" in render_report(_metrics(20))


def test_render_met_band() -> None:
    assert "達標" in render_report(_metrics(100))


def test_render_strong_band() -> None:
    assert "火力全開" in render_report(_metrics(220))
