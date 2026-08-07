"""
postgres.py: PostgreSQL Database Connection & ORM Base

Mission:
1. Define DBContext abstract class - the contract for all database backends
2. Define Base (DeclarativeBase) - the base class for all SQLAlchemy models
3. Implement PostgresDBContext - concrete PostgreSQL connection manager with connection pooling
4. Define AppBaseMixin - reusable mixin providing common fields (created_at, updated_at, object_status)
"""

from typing import AsyncGenerator, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import AsyncGenerator
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text, String, DateTime
from datetime import datetime, timezone
from app.enum.common import OBJECT_STATUS


# Abstract base class for database context
class DBContext(ABC):

    @abstractmethod
    async def session(self) -> AsyncGenerator[AsyncSession, None]: ...

    @abstractmethod
    async def healthcheck(self) -> bool: ...

    @abstractmethod
    async def close(self) -> None: ...


# Main base class for SQLAlchemy models
# All models should inherit from this base class so
# 1. Auto map models to database tables
# 2. Resgiter all models into metadata
class Base(DeclarativeBase):
    pass


# Connect to Postgres database
class PostgresDBContext(DBContext):
    def __init__(
        self,
        connection_string: str,  # db connection string
        echo: bool = False,  # log SQL
        pool_size: int = 10,  # min of connections in pool
        max_overflow: int = 20,  # max of connections in pool
    ):
        self.engine = create_async_engine(
            connection_string,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        # Create a sessionmaker for creating new sessions
        self._sessionmaker = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )

    # Get a new session for database operations
    async def session(self) -> AsyncSession:
        return self._sessionmaker()

    # Healthcheck method to check if the database connection is alive
    async def healthcheck(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    # Close the database connection
    async def close(self) -> None:
        await self.engine.dispose()


# Class to add common fields to all models
class AppBaseMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now().astimezone(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now().astimezone(timezone.utc),
    )

    object_status: Mapped[str] = mapped_column(
        String(20),
        default=OBJECT_STATUS.ACTIVE.value,
    )
