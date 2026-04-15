"""Render study metrics into Telegram-ready text."""

from __future__ import annotations

from datetime import date
from math import ceil

from .copy_bank import CLOSERS, FRICTION_LINES, HEADLINES, PUSH_LINES
from .metrics import StudyMetrics


def render_report(
    metrics: StudyMetrics,
    *,
    vocabulary_target_count: int = 1600,
    exam_date: date = date(2026, 5, 17),
    report_slot: str = "auto",
) -> str:
    band = metrics.performance_band
    slot = _resolve_slot(report_slot, metrics)
    days_left = max((exam_date - metrics.report_date).days, 0)
    started = min(metrics.started_card_count, vocabulary_target_count)
    remaining_words = max(vocabulary_target_count - started, 0)
    required_new_per_day = _required_per_day(remaining_words, days_left)
    progress_percent = round(started / vocabulary_target_count * 100) if vocabulary_target_count else 0
    seed = _seed(metrics, slot)
    today_push_line = _today_push_line(metrics.new_count, required_new_per_day, seed)
    headline = _pick_line(HEADLINES[band][slot], seed)

    goal_line = "已達標" if metrics.goal_met else f"未達標，還差 {metrics.daily_goal_reviews - metrics.review_count} 題"
    success_percent = round(metrics.success_rate * 100)
    friction_line = _friction_line(metrics.again_count, metrics.review_count, seed)
    closer = _pick_line(CLOSERS[slot], seed + metrics.review_count)

    return "\n".join(
        [
            f"會考單字戰報 {metrics.report_date.isoformat()}",
            headline,
            "",
            f"距離 2026-05-17 國中會考：倒數 {days_left} 天",
            f"1600 單字進度：已開始 {started} 個（{progress_percent}%），剩 {remaining_words} 個",
            f"建議節奏：每天至少新增 {required_new_per_day} 個單字",
            today_push_line,
            "",
            f"今天碰過：{metrics.distinct_card_count} 個單字，總共作答 {metrics.review_count} 次（{goal_line}）",
            f"今天新開：{metrics.new_count} 個；複習：{metrics.review_card_count} 個；卡回學習區：{metrics.relearn_count} 個",
            f"順手度：{success_percent}%；卡住重來：{metrics.again_count} 次",
            friction_line,
            closer,
        ]
    )


def _today_push_line(new_count: int, required_new_per_day: int, seed: int) -> str:
    if required_new_per_day == 0:
        return _pick_line(PUSH_LINES["done"], seed)
    if new_count == 0:
        return _pick_line(PUSH_LINES["zero"], seed).format(required=required_new_per_day)
    if new_count >= required_new_per_day:
        surplus = new_count - required_new_per_day
        return _pick_line(PUSH_LINES["ahead"], seed).format(new=new_count, delta=surplus)
    return _pick_line(PUSH_LINES["behind"], seed).format(new=new_count, delta=required_new_per_day - new_count)


def _friction_line(again_count: int, review_count: int, seed: int) -> str:
    if review_count == 0:
        return _pick_line(FRICTION_LINES["zero"], seed)
    again_rate = again_count / review_count
    if again_rate >= 0.4:
        return _pick_line(FRICTION_LINES["high"], seed)
    if again_rate >= 0.2:
        return _pick_line(FRICTION_LINES["medium"], seed)
    return _pick_line(FRICTION_LINES["low"], seed)


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
