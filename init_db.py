"""
Скрипт для инициализации базы данных Neon PostgreSQL
Запустите этот скрипт локально перед деплоем на Vercel
"""

import os
import sys
from sqlalchemy import create_engine, text

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.base import Base

def init_database():
    """Инициализация базы данных"""
    print(f"Подключение к базе данных...")
    
    # Создаем engine
    engine = create_engine(settings.database_url)
    
    try:
        # Проверяем подключение
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ Успешное подключение к PostgreSQL")
            print(f"  Версия: {version}")
        
        # Создаем все таблицы
        print("\nСоздание таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✓ Все таблицы успешно созданы")
        
        # Проверяем созданные таблицы
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            print(f"\nСозданные таблицы:")
            for table in tables:
                print(f"  - {table[0]}")
        
        print("\n✓ База данных успешно инициализирована!")
        print("\nТеперь вы можете:")
        print("1. Запустить миграции Alembic (если нужно)")
        print("2. Задеплоить на Vercel")
        
    except Exception as e:
        print(f"\n✗ Ошибка при инициализации базы данных:")
        print(f"  {str(e)}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    init_database()
