"""fix_updated_at_trigger

Revision ID: a1b2c3d4e5f6
Revises: d3289a75a290
Create Date: 2025-10-28 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd3289a75a290'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем функцию для автоматического обновления updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Удаляем старый триггер если существует
    op.execute("DROP TRIGGER IF EXISTS update_appointments_updated_at ON appointments;")
    
    # Создаем триггер для таблицы appointments
    op.execute("""
        CREATE TRIGGER update_appointments_updated_at
            BEFORE UPDATE ON appointments
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Устанавливаем значения для существующих записей
    op.execute("""
        UPDATE appointments 
        SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
        WHERE updated_at IS NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем триггер
    op.execute("DROP TRIGGER IF EXISTS update_appointments_updated_at ON appointments;")
    
    # Удаляем функцию
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")