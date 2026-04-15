"""Render study metrics into Telegram-ready text."""

from __future__ import annotations

from datetime import date
from math import ceil

from .metrics import StudyMetrics


def render_report(
    metrics: StudyMetrics,
    *,
    vocabulary_target_count: int = 1600,
    exam_date: date = date(2026, 5, 17),
) -> str:
    band = metrics.performance_band
    days_left = max((exam_date - metrics.report_date).days, 0)
    started = min(metrics.started_card_count, vocabulary_target_count)
    remaining_words = max(vocabulary_target_count - started, 0)
    required_new_per_day = _required_per_day(remaining_words, days_left)
    progress_percent = round(started / vocabulary_target_count * 100) if vocabulary_target_count else 0
    today_push_line = _today_push_line(metrics.new_count, required_new_per_day)
    headline = _pick_line(_headline_bank(band, days_left), metrics.report_date.toordinal())

    goal_line = "已達標" if metrics.goal_met else f"未達標，還差 {metrics.daily_goal_reviews - metrics.review_count} 題"
    success_percent = round(metrics.success_rate * 100)
    friction_line = _friction_line(metrics.again_count, metrics.review_count)

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
        ]
    )


def _headline_bank(band: str, days_left: int) -> list[str]:
    urgent_suffix = "倒數壓力已經上桌，今天的每一題都算數。" if days_left <= 35 else "先把節奏踩穩，後面才不會追到冒煙。"
    return {
        "zero": [
            f"今天單字進度掛零。{urgent_suffix}",
            "今天沒有新增火力，單字本們正在旁邊等人點名。",
            "今日學習雷達安靜無聲，會考倒數可不會一起暫停。",
        ],
        "low": [
            f"今天有動起來，但離安全速度還差一截。{urgent_suffix}",
            "有刷就有分，但今天比較像熱身，不像衝刺。",
            "單字列車有發車，只是速度還可以再催一下。",
        ],
        "met": [
            "今天有守住節奏，單字債沒有繼續長大。",
            "今日進度過關，記憶肌肉有確實報到。",
            "這波有穩住，會考單字牆少了一小塊。",
        ],
        "strong": [
            "今天火力很夠，單字們排隊進腦袋打卡。",
            "今日輸出偏猛，會考倒數被你反壓一波。",
            "這不是暖身，這是把單字清單往前推土機式處理。",
        ],
    }[band]


def _today_push_line(new_count: int, required_new_per_day: int) -> str:
    if required_new_per_day == 0:
        return "今天新開：目標已清完，現在重點是穩定複習。"
    if new_count == 0:
        return f"今天新開：0 個；照目標節奏今天應該補 {required_new_per_day} 個。"
    if new_count >= required_new_per_day:
        surplus = new_count - required_new_per_day
        return f"今天新開：{new_count} 個，超過建議節奏 {surplus} 個。"
    return f"今天新開：{new_count} 個，離建議節奏還差 {required_new_per_day - new_count} 個。"


def _friction_line(again_count: int, review_count: int) -> str:
    if review_count == 0:
        return "狀態：今天沒有留下作答紀錄，明天請讓單字知道誰才是考生。"
    again_rate = again_count / review_count
    if again_rate >= 0.4:
        return "狀態：今天卡關偏多，這不是失敗，是大腦在標記需要二刷的地方。"
    if again_rate >= 0.2:
        return "狀態：有幾個單字在裝熟，明天複習時優先抓出來。"
    return "狀態：整體算順，接下來要靠連續出勤把它變成穩定分數。"


def _required_per_day(remaining_words: int, days_left: int) -> int:
    if remaining_words <= 0:
        return 0
    return ceil(remaining_words / max(days_left, 1))


def _pick_line(lines: list[str], seed: int) -> str:
    return lines[seed % len(lines)]
