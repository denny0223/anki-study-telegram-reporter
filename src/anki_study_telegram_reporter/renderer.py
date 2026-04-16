"""Render study metrics into Telegram-ready text."""

from __future__ import annotations

from datetime import date
from math import ceil

from .copy_bank import COMPARISON_LINES, NUDGES, STATUS_LINES
from .metrics import StudyMetrics


def render_report(
    metrics: StudyMetrics,
    *,
    vocabulary_target_count: int = 1600,
    exam_date: date = date(2026, 5, 17),
    report_slot: str = "auto",
    supervisor_usernames: tuple[str, ...] = (),
) -> str:
    band = metrics.performance_band
    slot = _resolve_slot(report_slot, metrics)
    days_left = max((exam_date - metrics.report_date).days, 0)
    started = min(metrics.started_card_count, vocabulary_target_count)
    remaining_words = max(vocabulary_target_count - started, 0)
    required_new_per_day = _required_per_day(remaining_words, days_left)
    progress_pct = round(started / vocabulary_target_count * 100) if vocabulary_target_count else 0
    seed = _seed(metrics, slot)

    bar = _progress_bar(started, vocabulary_target_count)
    header = f"📊 會考單字日報｜倒數 {days_left} 天"
    progress = f"[{bar}] {progress_pct}%｜已收錄 {started} / {vocabulary_target_count} 字"
    activity = f"🎯 {_activity_line(metrics, required_new_per_day)}"
    status = _status_line(metrics, band, slot, seed)
    supervisor = _supervisor_line(metrics, supervisor_usernames, band, seed)

    return "\n".join([header, progress, activity, status, supervisor])


def _progress_bar(current: int, total: int) -> str:
    if total <= 0:
        return "░" * 10
    ratio = min(current / total, 1.0)
    filled = round(ratio * 10)
    return "▓" * filled + "░" * (10 - filled)


def _activity_line(metrics: StudyMetrics, required_new_per_day: int) -> str:
    review_part = _review_part(metrics)
    new_part = _new_word_part(metrics.new_count, required_new_per_day)
    return f"{review_part}｜{new_part}"


def _review_part(metrics: StudyMetrics) -> str:
    if metrics.review_count == 0:
        return "今天還沒刷題"
    if metrics.goal_met:
        return f"今天刷 {metrics.review_count} 題 ✅"
    gap = metrics.daily_goal_reviews - metrics.review_count
    return f"今天刷 {metrics.review_count} 題，差 {gap} 達標"


def _new_word_part(new_count: int, required_new_per_day: int) -> str:
    if required_new_per_day == 0:
        return "新字已全數收錄 ✅"
    if new_count == 0:
        return f"新字還沒開，每天要收 {required_new_per_day} 字"
    if new_count >= required_new_per_day:
        return f"新收 {new_count} 字 ✅"
    gap = required_new_per_day - new_count
    return f"新收 {new_count} 字，差 {gap} 跟上節奏"


def _status_line(metrics: StudyMetrics, band: str, slot: str, seed: int) -> str:
    comment = _pick_line(STATUS_LINES[band][slot], seed)
    if band == "zero":
        return f"🔴 {comment}"
    emoji = {"low": "🟡", "met": "🟢", "strong": "🟢"}[band]
    if metrics.again_count == 0:
        return f"{emoji} 零失誤，{comment}"
    pct = round(metrics.again_count / metrics.review_count * 100)
    return f"{emoji} 答錯 {metrics.again_count} 題（{pct}%），{comment}"


def _supervisor_line(metrics: StudyMetrics, supervisor_usernames: tuple[str, ...], band: str, seed: int) -> str:
    nudge_key = "behind" if band in {"zero", "low"} else "on_track"
    nudge = _pick_line(NUDGES[nudge_key], seed)
    comparison = _comparison_feedback(metrics)
    if not supervisor_usernames:
        if comparison:
            return f"🫵 {comparison}；{nudge}。"
        return f"🫵 群組監工請就位：{nudge}。"
    tag_text = " ".join(supervisor_usernames)
    if comparison:
        return f"🫵 {comparison}；請幫盯 {tag_text}：{nudge}。"
    return f"🫵 請幫盯 {tag_text}：{nudge}。"


def _comparison_feedback(metrics: StudyMetrics) -> str:
    comparison = metrics.comparison
    if comparison is None:
        return ""
    if comparison.review_count == 0:
        return _pick_line(COMPARISON_LINES["idle"], _seed(metrics, "comparison"))

    parts = [f"比上次 +{comparison.review_count} 題"]
    if comparison.new_count:
        parts.append(f"新字 +{comparison.new_count}")
    if comparison.started_card_count and comparison.started_card_count != comparison.new_count:
        parts.append(f"收錄 +{comparison.started_card_count}")
    if comparison.again_count:
        parts.append(f"錯題 +{comparison.again_count}")

    feedback = _comparison_comment(metrics)
    if not metrics.goal_met:
        gap = metrics.daily_goal_reviews - metrics.review_count
        feedback = f"{feedback}，還差 {gap} 題達標"
    return "、".join(parts) + f"｜{feedback}"


def _comparison_comment(metrics: StudyMetrics) -> str:
    comparison = metrics.comparison
    if comparison is None:
        return ""

    seed = _seed(metrics, "comparison") + comparison.review_count + comparison.new_count * 7
    if comparison.again_count == 0:
        return _pick_line(COMPARISON_LINES["clean"], seed)

    comparison_again_rate = comparison.again_count / comparison.review_count
    if comparison_again_rate >= 0.35:
        return _pick_line(COMPARISON_LINES["noisy"], seed)

    if comparison.review_count >= metrics.daily_goal_reviews:
        return _pick_line(COMPARISON_LINES["surge"], seed)
    if metrics.goal_met:
        return _pick_line(COMPARISON_LINES["on_track"], seed)
    return _pick_line(COMPARISON_LINES["catchup"], seed)


def _required_per_day(remaining_words: int, days_left: int) -> int:
    if remaining_words <= 0:
        return 0
    return ceil(remaining_words / max(days_left, 1))


def _pick_line(lines: list[str], seed: int) -> str:
    return lines[seed % len(lines)]


def _resolve_slot(report_slot: str, metrics: StudyMetrics) -> str:
    if report_slot in {"morning", "evening"}:
        return report_slot
    return "morning" if metrics.review_count < metrics.daily_goal_reviews else "evening"


def _seed(metrics: StudyMetrics, slot: str) -> int:
    slot_offset = 17 if slot == "evening" else 0
    return (
        metrics.report_date.toordinal()
        + metrics.review_count
        + metrics.new_count * 3
        + metrics.again_count * 5
        + slot_offset
    )
