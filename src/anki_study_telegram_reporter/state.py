"""Persist report execution state between runs."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path


class ReportStateError(RuntimeError):
    """Raised when report state cannot be read or written."""


def load_last_successful_run(path: Path) -> datetime | None:
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        value = payload.get("last_successful_run_at")
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportStateError(f"Could not read report state: {path}") from exc

    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError as exc:
        raise ReportStateError(f"Report state has invalid last_successful_run_at: {path}") from exc

    if parsed.tzinfo is None:
        raise ReportStateError(f"Report state timestamp must include timezone: {path}")
    return parsed


def save_last_successful_run(path: Path, run_at: datetime) -> None:
    if run_at.tzinfo is None:
        raise ReportStateError("Report run timestamp must include timezone.")

    payload = {"last_successful_run_at": run_at.isoformat()}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ReportStateError(f"Could not write report state: {path}") from exc
