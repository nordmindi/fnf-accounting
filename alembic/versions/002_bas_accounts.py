"""Add BAS accounts table

Revision ID: 002
Revises: 001
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create bas_accounts table
    op.create_table('bas_accounts',
        sa.Column('number', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('account_class', sa.String(length=10), nullable=False),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        sa.Column('vat_hint', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('allowed_regions', postgresql.ARRAY(sa.String(length=2)), nullable=True),
        sa.Column('bas_version', sa.String(length=20), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('number')
    )
    
    # Create index for faster lookups
    op.create_index('ix_bas_accounts_country_effective', 'bas_accounts', 
                   ['allowed_regions', 'effective_from', 'effective_to'])
    
    # Create index for account class lookups
    op.create_index('ix_bas_accounts_class', 'bas_accounts', ['account_class'])


def downgrade() -> None:
    op.drop_index('ix_bas_accounts_class', table_name='bas_accounts')
    op.drop_index('ix_bas_accounts_country_effective', table_name='bas_accounts')
    op.drop_table('bas_accounts')
