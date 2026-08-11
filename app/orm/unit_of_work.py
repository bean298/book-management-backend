"""
unit_of_work.py: Unit of Work Pattern

Mission:
1. Define UnitOfWork - manages a single database transaction per HTTP request
2. Auto-create repositories lazily via __getattr__ (cache in _repos)
3. Auto-commit on success, auto-rollback on error via async context manager (__aexit__)
"""

from typing import Callable, Dict

# It used to create a new session for database operations,
# server will call other requests while waiting for database response,
# so we need to use async session to avoid blocking other requests
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

# 1 UnitOfWork = 1 request. When request to API will create a new UnitOfWork,
# in this UnitOfWork will create a new session and all repositories
# After request finish, will UnitOfWork will auto commit or rollback if error, and close session


class UnitOfWork:
    def __init__(
        self,
        db,
        repositories: Dict[str, Callable[[AsyncSession], object]],
    ):
        self._db = db
        self._repo_factories = repositories
        self.session: AsyncSession | None = None
        self._repos = {}

    # Start a new unit of work
    # Auto call __aenter__ when using "async with" statement
    # Start a new session
    async def __aenter__(self):
        self.session = await self._db.session()
        self._repos = {}  # Clear cached repositories for the new session
        return self

    # Get repository by name
    # Push repository to _repose (cache) if not exist: because 1 request can call same repository multiple times
    # Dont need to define every repository in UnitOfWork
    def __getattr__(self, name):
        if name in self._repo_factories:
            if name not in self._repos:
                self._repos[name] = self._repo_factories[name](self.session)
            return self._repos[name]
        raise AttributeError(name)

    #  End the unit of work
    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()

    # Commit the current transaction
    async def commit(self):
        await self.session.commit()

    # Rollback the current transaction
    async def rollback(self):
        await self.session.rollback()
