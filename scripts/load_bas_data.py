#!/usr/bin/env python3
"""Script to load BAS 2025 v1.0 data into the database."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.rules.bas_dataset import bas_manager
from src.repositories.database import DatabaseRepository
from src.infra.config import get_settings


async def load_bas_data():
    """Load BAS data into the database."""
    settings = get_settings()
    repository = DatabaseRepository(settings.database_url)
    
    # Get current BAS dataset
    dataset = bas_manager.get_current_dataset()
    
    print(f"Loading BAS {dataset.version} with {len(dataset.accounts)} accounts...")
    
    # Load accounts into database
    await repository.load_bas_accounts_from_dataset(
        dataset.accounts, 
        dataset.version
    )
    
    print("✅ BAS data loaded successfully!")
    
    # Verify loading
    for account in dataset.accounts:
        is_valid = await repository.validate_bas_account(account.number, "SE")
        if is_valid:
            print(f"✅ Account {account.number} ({account.name}) validated")
        else:
            print(f"❌ Account {account.number} validation failed")


if __name__ == "__main__":
    asyncio.run(load_bas_data())
