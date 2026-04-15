import pytest

from anki_telegram.retry import retry


def test_retry_eventually_returns() -> None:
    calls = 0
    sleeps = []

    def operation() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise RuntimeError("temporary")
        return "ok"

    assert retry(operation, sleeper=sleeps.append) == "ok"
    assert calls == 3
    assert sleeps == [1.0, 2.0]


def test_retry_stops_on_non_retryable_error() -> None:
    calls = 0

    def operation() -> str:
        nonlocal calls
        calls += 1
        raise ValueError("bad config")

    with pytest.raises(ValueError, match="bad config"):
        retry(operation, sleeper=lambda _: None, retryable=lambda exc: not isinstance(exc, ValueError))

    assert calls == 1
