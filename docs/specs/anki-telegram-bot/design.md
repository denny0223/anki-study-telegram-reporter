# Design: Anki Telegram Study Reporter

## Development Approach

This project uses Spec-Driven Development:

1. Requirements define behavior and acceptance criteria.
2. Design defines architecture, boundaries, and risk controls.
3. Tasks map implementation steps to verifiable outcomes.
4. Tests and dry-runs validate each step before real Telegram delivery.

The AnkiWeb collection fetch is intentionally isolated because it has the highest technical and safety risk.

## Architecture

```text
GitHub Actions / local shell
        |
        v
CLI entrypoint
        |
        +--> Config loader
        |
        +--> Study source
        |       |
        |       +--> mock fixture source
        |       |
        |       +--> AnkiWeb collection source
        |
        +--> Metrics extractor
        |
        +--> Message renderer
        |
        +--> Telegram client
```

## Module Boundaries

### CLI

Responsibilities:

- Parse command flags.
- Load configuration.
- Select the study source.
- Coordinate report generation and delivery.
- Return non-zero exit codes on failure.

Non-responsibilities:

- No direct SQL.
- No Telegram API formatting details.
- No Anki sync implementation details.

### Config

Responsibilities:

- Load environment variables.
- Optionally load `.env` in local development.
- Validate required settings based on selected mode.
- Normalize timezone, deck filters, and booleans.

### Study Source

Responsibilities:

- Provide study data for a report date.
- Hide whether data came from mock fixtures or AnkiWeb.

Interface shape:

```python
class StudySource:
    def load_collection(self, config: AppConfig) -> CollectionHandle:
        ...
```

### AnkiWeb Source

Responsibilities:

- Create a temporary Anki workspace.
- Authenticate with Anki credentials.
- Download the latest collection.
- Return a read-only collection handle.
- Clean up temporary data.

Safety rules:

- Never use the user's local Anki profile.
- Never upload changes.
- Never store collection artifacts.
- Fail if the sync flow requires ambiguous conflict handling.

### Metrics Extractor

Responsibilities:

- Open the collection database read-only.
- Query review history for the configured local day.
- Apply deck filters.
- Convert raw revlog rows into report metrics.

Revlog type mapping:

- `type=0`: new cards.
- `type=1`: review cards.
- `type=2`: learning cards.
- `type=3`: relearning cards.

Notes:

- The Anki `revlog` table is the primary source for review activity.
- Time boundaries must be computed in the configured timezone and converted to the timestamp format used by Anki review logs.
- Tests should use small SQLite fixtures where possible.

### Message Renderer

Responsibilities:

- Convert metrics into Traditional Chinese text.
- Select tone based on performance band.
- Keep output deterministic for tests.

Message bands:

- `zero`: no study activity.
- `low`: activity exists but below goal.
- `met`: goal reached.
- `strong`: significantly above goal.

### Telegram Client

Responsibilities:

- Send a message through Telegram Bot API.
- Include `message_thread_id` only when configured.
- Surface API errors clearly.

Non-responsibilities:

- No message content decisions.
- No metric computation.

## Data Flow

1. CLI receives `report` command.
2. Config loader reads env and flags.
3. Study source loads a collection handle.
4. Metrics extractor computes daily metrics.
5. Message renderer creates final text.
6. If `dry_run` is true, CLI prints the text.
7. If `dry_run` is false, Telegram client sends the text.

## GitHub Actions Design

Workflow triggers:

- `schedule`: daily run.
- `workflow_dispatch`: manual run.

Jobs:

- `validate`: run lint and tests.
- `dry-run`: generate a mock report.
- `send-report`: run real AnkiWeb source and Telegram send.

The production job uses:

- `ANKI_USERNAME`
- `ANKI_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- optional `TELEGRAM_THREAD_ID`

## Duplicate Send Strategy

MVP behavior:

- Manual workflow runs may send again.
- Scheduled runs should execute once per configured schedule.

Post-MVP option:

- Store a send marker in GitHub Actions cache keyed by report date.
- Add `FORCE_SEND=true` to override.

## Risk Register

### Risk: AnkiWeb Sync Requires Write-Oriented Client Behavior

Mitigation:

- Implement AnkiWeb source as a PoC before depending on it.
- Use a fresh temporary profile.
- Keep the DB read-only after download.
- Fail safely on conflict/full-sync ambiguity.

### Risk: Credentials Leak Through Logs

Mitigation:

- Never print env values.
- Avoid debug logging raw request payloads.
- Keep downloaded collection out of artifacts.

### Risk: Timezone Boundary Bugs

Mitigation:

- Centralize date boundary computation.
- Test `Asia/Taipei` day boundaries.
- Support `--date` for reproducible runs.

### Risk: Telegram Spam During Development

Mitigation:

- Default to dry-run locally.
- Require explicit send mode.
- Support separate test chat configuration.

## Initial Technology Choices

- Language: Python.
- Runtime: Python 3.12.
- CLI: standard library `argparse` initially, unless project complexity justifies a CLI framework.
- HTTP: `httpx` or `requests`.
- Config: environment variables plus local `.env` support.
- Tests: `pytest`.
- Packaging: `pyproject.toml`.

These choices can be revisited during implementation if the Anki package imposes constraints.
