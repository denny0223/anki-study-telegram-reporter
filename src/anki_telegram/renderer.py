"""Render study metrics into Telegram-ready text."""

from __future__ import annotations

from datetime import date
from math import ceil

from .copy_bank import HEADLINES
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
    progress_percent = round(started / vocabulary_target_count * 100) if vocabulary_target_count else 0
    seed = _seed(metrics, slot)
    today_push_line = _short_push_line(metrics.new_count, required_new_per_day)
    headline = _pick_line(HEADLINES[band][slot], seed)
    supervisor_line = _supervisor_line(supervisor_usernames, seed)
    friction_line = _short_friction_line(metrics.again_count, metrics.review_count)
    review_line = _review_line(metrics)

    return "\n".join(
        [
            f"會考倒數 {days_left} 天｜單字 {started}/{vocabulary_target_count}（{progress_percent}%）",
            headline,
            f"{today_push_line}；{review_line}",
            friction_line,
            supervisor_line,
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


def _short_push_line(new_count: int, required_new_per_day: int) -> str:
    if required_new_per_day == 0:
        return "新字清完，今天主線是複習"
    if new_count >= required_new_per_day:
        return f"新字 {new_count}，超前 {new_count - required_new_per_day}"
    return f"新字 {new_count}，還差 {required_new_per_day - new_count}"


def _review_line(metrics: StudyMetrics) -> str:
    if metrics.review_count == 0:
        return "還沒開刷"
    if metrics.goal_met:
        return f"作答 {metrics.review_count} 次，已達標"
    return f"作答 {metrics.review_count} 次，差 {metrics.daily_goal_reviews - metrics.review_count}"


def _short_friction_line(again_count: int, review_count: int) -> str:
    if review_count == 0:
        return "狀態：今日尚未開張，請大家幫會考小專案敲一下門。"
    again_rate = again_count / review_count
    if again_rate >= 0.4:
        return f"卡關 {again_count} 次：不是壞掉，是弱點自己舉手報名。"
    if again_rate >= 0.2:
        return f"卡關 {again_count} 次：有幾個單字需要再被溫柔盯一下。"
    return f"卡關 {again_count} 次：今天手感可以，請繼續保持出勤。"


def _supervisor_line(supervisor_usernames: tuple[str, ...], seed: int) -> str:
    if not supervisor_usernames:
        return "群組監工請就位：看到偷懶可以溫柔但堅定地提醒。"
    tag_text = " ".join(supervisor_usernames)
    nudges = [
        "SITCON 監督小隊請就位，看到進度卡住可以溫柔提醒",
        "請大家幫忙做進度 review，不讓單字債偷偷長大",
        "麻煩各位路過補一點社群壓力，讓會考小專案保持活躍",
        "必要時請發一個友善 reminder，台灣社群精神靠大家",
        "讓會考倒數不要變成無人認領的坑",
        "請大家幫忙敲碗，單字不會自己走進腦袋",
        "請籌備團隊發揮社群精神，一起守護這個會考任務",
        "看到他失蹤可以 ping 一下，這是善意的社群關懷",
    ]
    return f"請協助盯 {tag_text}：{_pick_line(nudges, seed)}。"


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
