"""init

Revision ID: db4565253ec9
Revises: 
Create Date: 2025-08-22 16:57:21.887345
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'db4565253ec9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Создаём пользователей без active_chat_id
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_activated', sa.Boolean(), nullable=False),
        sa.Column('activation_code', sa.String(length=255), nullable=True),
        sa.Column('activation_code_expires', sa.DateTime(), nullable=True),
        sa.Column('activation_attempts', sa.Integer(), nullable=False),
        sa.Column('refresh_token', sa.String(length=500), nullable=True),
        sa.Column('refresh_token_expires', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Создаём чаты (user_id → users.id)
    op.create_table(
        'cardio_chats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('messages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cardio_chats_id'), 'cardio_chats', ['id'], unique=False)

    # 3. Теперь добавляем active_chat_id в users (FK → cardio_chats.id)
    op.add_column('users', sa.Column('active_chat_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_users_active_chat_id',
        'users', 'cardio_chats',
        ['active_chat_id'], ['id']
    )

    # 4. Анализы
    op.create_table(
        'cardio_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('age', sa.Text(), nullable=False),
        sa.Column('pulse', sa.Text(), nullable=False),
        sa.Column('risk', sa.Text(), nullable=False),
        sa.Column('symptoms', sa.Text(), nullable=False),
        sa.Column('ai_response', sa.Text(), nullable=False),
        sa.Column('cached', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cardio_analyses_id'), 'cardio_analyses', ['id'], unique=False)

    # 5. Прогнозы
    op.create_table(
        'heart_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('age', sa.Text(), nullable=False),
        sa.Column('sex', sa.Text(), nullable=False),
        sa.Column('cp', sa.Text(), nullable=False),
        sa.Column('trestbps', sa.Text(), nullable=False),
        sa.Column('chol', sa.Text(), nullable=False),
        sa.Column('fbs', sa.Text(), nullable=False),
        sa.Column('restecg', sa.Text(), nullable=False),
        sa.Column('thalach', sa.Text(), nullable=False),
        sa.Column('exang', sa.Text(), nullable=False),
        sa.Column('oldpeak', sa.Text(), nullable=False),
        sa.Column('slope', sa.Text(), nullable=False),
        sa.Column('ca', sa.Text(), nullable=False),
        sa.Column('thal', sa.Text(), nullable=False),
        sa.Column('pulse', sa.Text(), nullable=False),
        sa.Column('risk_prediction', sa.Text(), nullable=False),
        sa.Column('probability', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_heart_predictions_id'), 'heart_predictions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_heart_predictions_id'), table_name='heart_predictions')
    op.drop_table('heart_predictions')

    op.drop_index(op.f('ix_cardio_analyses_id'), table_name='cardio_analyses')
    op.drop_table('cardio_analyses')

    op.drop_constraint('fk_users_active_chat_id', 'users', type_='foreignkey')
    op.drop_column('users', 'active_chat_id')

    op.drop_index(op.f('ix_cardio_chats_id'), table_name='cardio_chats')
    op.drop_table('cardio_chats')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
