#!/usr/bin/env python3
"""Script to create database tables directly using SQLAlchemy."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.repositories.database import Base, DatabaseRepository
from src.infra.config import get_settings


async def create_tables():
    """Create all database tables."""
    settings = get_settings()
    repository = DatabaseRepository(settings.database_url)
    
    print("Creating database tables...")
    
    # Create all tables
    async with repository.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
