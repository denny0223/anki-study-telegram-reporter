from datetime import date
from pathlib import Path

from anki import sync_pb2

from anki_study_telegram_reporter.ankiweb import fetch_collection_to_path
from anki_study_telegram_reporter.config import build_config


class FakeStatus:
    def __init__(self, required: int) -> None:
        self.required = required
        self.new_endpoint = ""


class FakeSyncOutput:
    def __init__(self, required: int) -> None:
        self.required = required
        self.new_endpoint = "https://sync.example"


class FakeCollection:
    instances: list["FakeCollection"] = []

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.calls: list[tuple] = []
        FakeCollection.instances.append(self)

    def sync_login(self, username: str, password: str, endpoint: str | None):
        self.calls.append(("sync_login", username, password, endpoint))
        class Auth:
            endpoint = ""

        self.auth = Auth()
        return self.auth

    def sync_status(self, auth):
        self.calls.append(("sync_status", auth))
        return FakeStatus(sync_pb2.SyncStatusResponse.FULL_SYNC)

    def sync_collection(self, auth, sync_media: bool):
        self.calls.append(("sync_collection", sync_media))
        return FakeSyncOutput(sync_pb2.SyncCollectionResponse.FULL_DOWNLOAD)

    def full_upload_or_download(self, *, auth, server_usn: int | None, upload: bool) -> None:
        self.calls.append(("full_upload_or_download", server_usn, upload))
        self.path.write_text("fake collection", encoding="utf-8")

    def close_for_full_sync(self) -> None:
        self.calls.append(("close_for_full_sync",))

    def reopen(self, after_full_sync: bool = False) -> None:
        self.calls.append(("reopen", after_full_sync))

    def close(self, downgrade: bool = False) -> None:
        self.calls.append(("close", downgrade))


def test_fetch_collection_full_sync_downloads_without_upload(tmp_path) -> None:
    FakeCollection.instances = []
    config = build_config(
        source="ankiweb",
        dry_run=True,
        send=False,
        report_date=date(2026, 4, 15),
        env={"ANKI_USERNAME": "user", "ANKI_PASSWORD": "pass"},
        dotenv={},
    )

    collection_path = fetch_collection_to_path(
        config=config,
        workspace=tmp_path,
        collection_factory=FakeCollection,
    )

    assert collection_path == tmp_path / "collection.anki2"
    assert collection_path.exists()
    calls = FakeCollection.instances[0].calls
    assert calls[0] == ("sync_login", "user", "pass", None)
    assert calls[1][0] == "sync_status"
    assert ("sync_collection", False) in calls
    assert ("full_upload_or_download", None, False) in calls
    assert ("reopen", True) in calls
    assert ("close", False) in calls
    assert FakeCollection.instances[0].auth.endpoint == "https://sync.example"


class FlakyCollection(FakeCollection):
    attempts = 0

    def sync_login(self, username: str, password: str, endpoint: str | None):
        FlakyCollection.attempts += 1
        if FlakyCollection.attempts == 1:
            raise RuntimeError("temporary sync outage")
        return super().sync_login(username, password, endpoint)


def test_fetch_collection_retries_transient_sync_errors(tmp_path, monkeypatch) -> None:
    FakeCollection.instances = []
    FlakyCollection.attempts = 0
    monkeypatch.setattr("anki_study_telegram_reporter.retry.time.sleep", lambda _: None)
    config = build_config(
        source="ankiweb",
        dry_run=True,
        send=False,
        report_date=date(2026, 4, 15),
        env={"ANKI_USERNAME": "user", "ANKI_PASSWORD": "pass"},
        dotenv={},
    )

    collection_path = fetch_collection_to_path(
        config=config,
        workspace=tmp_path,
        collection_factory=FlakyCollection,
    )

    assert collection_path.exists()
    assert FlakyCollection.attempts == 2
