"""Read-only Anki collection metrics extraction."""

from __future__ import annotations

from contextlib import closing
from datetime import date, datetime, time, timezone
import json
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo

from .metrics import StudyMetrics


class CollectionReadError(RuntimeError):
    """Raised when an Anki collection cannot be read."""


def extract_daily_metrics(
    *,
    collection_path: Path,
    report_date: date,
    timezone_name: str | ZoneInfo,
    daily_goal_reviews: int,
    target_decks: tuple[str, ...] = (),
    excluded_decks: tuple[str, ...] = (),
) -> StudyMetrics:
    timezone_info = timezone_name if isinstance(timezone_name, ZoneInfo) else ZoneInfo(timezone_name)
    start_ms, end_ms = _day_bounds_ms(report_date, timezone_info)

    with closing(_connect_read_only(collection_path)) as connection:
        deck_names = _load_deck_names(connection)
        rows = connection.execute(
            """
            select r.ease, r.type, c.did
            from revlog r
            left join cards c on c.id = r.cid
            where r.id >= ? and r.id < ?
            """,
            (start_ms, end_ms),
        ).fetchall()

    filtered_rows = [
        (ease, review_type, deck_names.get(str(deck_id), ""))
        for ease, review_type, deck_id in rows
        if _deck_is_included(deck_names.get(str(deck_id), ""), target_decks, excluded_decks)
    ]

    review_count = len(filtered_rows)
    again_count = sum(1 for ease, _, _ in filtered_rows if ease == 1)
    hard_count = sum(1 for ease, _, _ in filtered_rows if ease == 2)
    good_count = sum(1 for ease, _, _ in filtered_rows if ease == 3)
    easy_count = sum(1 for ease, _, _ in filtered_rows if ease == 4)

    return StudyMetrics(
        report_date=report_date,
        review_count=review_count,
        new_count=sum(1 for _, review_type, _ in filtered_rows if review_type == 0),
        learning_count=sum(1 for _, review_type, _ in filtered_rows if review_type in {0, 2}),
        review_card_count=sum(1 for _, review_type, _ in filtered_rows if review_type == 1),
        again_count=again_count,
        hard_count=hard_count,
        good_count=good_count,
        easy_count=easy_count,
        daily_goal_reviews=daily_goal_reviews,
    )


def _connect_read_only(collection_path: Path) -> sqlite3.Connection:
    if not collection_path.exists():
        raise CollectionReadError(f"Collection not found: {collection_path}")

    uri = f"file:{collection_path}?mode=ro"
    try:
        return sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        raise CollectionReadError(f"Could not open collection read-only: {collection_path}") from exc


def _load_deck_names(connection: sqlite3.Connection) -> dict[str, str]:
    deck_table = connection.execute(
        "select 1 from sqlite_master where type='table' and name='decks'"
    ).fetchone()
    if deck_table:
        rows = connection.execute("select id, name from decks").fetchall()
        return {str(deck_id): str(name) for deck_id, name in rows}

    try:
        row = connection.execute("select decks from col limit 1").fetchone()
    except sqlite3.Error as exc:
        raise CollectionReadError("Could not read deck metadata from collection.") from exc

    if row is None:
        return {}

    try:
        decks = json.loads(row[0])
    except json.JSONDecodeError as exc:
        raise CollectionReadError("Collection deck metadata is invalid JSON.") from exc

    return {str(deck_id): str(deck.get("name", "")) for deck_id, deck in decks.items()}


def _day_bounds_ms(report_date: date, timezone_info: ZoneInfo) -> tuple[int, int]:
    start = datetime.combine(report_date, time.min, tzinfo=timezone_info)
    end = datetime.combine(report_date, time.max, tzinfo=timezone_info)
    start_ms = int(start.astimezone(timezone.utc).timestamp() * 1000)
    end_ms = int(end.astimezone(timezone.utc).timestamp() * 1000) + 1
    return start_ms, end_ms


def _deck_is_included(deck_name: str, target_decks: tuple[str, ...], excluded_decks: tuple[str, ...]) -> bool:
    if excluded_decks and deck_name in excluded_decks:
        return False
    if target_decks and deck_name not in target_decks:
        return False
    return True
