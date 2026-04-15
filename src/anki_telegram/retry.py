"""Retry helpers for transient external-service failures."""

from __future__ import annotations

from collections.abc import Callable
import time
from typing import TypeVar


T = TypeVar("T")


def retry(
    operation: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay_seconds: float = 1.0,
    sleeper: Callable[[float], None] | None = None,
    retryable: Callable[[Exception], bool] | None = None,
) -> T:
    last_error: Exception | None = None
    active_sleeper = sleeper or time.sleep
    for attempt_index in range(attempts):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if attempt_index == attempts - 1:
                break
            if retryable is not None and not retryable(exc):
                break
            active_sleeper(base_delay_seconds * (2**attempt_index))

    assert last_error is not None
    raise last_error
