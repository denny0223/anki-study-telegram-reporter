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
    assert "會考倒數" in report
    assert "狀態：" in report


def test_render_low_band() -> None:
    report = render_report(_metrics(20), report_slot="morning")
    assert "單字 420/1600（26%）" in report
    assert "新字 1，還差 36" in report


def test_render_met_band() -> None:
    assert "已達標" in render_report(_metrics(100), report_slot="evening")


def test_render_strong_band() -> None:
    assert "作答 220 次" in render_report(_metrics(220), report_slot="evening")


def test_report_slot_changes_copy_for_same_metrics() -> None:
    metrics = _metrics(220)

    morning = render_report(metrics, report_slot="morning")
    evening = render_report(metrics, report_slot="evening")

    assert morning != evening


def test_supervisor_usernames_are_tagged() -> None:
    report = render_report(_metrics(20), supervisor_usernames=("@alice", "@bob"))

    assert "請協助盯 @alice @bob" in report


def test_report_is_short_enough_for_group_chat() -> None:
    report = render_report(_metrics(220), supervisor_usernames=("@alice",))

    assert len(report.splitlines()) == 5
    assert len(report) < 260
