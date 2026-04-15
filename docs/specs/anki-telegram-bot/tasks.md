# Tasks: Anki Telegram Study Reporter

## Phase 0: Project Foundation

- [x] Initialize Python project metadata.
- [x] Add `.gitignore` for `.env`, caches, temp Anki data, logs, and build outputs.
- [x] Add `.env.example` with all supported configuration keys.
- [x] Add README with local dry-run and GitHub Actions setup instructions.
- [x] Add baseline test tooling.

Acceptance:

- A fresh clone can install dependencies.
- `pytest` runs successfully.
- The README documents the MVP workflow.

## Phase 1: CLI and Configuration

- [x] Add `report` CLI command.
- [x] Implement env and `.env` loading.
- [x] Implement config validation for dry-run, mock, ankiweb, and Telegram send modes.
- [x] Add `--source`, `--date`, `--dry-run`, and `--send` flags.

Acceptance:

- `report --source mock --dry-run` runs without secrets.
- Missing secrets fail with clear messages only when the selected mode needs them.
- Tests cover config parsing and validation.

## Phase 2: Mock Source and Message Renderer

- [x] Define metric data structures.
- [x] Add mock fixture data.
- [x] Implement message renderer for zero, low, met, and strong activity bands.
- [x] Add deterministic rendering behavior for tests.

Acceptance:

- Mock reports produce readable Traditional Chinese output.
- Tests cover all message bands.
- No Telegram request is made in dry-run mode.

## Phase 3: Telegram Delivery

- [x] Implement Telegram Bot API client.
- [x] Support optional `TELEGRAM_THREAD_ID`.
- [x] Add dry-run guard.
- [x] Add error handling for non-2xx and Telegram API `ok=false` responses.

Acceptance:

- Dry-run prints the message only.
- Real send requires explicit send mode and Telegram secrets.
- Telegram API failures exit non-zero with a clear error.

## Phase 4: Anki Collection Read Model

- [x] Define read-only collection handle.
- [x] Implement SQLite revlog parser.
- [x] Implement timezone-aware date boundary logic.
- [x] Implement deck inclusion/exclusion filters.
- [x] Add SQLite fixture tests.

Acceptance:

- Metrics are correct for fixture revlog rows.
- `Asia/Taipei` day boundaries are tested.
- Deck filters are tested.

## Phase 5: AnkiWeb Sync PoC

- [x] Pin and document the Anki package/version used for sync.
- [x] Implement temporary profile/workspace creation.
- [x] Authenticate with Anki credentials.
- [x] Download latest collection into temp storage.
- [x] Verify no upload path is executed.
- [x] Open the downloaded collection read-only.
- [x] Clean up temporary data.

Acceptance:

- A local run can fetch collection data using test Anki credentials. (Pending live credential verification.)
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
