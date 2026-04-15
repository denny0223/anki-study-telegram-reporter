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
