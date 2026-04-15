# Anki Telegram Study Reporter

This project will generate a daily Anki study report and post it to a Telegram group.

Development follows Spec-Driven Development. Start with the spec documents:

- `docs/specs/anki-telegram-bot/requirements.md`
- `docs/specs/anki-telegram-bot/design.md`
- `docs/specs/anki-telegram-bot/tasks.md`

## Current Status

Phase 0 implementation: project foundation.

The intended production workflow is:

1. GitHub Actions runs on a schedule.
2. The app fetches the latest Anki collection using Anki credentials from GitHub Actions secrets.
3. The app reads study history in read-only mode.
4. The app generates a Traditional Chinese report.
5. The app sends the report through Telegram Bot API.

The AnkiWeb collection sync implementation is treated as the main technical risk and will be validated separately before production use.

## Local Development

Create a virtual environment and install development dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

The first runnable target will be:

```bash
anki-telegram report --source mock --dry-run
```

Run the mock report through `uv`:

```bash
uv run anki-telegram report --source mock --date 2026-04-15 --dry-run
```

The AnkiWeb source is wired through the official `anki==25.9.2` package. A live
AnkiWeb run requires real credentials in `.env` or the environment:

```bash
uv run anki-telegram report --source ankiweb --dry-run
```

The sync adapter always requests full-sync downloads with `upload=False`; the
downloaded collection is opened by the metrics layer in SQLite read-only mode.
