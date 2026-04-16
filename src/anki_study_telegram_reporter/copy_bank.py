"""Traditional Chinese copy lines for Telegram reports.

Lines are picked deterministically by a seed so each day × slot × performance
combination produces a different but reproducible message.

STATUS_LINES are appended after the "答錯 N 題（X%）" prefix (or standalone
for the zero band). They should read naturally in that position.

NUDGES are supervisor tag-line suffixes, split into "behind" (zero/low) and
"on_track" (met/strong) to match the tone to the student's performance.

COMPARISON_LINES are appended after the "比上次 +N 題" delta summary.
They should work well in a SITCON-adjacent group: technical enough to feel
native, but still readable without knowing a private inside joke.
"""

STATUS_LINES: dict[str, dict[str, list[str]]] = {
    "zero": {
        "morning": [
            "今日 commit 數：0，單字 repo 等你開第一筆 PR",
            "CI 還沒被觸發，先 push 一小輪也算簽到",
            "Anki 開著但沒 input，跟開了 IDE 沒寫 code 一樣",
            "進度條冰凍中，需要 maintainer 手動 unblock",
            "build 掛蛋，連 bot 都比你早起",
            "今天 uptime 是 0%，建議手動重啟學習服務",
        ],
        "evening": [
            "一整天零 commit，睡前寫幾題算 hotfix",
            "changelog 是空的要發布了，最後機會 patch 幾題",
            "今天 production 零流量，明天 backlog 正在膨脹",
            "deploy 紀錄全空，趁睡前搶救一下 SLA",
            "CI/CD 今天全休，明天的你會感謝今晚加班的自己",
            "直接空白交卷的話，明天 standup 很難報告",
        ],
    },
    "low": {
        "morning": [
            "有 push 但 CI 還沒綠，再補幾題就過線",
            "branch 建好了，commit 再多一些就能開 PR",
            "有開工但離 merge 還有段路，繼續推",
            "先別收攤，test coverage 還沒到安全線",
            "有暖機但引擎還沒全開，下半場再衝一波",
            "changelog 有一行了，目標是寫到能發 release",
        ],
        "evening": [
            "PR 開了但 CI 沒全過，睡前補幾題就綠了",
            "今天 diff 有點薄，再厚一點明天比較輕鬆",
            "進度可用但 buffer 不夠，能推就多推一點",
            "不是沒努力，是 deadline 比想像中近",
            "今晚加一小段 OT，明天的自己會感謝你",
            "有在動但火力不足，明天記得一開場就上線",
        ],
    },
    "met": {
        "morning": [
            "CI 全綠，錯的字已排入明天 review queue",
            "今天的 PR 順利 merge，進度正常推進中",
            "build pass，maintain 這個節奏就穩了",
            "pipeline 跑完，今天的 sprint 有完成",
            "今天的 output 有交代，可以先去顧別的坑",
            "commit 品質不錯，持續 ship 就對了",
        ],
        "evening": [
            "CI 綠燈收工，錯的字已排進明天 queue",
            "今天 deploy 成功，可以安心關 terminal",
            "進度有推，明天不用帶 blocker 起床",
            "task 已 close，changelog 有東西可以寫",
            "build 通過，tech debt 今天沒有長大",
            "沒讓 sprint 空轉，今天可以 ship it",
        ],
    },
    "strong": {
        "morning": [
            "直接 merge 一大包，backlog 被削掉一段",
            "throughput 破表，連 reviewer 都跟不上",
            "一個早上把 milestone 推超遠，可以做 stretch goal 了",
            "效率拉滿，這就是 hackathon 精神",
            "不只達標還超額 deploy，commit graph 超漂亮",
            "火力全開，進度條被你拉著跑",
        ],
        "evening": [
            "全力 speedrun，單字牆被突破一大段",
            "deploy 破紀錄，backlog 直接少了一截",
            "commit graph 今天超綠，壓力被你反壓一波",
            "今日 output 猛到可以寫成 blog post",
            "不是普通出勤，是 hackathon 等級的輸出",
            "今天成績可以直接當 release note 發布",
        ],
    },
}

NUDGES: dict[str, list[str]] = {
    "behind": [
        "進度亮紅燈，請幫忙友善催更",
        "需要社群支援，看到的人麻煩 ping 一下",
        "請發一個友善的 /remind，這是自動化關懷",
        "進度落後，溫柔但堅定地敲一下碗",
        "PR 還沒 merge，有空幫忙推一把",
        "出勤率需要 boost，路過請留言打氣",
        "請幫忙當 reviewer，盯一下有沒有在讀",
        "需要社群壓力維持動力，各位支援一下",
    ],
    "on_track": [
        "今天有認真跑 pipeline，幫忙按個讚",
        "進度正常，請繼續保持監督火力",
        "有在 ship，幫忙維持這個 deploy 頻率",
        "今天的 commit 很紮實，給點正向 feedback",
        "streak 維持中，幫忙守護連續出勤",
        "今天戰績不錯，鼓勵他明天繼續上線",
        "進度在軌道上，但到 deadline 前都不能鬆懈",
        "表現不錯，持續監控到 release day",
    ],
}

COMPARISON_LINES: dict[str, list[str]] = {
    "idle": [
        "這段 timeline 沒新 commit，議程表暫時空白",
        "上次到現在 0 題，bot 已經在門口發提醒傳單",
        "活動場地很安靜，現在需要第一位講者上台",
        "沒有新增紀錄，這段像沒有人認領的 issue",
    ],
    "catchup": [
        "有 push 了，但 CI 還差一點才會綠",
        "進度開始有聲音，還需要再補幾個 commit",
        "像 CFP 前夜有在趕稿，但還沒到可以送出的版本",
        "BoF 已經開場，現在需要把討論串接著推下去",
    ],
    "on_track": [
        "這段增量已 merge，今天 quota 綠燈",
        "節奏有接上，像議程準時跑完沒有 delay",
        "這波輸出可以寫進 release note，明天繼續維護",
        "有把 backlog 往下清，maintainer 可以先喘一口氣",
    ],
    "surge": [
        "這段像 lightning talk 連發，進度直接有聲量",
        "輸出量接近 unconference 爆場，單字牆被推進一截",
        "commit graph 突然長出一片綠，群組可以開香檳水",
        "這波 throughput 很 SITCON，志工台都想幫你貼貼紙",
    ],
    "noisy": [
        "錯題偏吵，建議先開 issue 逐一追蹤",
        "fail case 有點多，這段需要加測試也需要再複習",
        "錯題像會場 Wi-Fi 尖峰，先穩住再衝下一輪",
        "紅燈不少，但至少 log 很完整，下一輪可以精準修",
    ],
    "clean": [
        "這段零失誤，像 demo 一次就過",
        "沒有 Again，CI 乾淨到 reviewer 會點頭",
        "這波品質很穩，像排練過的 lightning talk",
        "錯題噪音歸零，這段可以安心標成 stable",
    ],
}
