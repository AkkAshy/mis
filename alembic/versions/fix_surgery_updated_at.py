"""fix_surgery_updated_at

Revision ID: fix_surgery_updated_at
Revises: 98cfb58b40be
Create Date: 2025-11-01 10:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_surgery_updated_at'
down_revision: Union[str, Sequence[str], None] = '98cfb58b40be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Изменяем updated_at чтобы он автоматически устанавливался
    op.alter_column('surgeries', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=sa.text('now()'),
               nullable=False)
    
    # Создаем функцию для автоматического обновления updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_surgeries_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Удаляем старый триггер если существует
    op.execute("DROP TRIGGER IF EXISTS update_surgeries_updated_at ON surgeries;")
    
    # Создаем триггер для таблицы surgeries
    op.execute("""
        CREATE TRIGGER update_surgeries_updated_at
            BEFORE UPDATE ON surgeries
            FOR EACH ROW
            EXECUTE FUNCTION update_surgeries_updated_at_column();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем триггер
    op.execute("DROP TRIGGER IF EXISTS update_surgeries_updated_at ON surgeries;")
    
    # Удаляем функцию
    op.execute("DROP FUNCTION IF EXISTS update_surgeries_updated_at_column();")
    
    # Возвращаем старое состояние
    op.alter_column('surgeries', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=None,
               nullable=False)
