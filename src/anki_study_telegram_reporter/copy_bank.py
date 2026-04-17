"""Traditional Chinese copy lines for Telegram reports.

Lines are picked deterministically by a seed so each day × slot × performance
combination produces a different but reproducible message.

STATUS_LINES are appended after the "N 題還不熟（X%）" prefix (or standalone
for the zero band). They should read naturally in that position.

NUDGES are group call-to-action templates. They receive a `{target}` placeholder
that resolves to the tagged learner or to a neutral fallback when nobody is
tagged.

COMPARISON_LINES are appended after the "上次後：刷 +N 題" delta summary.
They should stay short enough for Telegram and use tech references sparingly:
the message should read like natural Traditional Chinese first.
"""

STATUS_LINES: dict[str, dict[str, list[str]]] = {
    "zero": {
        "morning": [
            "今天還沒開刷，先做一小題暖身",
            "進度條還沒亮，先點第一格就好",
            "Anki 已經待命，刷一輪讓今天有紀錄",
            "先不用衝量，五分鐘也算啟動",
            "今日紀錄還空著，先補第一筆",
            "先開一個小分支，從一題開始",
        ],
        "evening": [
            "今天還沒留下紀錄，睡前補一小輪就好",
            "進度條還空著，先存一點給明天",
            "今天先不求多，補幾題讓節奏接上",
            "睡前刷一小輪，明天比較好接",
            "今日版本還沒更新，補一點就有紀錄",
            "先做一個小收尾，別讓今天空白",
        ],
    },
    "low": {
        "morning": [
            "已經開刷了，再補一點就更穩",
            "進度有動，先把節奏接起來",
            "暖身完成，下一輪會更順",
            "今天有起步，再多幾題更安心",
            "分支開好了，繼續往前推一點",
            "先累積手感，晚點再補量",
        ],
        "evening": [
            "今天有累積，再補一小輪會更完整",
            "進度有動，收尾再加幾題",
            "還差一點達標，但節奏已經接上",
            "睡前補幾題，明天會輕鬆一點",
            "今天不是空白，收尾再拉一格",
            "先穩穩補量，不用一次爆衝",
        ],
    },
    "met": {
        "morning": [
            "今日目標已達成，照這個節奏走",
            "進度已到位，接下來穩穩維持",
            "這輪刷得穩，明天繼續接",
            "今天有交代，進度條好看",
            "節奏已上線，保持就很夠",
            "目標已過線，可以安心往下安排",
        ],
        "evening": [
            "今日目標完成，可以收工",
            "進度有補上，明天不用重開機",
            "這輪有顧到，單字庫又更新一版",
            "今天節奏穩，睡前可以放心",
            "目標已達成，明天照表接續",
            "今天沒有空轉，進度確實往前",
        ],
    },
    "strong": {
        "morning": [
            "今天刷很滿，單字牆被推進一大段",
            "進度條跑很快，可以記一筆亮眼紀錄",
            "輸出很漂亮，今天算大改版",
            "火力全開，目標被超車",
            "單字庫更新很有感，手感在線",
            "今天像連發閃電講，量和節奏都有",
        ],
        "evening": [
            "今天刷到很紮實，可以漂亮收工",
            "單字牆前進一大段，明天接著守住",
            "進度條被你推很遠，這波很可以",
            "今日紀錄很亮，值得留在更新紀錄",
            "今天不是普通達標，是加碼完成",
            "這輪輸出很穩，睡前可以安心",
        ],
    },
}

NUDGES: dict[str, list[str]] = {
    "behind": [
        "幫{target}打氣一下，先把第一輪開起來",
        "溫柔提醒{target}先刷幾題",
        "約{target}五分鐘刷一小輪",
        "幫{target}把節奏叫回來",
        "路過幫{target}留個加油",
        "提醒{target}不用一次補完，先開始就好",
        "幫{target}守一下連續紀錄",
        "用友善推力陪{target}把進度推回來",
    ],
    "on_track": [
        "幫{target}按個讚，明天繼續",
        "幫{target}守住今天的好節奏",
        "留一句鼓勵，讓{target}明天更好開場",
        "繼續陪{target}跑，進度在線",
        "幫{target}加個油，這波有穩",
        "路過幫{target}打氣一下，連續紀錄值得守",
        "幫{target}記一筆，這個節奏可以保留",
        "給{target}一點回饋，讓好節奏留下來",
    ],
}

COMPARISON_LINES: dict[str, list[str]] = {
    "idle": [
        "這段還沒有新增紀錄，先從一小輪開始",
        "上次後還沒開刷，先點亮進度條",
        "目前安靜如空 repo，需要第一筆 commit",
        "先補幾題，讓今天有 log",
    ],
    "catchup": [
        "有開始補量，繼續接上就好",
        "節奏回來了，再推一點會更穩",
        "像修 bug，一次處理一小段",
        "已經有動靜，先把手感接起來",
    ],
    "on_track": [
        "節奏有接上，今天進度穩",
        "這段補得剛好，明天照著走",
        "進度有往前，單字庫更新成功",
        "這波有穩住，可以先喘口氣",
    ],
    "surge": [
        "這段刷得很有感，進度大步往前",
        "單字牆被推進一段，今天很亮",
        "這波像閃電講連發，量很足",
        "進度條突然長高，群組可以倒香檳水",
    ],
    "noisy": [
        "不熟的訊號很清楚，下一輪就有方向",
        "需要回頭看的題比較多，這是好線索",
        "這段像在除錯，log 很完整",
        "先穩住不熟的字，下一輪會更準",
    ],
    "clean": [
        "這段都很順，手感不錯",
        "沒有不熟標記，這輪很乾淨",
        "這波品質穩，像 demo 一次過",
        "不熟訊號很少，可以安心往下走",
    ],
}
