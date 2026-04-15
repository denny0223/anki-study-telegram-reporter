from datetime import date, datetime
import json
import sqlite3
from zoneinfo import ZoneInfo

from anki_telegram.collection import extract_daily_metrics


def test_extract_daily_metrics_from_revlog(tmp_path) -> None:
    collection = tmp_path / "collection.anki2"
    _create_collection(
        collection,
        [
            _review(1, "2026-04-15T00:00:00+08:00", cid=100, ease=1, review_type=0),
            _review(2, "2026-04-15T12:00:00+08:00", cid=101, ease=2, review_type=1),
            _review(3, "2026-04-15T23:59:59+08:00", cid=102, ease=3, review_type=2),
            _review(4, "2026-04-14T23:59:59+08:00", cid=103, ease=4, review_type=1),
            _review(5, "2026-04-16T00:00:00+08:00", cid=104, ease=4, review_type=1),
        ],
    )

    metrics = extract_daily_metrics(
        collection_path=collection,
        report_date=date(2026, 4, 15),
        timezone_name="Asia/Taipei",
        daily_goal_reviews=3,
    )

    assert metrics.review_count == 3
    assert metrics.distinct_card_count == 3
    assert metrics.new_count == 1
    assert metrics.learning_count == 1
    assert metrics.review_card_count == 1
    assert metrics.relearn_count == 0
    assert metrics.again_count == 1
    assert metrics.hard_count == 1
    assert metrics.good_count == 1
    assert metrics.easy_count == 0
    assert metrics.total_card_count == 5
    assert metrics.started_card_count == 5
    assert metrics.goal_met is True


def test_extract_daily_metrics_filters_decks(tmp_path) -> None:
    collection = tmp_path / "collection.anki2"
    _create_collection(
        collection,
        [
            _review(1, "2026-04-15T08:00:00+08:00", cid=100, ease=3, review_type=1),
            _review(2, "2026-04-15T09:00:00+08:00", cid=200, ease=1, review_type=1),
            _review(3, "2026-04-15T10:00:00+08:00", cid=300, ease=4, review_type=1),
        ],
        cards={100: 10, 200: 20, 300: 30},
        decks={"10": "Japanese", "20": "English", "30": "Ignored"},
    )

    metrics = extract_daily_metrics(
        collection_path=collection,
        report_date=date(2026, 4, 15),
        timezone_name=ZoneInfo("Asia/Taipei"),
        daily_goal_reviews=10,
        target_decks=("Japanese", "English"),
        excluded_decks=("English",),
    )

    assert metrics.review_count == 1
    assert metrics.good_count == 1
    assert metrics.again_count == 0


def test_extract_daily_metrics_separates_relearning_type(tmp_path) -> None:
    collection = tmp_path / "collection.anki2"
    _create_collection(
        collection,
        [
            _review(1, "2026-04-15T08:00:00+08:00", cid=100, ease=1, review_type=3),
            _review(2, "2026-04-15T09:00:00+08:00", cid=101, ease=3, review_type=2),
        ],
    )

    metrics = extract_daily_metrics(
        collection_path=collection,
        report_date=date(2026, 4, 15),
        timezone_name="Asia/Taipei",
        daily_goal_reviews=10,
    )

    assert metrics.relearn_count == 1
    assert metrics.learning_count == 1
    assert metrics.new_count == 0


def test_extract_daily_metrics_reads_newer_decks_table(tmp_path) -> None:
    collection = tmp_path / "collection.anki2"
    _create_collection(
        collection,
        [
            _review(1, "2026-04-15T08:00:00+08:00", cid=100, ease=3, review_type=1),
            _review(2, "2026-04-15T09:00:00+08:00", cid=200, ease=4, review_type=1),
        ],
        cards={100: 10, 200: 20},
        decks={"10": "Legacy Empty"},
        newer_decks={10: "Japanese", 20: "English"},
    )

    metrics = extract_daily_metrics(
        collection_path=collection,
        report_date=date(2026, 4, 15),
        timezone_name="Asia/Taipei",
        daily_goal_reviews=10,
        target_decks=("English",),
    )

    assert metrics.review_count == 1
    assert metrics.easy_count == 1


def _create_collection(
    path,
    reviews: list[tuple[int, int, int, int]],
    cards: dict[int, int] | None = None,
    decks: dict[str, str] | None = None,
    newer_decks: dict[int, str] | None = None,
) -> None:
    cards = cards or {100: 10, 101: 10, 102: 10, 103: 10, 104: 10}
    decks = decks or {"10": "Default"}

    connection = sqlite3.connect(path)
    try:
        connection.execute("create table col (decks text not null)")
        connection.execute("create table cards (id integer primary key, did integer not null)")
        connection.execute("create table revlog (id integer primary key, cid integer not null, ease integer not null, type integer not null)")
        if newer_decks is not None:
            connection.execute("create table decks (id integer primary key, name text not null)")
        connection.execute(
            "insert into col (decks) values (?)",
            (json.dumps({deck_id: {"name": name} for deck_id, name in decks.items()}),),
        )
        connection.executemany("insert into cards (id, did) values (?, ?)", cards.items())
        connection.executemany("insert into revlog (id, cid, ease, type) values (?, ?, ?, ?)", reviews)
        if newer_decks is not None:
            connection.executemany("insert into decks (id, name) values (?, ?)", newer_decks.items())
        connection.commit()
    finally:
        connection.close()


def _review(row_id: int, timestamp: str, *, cid: int, ease: int, review_type: int) -> tuple[int, int, int, int]:
    del row_id
    review_id = int(datetime.fromisoformat(timestamp).timestamp() * 1000)
    return review_id, cid, ease, review_type
