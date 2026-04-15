# Requirements: Anki Telegram Study Reporter

## Goal

Build a Telegram bot workflow that reads the user's Anki study activity and posts a playful daily study report to a Telegram group. The production workflow runs on GitHub Actions on a schedule, using GitHub Actions secrets for Anki and Telegram credentials. The project must also support local development validation without posting to the real group.

## Scope

### In Scope

- Run as a command-line application suitable for GitHub Actions.
- Fetch the latest Anki collection using Anki account credentials.
- Read study activity from the local Anki collection database in read-only mode.
- Compute daily study metrics for a configured timezone.
- Generate Traditional Chinese report text with a playful tone.
- Send the report to a Telegram group.
- Support dry-run mode for local development and CI validation.
- Support mock data so message generation can be tested without Anki credentials.
- Provide a GitHub Actions workflow with scheduled and manual triggers.

### Out of Scope

- Editing cards, decks, notes, or Anki scheduling data.
- Uploading changes back to AnkiWeb.
- Replacing Anki's normal sync behavior.
- Multi-user leaderboard support.
- Running a long-lived Telegram bot process.
- Receiving Telegram commands.

## Functional Requirements

### FR-1: Configuration

The application must read configuration from environment variables and optional local `.env` files.

Required production variables:

- `ANKI_USERNAME`
- `ANKI_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Optional variables:

- `TELEGRAM_THREAD_ID`
- `TIMEZONE`, default `Asia/Taipei`
- `DAILY_GOAL_REVIEWS`, default `100`
- `VOCABULARY_TARGET_COUNT`, default `1600`
- `EXAM_DATE`, default `2026-05-17`
- `REPORT_SLOT`, one of `auto`, `morning`, or `evening`, default `auto`
- `TARGET_DECKS`
- `EXCLUDED_DECKS`
- `DRY_RUN`, default `true` outside GitHub Actions
- `SOURCE`, one of `mock` or `ankiweb`

Acceptance criteria:

- Missing required variables produce a clear error before network calls.
- Secret values are never printed.
- `.env.example` documents every supported variable.

### FR-2: Local Development Modes

The CLI must support development validation without real Anki or Telegram calls.

Acceptance criteria:

- `--source mock --dry-run` generates a report from fixture data.
- `--dry-run` prints the final Telegram message instead of sending it.
- `--date YYYY-MM-DD` computes a report for a specific local date.
- Real Telegram sends require an explicit non-dry-run mode.

### FR-3: Anki Collection Fetching

The production source must fetch the latest Anki collection into a temporary workspace using Anki credentials.

Acceptance criteria:

- The collection is fetched into a fresh temporary directory.
- The implementation does not reuse a developer's local Anki profile.
- The implementation does not upload local changes back to AnkiWeb.
- If a conflict, full-sync ambiguity, or write requirement is detected, the command fails safely.
- Downloaded collection data is not committed, logged, or stored as a GitHub Actions artifact.

### FR-4: Study Metrics

The application must compute daily study metrics from Anki review history.

Minimum metrics:

- `review_count`
- `distinct_card_count`
- `new_count`
- `learning_count`
- `review_card_count`
- `relearn_count`
- `total_card_count`
- `started_card_count`
- `again_count`
- `hard_count`
- `good_count`
- `easy_count`
- `success_rate`
- `goal_met`

Acceptance criteria:

- Metrics are computed for the configured timezone.
- Deck filtering honors `TARGET_DECKS` and `EXCLUDED_DECKS`.
- A day with no activity is represented explicitly instead of treated as an error.
- The metric parser is covered by tests using fixture data.

### FR-5: Message Generation

The application must generate a Traditional Chinese Telegram message based on the computed metrics.

Acceptance criteria:

- The message includes the local report date.
- The message includes core metrics and goal status.
- The tone varies for zero activity, under-goal, goal-met, and strong-performance cases.
- The message is deterministic enough for tests, or randomness can be seeded/disabled.
- The generated text must not include secrets or raw database content.

### FR-6: Telegram Delivery

The application must send the generated message through Telegram Bot API.

Acceptance criteria:

- `TELEGRAM_CHAT_ID` is required for real sends.
- `TELEGRAM_THREAD_ID` is included only when configured.
- Telegram API failures produce a clear non-zero command failure.
- Dry-run mode never calls Telegram.

### FR-7: GitHub Actions

The repository must include a scheduled workflow.

Acceptance criteria:

- The workflow supports `schedule` and `workflow_dispatch`.
- The schedule defaults to a Taipei evening report time.
- The workflow installs dependencies from a lockfile.
- The workflow can run a mock dry-run validation without secrets.
- Real production sends use GitHub Actions secrets.

## Non-Functional Requirements

### Security

- Secrets must only be read from environment variables or local `.env`.
- Logs must redact secret-shaped values where practical.
- Anki collection files, cache directories, logs, and `.env` must be ignored by git.

### Reliability

- The CLI should fail fast on configuration problems.
- Network failures should produce actionable errors.
- The application should avoid duplicate sends where feasible.

### Maintainability

- The code should separate source fetching, metric extraction, message generation, and Telegram delivery.
- AnkiWeb fetching should be behind an interface because it is the highest-risk integration point.
- Tests should cover logic that does not require external services.

## Open Questions

- Which Anki package/version should be pinned for headless collection sync?
- What exact Anki full-sync behavior can be made read-only and safe in GitHub Actions?
- Should duplicate-send prevention be part of MVP or a post-MVP task?
- Should `TARGET_DECKS` match exact deck names, prefixes, or regex patterns?
