"""
Add CardioChat table and remove old CardioAnalysis data
"""
revision = '002_cardio_chat_table'
down_revision = '001'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'cardio_chats',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('messages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    # Удалить все старые данные из cardio_analyses
    op.execute('DELETE FROM cardio_analyses')

def downgrade():
    op.drop_table('cardio_chats')
