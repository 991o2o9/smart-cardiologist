"""Add active chat support

Revision ID: 003
Revises: 002_cardio_chat_table
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_cardio_chat_table'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем поле active_chat_id в таблицу users
    op.add_column('users', sa.Column('active_chat_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_active_chat', 'users', 'cardio_chats', ['active_chat_id'], ['id'])
    
    # Добавляем поле is_active в таблицу cardio_chats
    op.add_column('cardio_chats', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade():
    # Удаляем поле is_active из таблицы cardio_chats
    op.drop_column('cardio_chats', 'is_active')
    
    # Удаляем внешний ключ и поле active_chat_id из таблицы users
    op.drop_constraint('fk_users_active_chat', 'users', type_='foreignkey')
    op.drop_column('users', 'active_chat_id')
