"""Render study metrics into Telegram-ready text."""

from __future__ import annotations

from .metrics import StudyMetrics


def render_report(metrics: StudyMetrics) -> str:
    band = metrics.performance_band
    headline = {
        "zero": "今日 Anki 安靜得像圖書館閉館。",
        "low": "今日 Anki 有動起來，但還在暖機區。",
        "met": "今日 Anki 達標，記憶肌肉有練到。",
        "strong": "今日 Anki 火力全開，卡片們排隊下班。",
    }[band]

    goal_line = "已達標" if metrics.goal_met else f"未達標，還差 {metrics.daily_goal_reviews - metrics.review_count} 題"
    success_percent = round(metrics.success_rate * 100)

    return "\n".join(
        [
            f"Anki 今日戰報 {metrics.report_date.isoformat()}",
            headline,
            "",
            f"答題數：{metrics.review_count} / {metrics.daily_goal_reviews}（{goal_line}）",
            f"新卡：{metrics.new_count}",
            f"學習中：{metrics.learning_count}",
            f"複習卡：{metrics.review_card_count}",
            f"按鈕分布：Again {metrics.again_count}、Hard {metrics.hard_count}、Good {metrics.good_count}、Easy {metrics.easy_count}",
            f"大略正確率：{success_percent}%",
        ]
    )
