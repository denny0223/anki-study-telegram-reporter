from datetime import date

from anki_telegram.metrics import StudyMetrics
from anki_telegram.renderer import render_report


def _metrics(review_count: int, goal: int = 100) -> StudyMetrics:
    return StudyMetrics(
        report_date=date(2026, 4, 15),
        review_count=review_count,
        distinct_card_count=max(review_count // 2, 0),
        new_count=1,
        learning_count=2,
        review_card_count=3,
        relearn_count=4,
        total_card_count=1600,
        started_card_count=420,
        again_count=1 if review_count else 0,
        hard_count=1 if review_count else 0,
        good_count=max(review_count - 2, 0),
        easy_count=0,
        daily_goal_reviews=goal,
    )


def test_render_zero_band() -> None:
    report = render_report(_metrics(0), report_slot="morning")
    assert "會考單字戰報" in report
    assert "狀態：" in report


def test_render_low_band() -> None:
    report = render_report(_metrics(20), report_slot="morning")
    assert "1600 單字進度：已開始 420 個（26%），剩 1180 個" in report
    assert "建議節奏：每天至少新增 37 個單字" in report


def test_render_met_band() -> None:
    assert "已達標" in render_report(_metrics(100), report_slot="evening")


def test_render_strong_band() -> None:
    assert "總共作答 220 次" in render_report(_metrics(220), report_slot="evening")


def test_report_slot_changes_copy_for_same_metrics() -> None:
    metrics = _metrics(220)

    morning = render_report(metrics, report_slot="morning")
    evening = render_report(metrics, report_slot="evening")

    assert morning != evening
