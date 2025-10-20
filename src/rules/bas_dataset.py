"""BAS (Kontoplan) dataset management for Swedish accounting compliance."""

import json
from datetime import date

from pydantic import BaseModel, Field


class BASAccount(BaseModel):
    """BAS account definition."""
    number: str = Field(..., description="Account number (e.g., '6071')")
    name: str = Field(..., description="Account name (e.g., 'Representation')")
    account_class: str = Field(..., description="Account class (e.g., '60')")
    account_type: str = Field(..., description="Account type (expense, income, asset, liability)")
    vat_hint: float | None = Field(None, description="Suggested VAT rate")
    allowed_regions: list[str] = Field(default_factory=list, description="Allowed regions (e.g., ['SE'])")
    description: str | None = Field(None, description="Account description")


class BASDataset(BaseModel):
    """BAS dataset with versioning."""
    version: str = Field(..., description="BAS version (e.g., '2025_v1.0')")
    effective_from: date = Field(..., description="Effective date")
    effective_to: date | None = Field(None, description="End date (if applicable)")
    accounts: list[BASAccount] = Field(..., description="List of BAS accounts")

    def get_account(self, number: str) -> BASAccount | None:
        """Get account by number."""
        for account in self.accounts:
            if account.number == number:
                return account
        return None

    def get_accounts_by_class(self, account_class: str) -> list[BASAccount]:
        """Get all accounts in a specific class."""
        return [acc for acc in self.accounts if acc.account_class == account_class]

    def get_accounts_by_type(self, account_type: str) -> list[BASAccount]:
        """Get all accounts of a specific type."""
        return [acc for acc in self.accounts if acc.account_type == account_type]

    def validate_account(self, number: str, region: str = "SE") -> bool:
        """Validate if account exists and is allowed for region."""
        account = self.get_account(number)
        if not account:
            return False

        if account.allowed_regions and region not in account.allowed_regions:
            return False

        return True


class BASManager:
    """Manages BAS datasets and validation."""

    def __init__(self, bas_data_path: str | None = None):
        """Initialize BAS manager."""
        self.bas_data_path = bas_data_path or "src/rules/bas_datasets"
        self._current_dataset: BASDataset | None = None
        self._load_default_dataset()

    def _load_default_dataset(self) -> None:
        """Load the default BAS 2025 v1.0 dataset."""
        # Create default BAS dataset with the accounts we're currently using
        default_accounts = [
            BASAccount(
                number="6071",
                name="Representation",
                account_class="60",
                account_type="expense",
                vat_hint=12.0,
                allowed_regions=["SE"],
                description="Representation meals and entertainment"
            ),
            BASAccount(
                number="2641",
                name="Moms på representation",
                account_class="26",
                account_type="liability",
                vat_hint=12.0,
                allowed_regions=["SE"],
                description="VAT on representation expenses"
            ),
            BASAccount(
                number="6540",
                name="Transportkostnader",
                account_class="65",
                account_type="expense",
                vat_hint=25.0,
                allowed_regions=["SE"],
                description="Transport and travel expenses"
            ),
            BASAccount(
                number="2640",
                name="Moms på varor och tjänster",
                account_class="26",
                account_type="liability",
                vat_hint=25.0,
                allowed_regions=["SE"],
                description="VAT on goods and services"
            ),
            BASAccount(
                number="6541",
                name="Programvaror och datatjänster",
                account_class="65",
                account_type="expense",
                vat_hint=25.0,
                allowed_regions=["SE"],
                description="Software and data services"
            ),
            BASAccount(
                number="1930",
                name="Kassa och bank",
                account_class="19",
                account_type="asset",
                vat_hint=None,
                allowed_regions=["SE"],
                description="Cash and bank accounts"
            ),
        ]

        self._current_dataset = BASDataset(
            version="2025_v1.0",
            effective_from=date(2025, 1, 1),
            accounts=default_accounts
        )

    def get_current_dataset(self) -> BASDataset:
        """Get the current BAS dataset."""
        if not self._current_dataset:
            self._load_default_dataset()
        return self._current_dataset

    def validate_account(self, account_number: str, region: str = "SE") -> bool:
        """Validate account against current BAS dataset."""
        dataset = self.get_current_dataset()
        return dataset.validate_account(account_number, region)

    def get_account_info(self, account_number: str) -> BASAccount | None:
        """Get account information."""
        dataset = self.get_current_dataset()
        return dataset.get_account(account_number)

    def load_dataset_from_file(self, file_path: str) -> BASDataset:
        """Load BAS dataset from JSON file."""
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)

        accounts = [BASAccount(**acc) for acc in data['accounts']]
        return BASDataset(
            version=data['version'],
            effective_from=date.fromisoformat(data['effective_from']),
            effective_to=date.fromisoformat(data['effective_to']) if data.get('effective_to') else None,
            accounts=accounts
        )

    def save_dataset_to_file(self, dataset: BASDataset, file_path: str) -> None:
        """Save BAS dataset to JSON file."""
        data = {
            'version': dataset.version,
            'effective_from': dataset.effective_from.isoformat(),
            'effective_to': dataset.effective_to.isoformat() if dataset.effective_to else None,
            'accounts': [acc.dict() for acc in dataset.accounts]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Global BAS manager instance
bas_manager = BASManager()


def validate_bas_account(account_number: str, region: str = "SE") -> bool:
    """Validate account against BAS dataset."""
    return bas_manager.validate_account(account_number, region)


def get_bas_account_info(account_number: str) -> BASAccount | None:
    """Get BAS account information."""
    return bas_manager.get_account_info(account_number)
