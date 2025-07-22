"""cria tabela memory_digi

Revision ID: 33e8fa4af35f
Revises: 
Create Date: 2025-07-22 11:17:49.466984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '33e8fa4af35f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    print("🚀 Iniciando migration: criando tabela memory_digi...")
    op.create_table(
        'memory_digi',
        sa.Column('memory_id', postgresql.UUID(as_uuid=True), primary_key=True, unique=True, nullable=False),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('memory_data', sa.JSON, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    print("✅ Tabela memory_digi criada com sucesso!")


def downgrade() -> None:
    """Downgrade schema."""
    print("⚠️ Removendo tabela memory_digi...")
    op.drop_table('memory_digi')
    print("🗑️ Tabela memory_digi removida!")
