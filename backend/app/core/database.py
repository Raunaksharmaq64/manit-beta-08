"""
RIGHT FIT Core — Database Session & Async Engine
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create asynchronous engine
# connect_args={"check_same_thread": False} is required only for SQLite
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False
else:
    connect_args["statement_cache_size"] = 0
    connect_args["prepared_statement_cache_size"] = 0
    connect_args["prepared_statement_name_func"] = lambda: ""
    connect_args["command_timeout"] = 30

engine_kwargs = {
    "echo": False,
    "connect_args": connect_args,
    "pool_pre_ping": False,
    "pool_recycle": 600,
    "future": True,
}
if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs["pool_size"] = 15
    engine_kwargs["max_overflow"] = 25
    engine_kwargs["pool_timeout"] = 30

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Creates all database tables registered with Base.metadata and verifies column migrations."""
    # Ensure all models are imported so Base.metadata contains the complete schema
    import app.db.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Non-destructive migrations for candidate_profiles
        new_columns = [
            ("portfolio_url", "VARCHAR(255)"),
            ("linkedin_url", "VARCHAR(255)"),
            ("github_url", "VARCHAR(255)"),
            ("website_url", "VARCHAR(255)"),
            ("social_links_json", "JSON" if "sqlite" not in settings.DATABASE_URL else "TEXT"),
        ]
        for col, col_type in new_columns:
            try:
                await conn.execute(text(f"ALTER TABLE candidate_profiles ADD COLUMN {col} {col_type}"))
            except Exception:
                pass
