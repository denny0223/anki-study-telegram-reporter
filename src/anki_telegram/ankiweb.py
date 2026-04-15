"""AnkiWeb collection fetching.

This module wraps Anki's sync APIs in one narrow place. The production path
creates a fresh collection, authenticates, downloads into that temporary
workspace, closes the collection, and lets the metrics layer reopen SQLite in
read-only mode.
"""

from __future__ import annotations

from contextlib import redirect_stdout
import io
from pathlib import Path
from typing import Protocol

from anki import sync_pb2
from anki.collection import Collection

from .config import AppConfig


class AnkiWebSyncError(RuntimeError):
    """Raised when AnkiWeb collection sync cannot finish safely."""


class AnkiCollection(Protocol):
    def sync_login(self, username: str, password: str, endpoint: str | None):
        ...

    def sync_status(self, auth):
        ...

    def sync_collection(self, auth, sync_media: bool):
        ...

    def full_upload_or_download(self, *, auth, server_usn: int | None, upload: bool) -> None:
        ...

    def close_for_full_sync(self) -> None:
        ...

    def reopen(self, after_full_sync: bool = False) -> None:
        ...

    def close(self, downgrade: bool = False) -> None:
        ...


def fetch_collection_to_path(
    *,
    config: AppConfig,
    workspace: Path,
    collection_factory=Collection,
) -> Path:
    """Fetch the latest AnkiWeb collection into `workspace`.

    The returned path remains valid only while the caller keeps `workspace`.
    """

    if not config.anki_username or not config.anki_password:
        raise AnkiWebSyncError("Anki credentials are required for AnkiWeb sync.")

    workspace.mkdir(parents=True, exist_ok=True)
    collection_path = workspace / "collection.anki2"
    collection = collection_factory(str(collection_path))

    try:
        with redirect_stdout(io.StringIO()):
            auth = collection.sync_login(config.anki_username, config.anki_password, None)
            status = collection.sync_status(auth)
            if status.new_endpoint:
                auth.endpoint = status.new_endpoint
            _sync_by_required_state(collection, auth, status.required)
    except Exception as exc:
        if isinstance(exc, AnkiWebSyncError):
            raise
        raise AnkiWebSyncError("AnkiWeb collection sync failed.") from exc
    finally:
        _close_collection(collection)

    if not collection_path.exists():
        raise AnkiWebSyncError("AnkiWeb sync finished but no collection file was created.")

    return collection_path


def _sync_by_required_state(collection: AnkiCollection, auth, required: int) -> None:
    if required == sync_pb2.SyncStatusResponse.NO_CHANGES:
        return

    if required in {
        sync_pb2.SyncStatusResponse.NORMAL_SYNC,
        sync_pb2.SyncStatusResponse.FULL_SYNC,
    }:
        output = collection.sync_collection(auth, sync_media=False)
        if output.new_endpoint:
            auth.endpoint = output.new_endpoint
        if output.required in {
            sync_pb2.SyncCollectionResponse.FULL_SYNC,
            sync_pb2.SyncCollectionResponse.FULL_DOWNLOAD,
        }:
            _download_full_collection(collection, auth)
        elif output.required == sync_pb2.SyncCollectionResponse.FULL_UPLOAD:
            raise AnkiWebSyncError("AnkiWeb requested a full upload; refusing to upload from automation.")
        elif output.required not in {
            sync_pb2.SyncCollectionResponse.NO_CHANGES,
            sync_pb2.SyncCollectionResponse.NORMAL_SYNC,
        }:
            raise AnkiWebSyncError(f"Unsupported Anki sync response: {output.required}")
        return

    raise AnkiWebSyncError(f"Unsupported Anki sync status: {required}")


def _download_full_collection(collection: AnkiCollection, auth) -> None:
    collection.close_for_full_sync()
    collection.full_upload_or_download(auth=auth, server_usn=None, upload=False)
    collection.reopen(after_full_sync=True)


def _close_collection(collection: AnkiCollection) -> None:
    try:
        collection.close()
    except Exception:
        pass
