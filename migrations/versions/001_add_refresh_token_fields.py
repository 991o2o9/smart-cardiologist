"""Add refresh token fields to User model

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Колонки уже существуют, миграция no-op
    pass

def downgrade() -> None:
    # Колонки уже существуют, миграция no-op
    pass
