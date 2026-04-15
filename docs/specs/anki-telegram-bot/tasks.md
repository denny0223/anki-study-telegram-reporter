# Tasks: Anki Telegram Study Reporter

## Phase 0: Project Foundation

- [ ] Initialize Python project metadata.
- [ ] Add `.gitignore` for `.env`, caches, temp Anki data, logs, and build outputs.
- [ ] Add `.env.example` with all supported configuration keys.
- [ ] Add README with local dry-run and GitHub Actions setup instructions.
- [ ] Add baseline test tooling.

Acceptance:

- A fresh clone can install dependencies.
- `pytest` runs successfully.
- The README documents the MVP workflow.

## Phase 1: CLI and Configuration

- [ ] Add `report` CLI command.
- [ ] Implement env and `.env` loading.
- [ ] Implement config validation for dry-run, mock, ankiweb, and Telegram send modes.
- [ ] Add `--source`, `--date`, `--dry-run`, and `--send` flags.

Acceptance:

- `report --source mock --dry-run` runs without secrets.
- Missing secrets fail with clear messages only when the selected mode needs them.
- Tests cover config parsing and validation.

## Phase 2: Mock Source and Message Renderer

- [ ] Define metric data structures.
- [ ] Add mock fixture data.
- [ ] Implement message renderer for zero, low, met, and strong activity bands.
- [ ] Add deterministic rendering behavior for tests.

Acceptance:

- Mock reports produce readable Traditional Chinese output.
- Tests cover all message bands.
- No Telegram request is made in dry-run mode.

## Phase 3: Telegram Delivery

- [ ] Implement Telegram Bot API client.
- [ ] Support optional `TELEGRAM_THREAD_ID`.
- [ ] Add dry-run guard.
- [ ] Add error handling for non-2xx and Telegram API `ok=false` responses.

Acceptance:

- Dry-run prints the message only.
- Real send requires explicit send mode and Telegram secrets.
- Telegram API failures exit non-zero with a clear error.

## Phase 4: Anki Collection Read Model

- [ ] Define read-only collection handle.
- [ ] Implement SQLite revlog parser.
- [ ] Implement timezone-aware date boundary logic.
- [ ] Implement deck inclusion/exclusion filters.
- [ ] Add SQLite fixture tests.

Acceptance:

- Metrics are correct for fixture revlog rows.
- `Asia/Taipei` day boundaries are tested.
- Deck filters are tested.

## Phase 5: AnkiWeb Sync PoC

- [ ] Pin and document the Anki package/version used for sync.
- [ ] Implement temporary profile/workspace creation.
- [ ] Authenticate with Anki credentials.
- [ ] Download latest collection into temp storage.
- [ ] Verify no upload path is executed.
- [ ] Open the downloaded collection read-only.
- [ ] Clean up temporary data.

Acceptance:

- A local run can fetch collection data using test Anki credentials.
- The command fails safely on ambiguous sync conditions.
- No downloaded collection files remain after normal execution.

## Phase 6: GitHub Actions

- [ ] Add workflow with `schedule` and `workflow_dispatch`.
- [ ] Add test job.
- [ ] Add mock dry-run job.
- [ ] Add production send job using secrets.
- [ ] Document secret setup.

Acceptance:

- Workflow can be manually triggered.
- Mock dry-run works without Anki or Telegram secrets.
- Production job uses secrets and does not print them.

## Phase 7: Hardening

- [ ] Add structured logging with secret redaction.
- [ ] Add duplicate-send prevention or document MVP behavior.
- [ ] Add retry/backoff for transient network failures.
- [ ] Add failure-mode documentation.

Acceptance:

- Common failure modes have clear messages.
- Scheduled production use is documented.
- Security-sensitive files remain ignored by git.

## Implementation Order

Recommended order:

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5
7. Phase 6
8. Phase 7

The AnkiWeb sync PoC should remain isolated until it is proven safe. All other phases can be developed and tested independently with mock data.
