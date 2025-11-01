# 1. Войти в psql или использовать Python скрипт для удаления таблиц
python3 << 'EOF'
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-calm-dew-a86c7qwq-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Удалить все таблицы
    conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS surgeries CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS appointments CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS patients CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    conn.commit()
    print("✅ Таблицы удалены")
EOF

# 2. Применить миграции заново
alembic upgrade head

# 3. Проверить
alembic current