from datetime import date

from anki_study_telegram_reporter.metrics import StudyComparison, StudyMetrics
from anki_study_telegram_reporter.renderer import render_report


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
    assert "倒數" in report
    assert "🔴" in report
    assert "還沒刷題" in report


def test_render_low_band() -> None:
    report = render_report(_metrics(20), report_slot="morning")
    assert "已收錄 420 / 1600 字" in report
    assert "新收 1 字，差 36 跟上節奏" in report
    assert "🟡" in report


def test_render_met_band() -> None:
    report = render_report(_metrics(100), report_slot="evening")
    assert "✅" in report
    assert "🟢" in report


def test_render_strong_band() -> None:
    report = render_report(_metrics(220), report_slot="evening")
    assert "刷 220 題" in report
    assert "🟢" in report


def test_render_zero_again() -> None:
    m = StudyMetrics(
        report_date=date(2026, 4, 15),
        review_count=100,
        distinct_card_count=50,
        new_count=10,
        learning_count=5,
        review_card_count=35,
        relearn_count=0,
        total_card_count=1600,
        started_card_count=420,
        again_count=0,
        hard_count=10,
        good_count=80,
        easy_count=10,
        daily_goal_reviews=100,
    )
    report = render_report(m, report_slot="evening")
    assert "零失誤" in report


def test_render_has_progress_bar() -> None:
    report = render_report(_metrics(100), report_slot="morning")
    assert "▓" in report
    assert "░" in report
    assert "26%" in report


def test_report_slot_changes_copy_for_same_metrics() -> None:
    metrics = _metrics(220)

    morning = render_report(metrics, report_slot="morning")
    evening = render_report(metrics, report_slot="evening")

    assert morning != evening


def test_supervisor_usernames_are_tagged() -> None:
    report = render_report(_metrics(20), supervisor_usernames=("@alice", "@bob"))

    assert "請幫盯 @alice @bob" in report


def test_comparison_feedback_is_rendered_when_available() -> None:
    metrics = StudyMetrics(
        report_date=date(2026, 4, 15),
        review_count=70,
        distinct_card_count=40,
        new_count=8,
        learning_count=2,
        review_card_count=30,
        relearn_count=0,
        total_card_count=1600,
        started_card_count=420,
        again_count=3,
        hard_count=10,
        good_count=50,
        easy_count=7,
        daily_goal_reviews=100,
        comparison=StudyComparison(
            review_count=30,
            new_count=5,
            started_card_count=5,
            again_count=1,
        ),
    )

    report = render_report(metrics, supervisor_usernames=("@alice",))

    assert "比上次 +30 題" in report
    assert "新字 +5" in report
    assert "錯題 +1" in report
    assert "還差 30 題達標" in report
    assert "請幫盯 @alice" in report


def test_comparison_feedback_handles_idle_delta() -> None:
    metrics = _metrics(20)
    metrics = StudyMetrics(
        **{**metrics.__dict__, "comparison": StudyComparison(
            review_count=0,
            new_count=0,
            started_card_count=0,
            again_count=0,
        )}
    )

    report = render_report(metrics)

    assert "比上次 +0" not in report
    assert "比上次沒有新增紀錄" in report
    assert any(text in report for text in ("timeline", "0 題", "講者", "issue"))


def test_comparison_feedback_calls_out_noisy_delta() -> None:
    metrics = _metrics(140)
    metrics = StudyMetrics(
        **{**metrics.__dict__, "comparison": StudyComparison(
            review_count=20,
            new_count=2,
            started_card_count=2,
            again_count=9,
        )}
    )

    report = render_report(metrics)

    assert "比上次 +20 題" in report
    assert "錯題 +9" in report
    assert any(text in report for text in ("錯題偏吵", "fail case", "Wi-Fi", "紅燈"))


def test_comparison_feedback_calls_out_clean_delta() -> None:
    metrics = _metrics(140)
    metrics = StudyMetrics(
        **{**metrics.__dict__, "comparison": StudyComparison(
            review_count=20,
            new_count=2,
            started_card_count=2,
            again_count=0,
        )}
    )

    report = render_report(metrics)

    assert "比上次 +20 題" in report
    assert "錯題 +" not in report
    assert any(text in report for text in ("零失誤", "CI", "lightning talk", "stable"))


def test_report_is_short_enough_for_group_chat() -> None:
    report = render_report(_metrics(220), supervisor_usernames=("@alice",))

    assert len(report.splitlines()) == 5
    assert len(report) < 300


def test_report_with_comparison_is_short_enough_for_group_chat() -> None:
    metrics = _metrics(220)
    metrics = StudyMetrics(
        **{**metrics.__dict__, "comparison": StudyComparison(
            review_count=80,
            new_count=12,
            started_card_count=12,
            again_count=4,
        )}
    )

    report = render_report(metrics, supervisor_usernames=("@alice",))

    assert len(report.splitlines()) == 5
    assert len(report) < 300
