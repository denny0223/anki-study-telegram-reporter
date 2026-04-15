# Anki Study Telegram Reporter

每天自動從 AnkiWeb 抓取學習紀錄，產生進度報告並發送到 Telegram 群組，讓社群幫忙監督學習進度。

> [English version](README.en.md)

## 報告範例

```
📊 會考單字日報｜倒數 31 天
[▓▓▓░░░░░░░] 26%｜已收錄 420 / 1600 字
🎯 今天刷 132 題 ✅｜新收 18 字，差 21 跟上節奏
🟢 答錯 9 題（7%），進度有推，明天不用帶 blocker 起床
🫵 請幫盯 @someone：有在 ship，幫忙維持這個 deploy 頻率。
```

報告會依據當天表現自動切換語氣：沒讀書 🔴、不夠 🟡、達標 🟢，讓群組裡的人一眼看出該不該出手催。

## Fork 之後怎麼用

### 第一步：建立 Telegram Bot

1. 在 Telegram 找 [@BotFather](https://t.me/BotFather)，輸入 `/newbot` 建立機器人
2. 記下拿到的 **Bot Token**
3. 把機器人加入你的目標群組
4. 取得群組的 **Chat ID**（可以透過 [@userinfobot](https://t.me/userinfobot) 或將機器人加入群組後呼叫 Telegram API 取得）

### 第二步：設定 GitHub Secrets

在你 fork 的 repo 進入 **Settings → Secrets and variables → Actions**，新增以下 secrets：

| Secret | 說明 |
|--------|------|
| `ANKI_USERNAME` | AnkiWeb 帳號（電子郵件） |
| `ANKI_PASSWORD` | AnkiWeb 密碼 |
| `TELEGRAM_BOT_TOKEN` | 從 BotFather 拿到的 token |
| `TELEGRAM_CHAT_ID` | 目標群組的 chat ID |

可選 secret：

| Secret | 說明 |
|--------|------|
| `TELEGRAM_THREAD_ID` | 如果群組有開啟 Topics，填入目標 thread ID |

### 第三步：依需求調整 Variables

在 **Settings → Secrets and variables → Actions → Variables** 設定（都有預設值，不設也能跑）：

| Variable | 預設值 | 說明 |
|----------|--------|------|
| `TIMEZONE` | `Asia/Taipei` | 報告的時區 |
| `DAILY_GOAL_REVIEWS` | `100` | 每日目標刷題數 |
| `VOCABULARY_TARGET_COUNT` | `1600` | 總單字目標數 |
| `EXAM_DATE` | `2026-05-17` | 考試日期，用來算倒數天數 |
| `REPORT_SLOT` | `auto` | 報告語氣：`auto` 依成績決定、`morning` 早場、`evening` 晚場 |
| `SUPERVISOR_USERNAMES` | （空） | 要 tag 的監督者 Telegram username，逗號分隔，例如 `alice,bob` |
| `TARGET_DECKS` | （空） | 只統計這些牌組，逗號分隔；空白 = 全部 |
| `EXCLUDED_DECKS` | （空） | 排除這些牌組 |

### 第四步：啟用排程

設定完成後，GitHub Actions 會自動依排程執行。預設每天台北時間 18:00 和 22:00 各發一次報告：

```yaml
# .github/workflows/daily-report.yml
schedule:
  - cron: "0 10 * * *"   # 18:00 Asia/Taipei
  - cron: "0 14 * * *"   # 22:00 Asia/Taipei
```

你可以直接修改 cron 來調整時間。

也可以在 GitHub Actions 頁面手動觸發（Run workflow），有以下選項：

| 輸入 | 說明 |
|------|------|
| `send` | 設為 `true` 才會真的發到 Telegram，預設 `false`（dry-run） |
| `source` | `ankiweb`（預設）或 `mock`（測試用假資料） |
| `report_date` | 指定日期 `YYYY-MM-DD`，空白 = 今天 |

## 本地開發

需要 [uv](https://docs.astral.sh/uv/) 套件管理工具。

```bash
# 安裝依賴
uv sync --extra dev

# 跑測試
uv run pytest

# 用假資料產生報告（不需要任何帳號）
uv run anki-study-telegram-reporter report --source mock --date 2026-04-16 --dry-run
```

### 連接 AnkiWeb 測試

```bash
cp .env.example .env
# 編輯 .env，填入 ANKI_USERNAME 和 ANKI_PASSWORD
uv run anki-study-telegram-reporter report --source ankiweb --dry-run
```

加上 `--send` 會真的發到 Telegram（需要同時設定 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`）。

### 保留下載的 collection

在 `.env` 設定 `ANKI_COLLECTION_OUTPUT_DIR=anki-collection-debug`，下載的 SQLite 資料庫會保留在 `anki-collection-debug/collection.anki2`，方便除錯。這個目錄已被 git 忽略。

## 運作原理

```
GitHub Actions (排程)
  → 從 AnkiWeb 下載 collection（唯讀，不會上傳）
  → 解析 SQLite 資料庫，計算當日學習指標
  → 產生繁體中文報告
  → 透過 Telegram Bot API 發送到群組
```

程式只會讀取 Anki 資料，**不會修改或上傳任何內容**。如果 AnkiWeb 要求上傳，程式會直接拒絕並報錯。

## 常見問題

**Q: 報告沒有發出來？**
- 檢查 GitHub Actions 的 log，確認 secrets 都有設定
- `ANKI_USERNAME` / `ANKI_PASSWORD` 錯誤會導致 AnkiWeb 連線失敗
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` 沒設會無法發送

**Q: 手動重跑會不會重複發送？**
- 會。目前 MVP 版本允許重複發送，方便失敗時手動重試。

**Q: 密碼安全嗎？**
- 密碼只存在 GitHub Actions Secrets，不會出現在 log 中。程式會自動遮蔽錯誤訊息中的敏感資訊。

## 授權

[MIT License](LICENSE)
