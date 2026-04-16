# Anki Study Telegram Reporter

Automatically fetches your Anki study history from AnkiWeb and posts daily progress reports to a Telegram group, enabling community-driven accountability for exam preparation.

> [中文版](README.md)

## Sample Report

```
📊 會考單字日報｜倒數 31 天
[▓▓▓░░░░░░░] 26%｜已收錄 420 / 1600 字
🎯 今天刷 132 題 ✅｜新收 18 字，差 21 跟上節奏
🟢 答錯 9 題（7%），進度有推，明天不用帶 blocker 起床
🫵 比上次 +36 題、新字 +6、錯題 +2｜有把 backlog 往下清，maintainer 可以先喘一口氣；請幫盯 @someone：有在 ship，幫忙維持這個 deploy 頻率。
```

Reports are generated in Traditional Chinese. The tone adapts automatically: 🔴 no activity, 🟡 below goal, 🟢 goal met or exceeded.
Scheduled reports without `--date` read the previous successful send time, compare activity since then, and include delta feedback in the copy.

## Quick Start (Fork & Deploy)

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram and run `/newbot`
2. Save the **Bot Token**
3. Add the bot to your target group
4. Obtain the group's **Chat ID** (e.g. via [@userinfobot](https://t.me/userinfobot))

### 2. Configure GitHub Secrets

In your forked repo, go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|-------------|
| `ANKI_USERNAME` | AnkiWeb account (email) |
| `ANKI_PASSWORD` | AnkiWeb password |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Target group chat ID |

Optional:

| Secret | Description |
|--------|-------------|
| `TELEGRAM_THREAD_ID` | Thread ID if the group has Topics enabled |

### 3. Customize Variables (Optional)

Under **Settings → Secrets and variables → Actions → Variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `TIMEZONE` | `Asia/Taipei` | Timezone for report date boundaries |
| `DAILY_GOAL_REVIEWS` | `100` | Daily review count target |
| `VOCABULARY_TARGET_COUNT` | `1600` | Total vocabulary goal |
| `EXAM_DATE` | `2026-05-17` | Exam date for countdown |
| `REPORT_SLOT` | `auto` | Report tone: `auto`, `morning`, or `evening` |
| `REPORT_STATE_PATH` | `.report-state/last-success.json` | State file path for the previous successful send time, used for delta feedback |
| `SUPERVISOR_USERNAMES` | (empty) | Telegram usernames to tag, comma-separated |
| `TARGET_DECKS` | (empty) | Only count these decks, comma-separated; empty = all |
| `EXCLUDED_DECKS` | (empty) | Exclude these decks |

### 4. Schedule

The default workflow runs twice daily at 18:00 and 22:00 Asia/Taipei:

```yaml
schedule:
  - cron: "0 10 * * *"   # 18:00 Asia/Taipei
  - cron: "0 14 * * *"   # 22:00 Asia/Taipei
```

Edit `.github/workflows/daily-report.yml` to change the schedule.

You can also trigger a run manually from the GitHub Actions tab:

| Input | Description |
|-------|-------------|
| `send` | Set to `true` to send to Telegram; default `false` (dry-run) |
| `source` | `ankiweb` (default) or `mock` (test with fixture data) |
| `report_date` | Optional `YYYY-MM-DD`; empty = today |

## Local Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Generate a mock report (no credentials needed)
uv run anki-study-telegram-reporter report --source mock --date 2026-04-16 --dry-run
```

### Test with AnkiWeb

```bash
cp .env.example .env
# Fill in ANKI_USERNAME and ANKI_PASSWORD
uv run anki-study-telegram-reporter report --source ankiweb --dry-run
```

Add `--send` to deliver to Telegram (requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`).

### Keep Downloaded Collection

Set `ANKI_COLLECTION_OUTPUT_DIR=anki-collection-debug` in `.env` to retain the downloaded SQLite database at `anki-collection-debug/collection.anki2` for inspection. This directory is git-ignored.

## How It Works

```
GitHub Actions (scheduled)
  → Download collection from AnkiWeb (read-only, never uploads)
  → Parse SQLite database for daily study metrics
  → Generate Traditional Chinese report
  → Send via Telegram Bot API
```

The app only reads Anki data. **It never modifies or uploads anything.** If AnkiWeb requests an upload, the app refuses and exits with an error.

## Troubleshooting

- **No report sent**: Check GitHub Actions logs. Verify all required secrets are set.
- **AnkiWeb auth failure**: Confirm `ANKI_USERNAME` and `ANKI_PASSWORD` are correct.
- **Duplicate sends**: The MVP allows duplicates on manual re-runs. This is intentional to support retrying failed deliveries.
- **Security**: Credentials are stored in GitHub Actions Secrets and never appear in logs. The app redacts sensitive values from error messages.

## License

[MIT License](LICENSE)
