from datetime import datetime

import pytest

from anki_study_telegram_reporter.state import (
    ReportStateError,
    load_last_successful_run,
    save_last_successful_run,
)


def test_report_state_round_trips_timestamp(tmp_path) -> None:
    state_path = tmp_path / "report-state" / "last-success.json"
    run_at = datetime.fromisoformat("2026-04-15T22:01:02+08:00")

    save_last_successful_run(state_path, run_at)

    assert load_last_successful_run(state_path) == run_at


def test_missing_report_state_returns_none(tmp_path) -> None:
    assert load_last_successful_run(tmp_path / "missing.json") is None


def test_report_state_rejects_naive_timestamp(tmp_path) -> None:
    state_path = tmp_path / "state.json"
    state_path.write_text('{"last_successful_run_at": "2026-04-15T22:00:00"}\n', encoding="utf-8")

    with pytest.raises(ReportStateError, match="must include timezone"):
        load_last_successful_run(state_path)
