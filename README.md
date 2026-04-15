# Anki Study Telegram Reporter

This project generates daily Anki study progress reports and posts them to a Telegram group.

Development follows Spec-Driven Development. Start with the spec documents:

- `docs/specs/anki-telegram-bot/requirements.md`
- `docs/specs/anki-telegram-bot/design.md`
- `docs/specs/anki-telegram-bot/tasks.md`

## Current Status

MVP implementation in progress. Local mock reports, Telegram delivery, read-only
Anki collection metrics, and AnkiWeb collection download are implemented.

The intended production workflow is:

1. GitHub Actions runs on a schedule.
2. The app fetches the latest Anki collection using Anki credentials from GitHub Actions secrets.
3. The app reads study history in read-only mode.
4. The app generates a Traditional Chinese report.
5. The app sends the report through Telegram Bot API.

The AnkiWeb collection sync path has been verified locally with a dry-run. It
downloads to temporary storage, requests full-downloads with `upload=False`, and
opens the downloaded collection through SQLite read-only mode.

## Local Development

Install dependencies:

```bash
uv sync --extra dev
```

Run tests:

```bash
uv run pytest
```

Run a mock report:

```bash
uv run anki-study-telegram-reporter report --source mock --date 2026-04-15 --dry-run
```

The old `anki-telegram` command is kept as a compatibility alias, but new usage
should prefer `anki-study-telegram-reporter`.

Run a local AnkiWeb dry-run:

```bash
cp .env.example .env
uv run anki-study-telegram-reporter report --source ankiweb --dry-run
```

The `.env` file must contain at least:

```env
ANKI_USERNAME=
ANKI_PASSWORD=
```

For a real Telegram send, also set:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Then run:

```bash
uv run anki-study-telegram-reporter report --source ankiweb --send
```

To keep the downloaded collection for local inspection, set:

```env
ANKI_COLLECTION_OUTPUT_DIR=anki-collection-debug
```

Then run:

```bash
uv run anki-study-telegram-reporter report --source ankiweb --dry-run
```

The downloaded SQLite collection will be kept at:

```text
anki-collection-debug/collection.anki2
```

This directory is ignored by git.

## GitHub Actions

The workflow is defined at `.github/workflows/daily-report.yml`.

It runs:

- tests on every workflow run
- a mock dry-run without secrets
- the production report on the daily schedule or when manually triggered with `send=true`

The default schedule runs twice per day, 08:00 and 23:00 Asia/Taipei:

```yaml
cron: "0 0 * * *"
cron: "0 15 * * *"
```

Required repository secrets:

- `ANKI_USERNAME`
- `ANKI_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Optional repository secret:

- `TELEGRAM_THREAD_ID`

Optional repository variables:

- `TIMEZONE`, default `Asia/Taipei`
- `DAILY_GOAL_REVIEWS`, default `100`
- `VOCABULARY_TARGET_COUNT`, default `1600`
- `EXAM_DATE`, default `2026-05-17`
- `REPORT_SLOT`, default `auto`; use `morning` or `evening` to force copy style
- `SUPERVISOR_USERNAMES`, comma-separated Telegram usernames to tag, with or without `@`
- `TARGET_DECKS`
- `EXCLUDED_DECKS`

Manual dispatch inputs:

- `send`: set to `true` to send to Telegram; default is `false`
- `source`: `mock` or `ankiweb`; default is `ankiweb`
- `report_date`: optional `YYYY-MM-DD`

## Failure Modes

Common failures:

- Missing `ANKI_USERNAME` or `ANKI_PASSWORD`: the AnkiWeb source cannot run.
- Missing `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID`: real sends cannot run.
- AnkiWeb requests full upload: the app refuses to upload from automation.
- Telegram API returns `ok=false`: the command exits non-zero and reports the Telegram error.

The app redacts known secret values from command-level errors. Avoid enabling
extra debug logging around third-party libraries in public CI logs.

## Duplicate Sends

MVP behavior allows duplicate sends when a workflow is manually re-run with
`send=true`, or when the scheduled job is retried. This is intentional for the
first production version so failed deliveries can be retried manually.

A future hardening step can store a per-date send marker in GitHub Actions cache
and require an explicit `FORCE_SEND=true` override.
