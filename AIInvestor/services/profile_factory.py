"""Factory that returns an async UserProfileRepo (Blob or SQLite-wrapped).

Handlers call `await repo.get_or_create(...)` regardless of backend.
- STORAGE_BACKEND=blob → BlobUserProfileRepo (native async)
- STORAGE_BACKEND=sqlite (default) → SqliteAsyncWrapper around the sync
  SQLite implementation, using asyncio.to_thread under the hood
"""

from __future__ import annotations

import asyncio
import logging
from typing import Protocol

from config import Config
from .user_profile import UserProfile, UserProfileRepo

logger = logging.getLogger(__name__)


class AsyncUserProfileRepo(Protocol):
    async def get_or_create(
        self, user_key: str, default_language: str, default_persona: str
    ) -> UserProfile: ...
    async def update(self, user_key: str, **fields) -> UserProfile: ...
    async def get(self, user_key: str) -> UserProfile: ...
    async def delete(self, user_key: str) -> bool: ...


class SqliteAsyncWrapper:
    """Wraps the sync UserProfileRepo so handlers can `await` uniformly."""

    def __init__(self, sync_repo: UserProfileRepo) -> None:
        self._repo = sync_repo

    async def get_or_create(
        self, user_key: str, default_language: str, default_persona: str
    ) -> UserProfile:
        return await asyncio.to_thread(
            self._repo.get_or_create, user_key, default_language, default_persona
        )

    async def update(self, user_key: str, **fields) -> UserProfile:
        return await asyncio.to_thread(self._repo.update, user_key, **fields)

    async def get(self, user_key: str) -> UserProfile:
        return await asyncio.to_thread(self._repo.get, user_key)

    async def delete(self, user_key: str) -> bool:
        return await asyncio.to_thread(self._repo.delete, user_key)


def build_repo(config: Config):
    """Return an async-callable repo (Blob native or SQLite-wrapped)."""
    backend = config.storage_backend
    if backend == "blob":
        if not config.storage_account_name:
            raise RuntimeError(
                "STORAGE_BACKEND=blob requires STORAGE_ACCOUNT_NAME to be set."
            )
        from .user_profile_blob import BlobUserProfileRepo
        account_url = f"https://{config.storage_account_name}.blob.core.windows.net"
        logger.info("Using BlobUserProfileRepo (account=%s)", config.storage_account_name)
        return BlobUserProfileRepo(account_url=account_url, salt=config.user_id_salt)

    # default: sqlite, wrapped for async
    logger.info("Using SqliteAsyncWrapper(UserProfileRepo) at %s", config.sqlite_path)
    sync_repo = UserProfileRepo(db_path=config.sqlite_path, salt=config.user_id_salt)
    return SqliteAsyncWrapper(sync_repo)
