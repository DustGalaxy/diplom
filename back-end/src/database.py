from typing import AsyncGenerator
from uuid import UUID as UUIDTYPE
from datetime import datetime

from uuid6 import uuid7
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as UUIDCOLUMN
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.config import Config

engine = create_async_engine(Config.DB_URL)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


Base = declarative_base()


async def create_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class UUIDMixin:
    id: Mapped[UUIDTYPE] = mapped_column(
        "id",
        UUIDCOLUMN(as_uuid=True),
        primary_key=True,
        default=uuid7,
        unique=True,
        index=True,
        nullable=False,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        sort_order=9999,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        server_default=func.now(),
        server_onupdate=func.now(),
        sort_order=10000,
    )
