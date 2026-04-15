from datetime import date
from pathlib import Path

from anki import sync_pb2

from anki_telegram.ankiweb import fetch_collection_to_path
from anki_telegram.config import build_config


class FakeStatus:
    def __init__(self, required: int) -> None:
        self.required = required


class FakeSyncOutput:
    def __init__(self, required: int) -> None:
        self.required = required


class FakeCollection:
    instances: list["FakeCollection"] = []

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.calls: list[tuple] = []
        FakeCollection.instances.append(self)

    def sync_login(self, username: str, password: str, endpoint: str | None):
        self.calls.append(("sync_login", username, password, endpoint))
        return object()

    def sync_status(self, auth):
        self.calls.append(("sync_status", auth))
        return FakeStatus(sync_pb2.SyncStatusResponse.FULL_SYNC)

    def sync_collection(self, auth, sync_media: bool):
        self.calls.append(("sync_collection", sync_media))
        return FakeSyncOutput(sync_pb2.SyncStatusResponse.NO_CHANGES)

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
    assert ("full_upload_or_download", None, False) in calls
    assert ("reopen", True) in calls
    assert ("close", False) in calls
