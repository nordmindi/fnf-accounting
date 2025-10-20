"""Database initialization and configuration."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.repositories.database import Base


async def init_db(database_url: str) -> None:
    """Initialize database connection and create tables."""
    # Convert sync URL to async URL
    if database_url.startswith("postgresql://"):
        async_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        async_url = database_url

    # Create async engine
    engine = create_async_engine(
        async_url,
        echo=False,  # Set to True for SQL logging
        future=True
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    return async_session
