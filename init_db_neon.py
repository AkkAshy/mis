#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных Neon PostgreSQL
Создает все таблицы для Medical Information System
"""

import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.db.base import Base
from app.core.config import settings

def init_database():
    """Инициализация базы данных"""
    print("=" * 80)
    print("🗄️  ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ NEON")
    print("=" * 80)
    print()
    
    # Показываем строку подключения (скрываем пароль)
    db_url = settings.database_url
    if "@" in db_url:
        parts = db_url.split("@")
        user_part = parts[0].split("://")[1].split(":")[0]
        db_url_safe = db_url.replace(parts[0].split("://")[1].split(":")[1], "***")
        print(f"📡 Подключение к: {db_url_safe}")
    else:
        print(f"📡 Подключение к базе данных...")
    
    print()
    
    try:
        # Создаем engine
        print("🔧 Создание engine...")
        engine = create_engine(settings.database_url)
        print("✅ Engine создан")
        print()
        
        # Проверяем подключение
        print("🔍 Проверка подключения...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Подключение успешно!")
            print(f"📊 PostgreSQL версия: {version[:50]}...")
        print()
        
        # Проверяем существующие таблицы
        print("🔍 Проверка существующих таблиц...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            existing_tables = [row[0] for row in result.fetchall()]
            
            if existing_tables:
                print(f"📋 Найдено таблиц: {len(existing_tables)}")
                for table in existing_tables:
                    print(f"   - {table}")
            else:
                print("📋 Таблиц не найдено (база пустая)")
        print()
        
        # Создаем все таблицы
        print("🔨 Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы созданы")
        print()
        
        # Проверяем созданные таблицы
        print("🔍 Проверка созданных таблиц...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"✅ Создано таблиц: {len(tables)}")
                for table in tables:
                    # Получаем количество колонок
                    col_result = conn.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM information_schema.columns 
                        WHERE table_name = '{table[0]}'
                    """))
                    col_count = col_result.fetchone()[0]
                    print(f"   ✓ {table[0]} ({col_count} колонок)")
            else:
                print("⚠️  Таблицы не были созданы")
        
        print()
        print("=" * 80)
        print("✅ БАЗА ДАННЫХ УСПЕШНО ИНИЦИАЛИЗИРОВАНА!")
        print("=" * 80)
        print()
        print("📋 Следующие шаги:")
        print("   1. Задеплойте на Vercel:")
        print("      git add .")
        print("      git commit -m 'Initialize database'")
        print("      git push origin main")
        print()
        print("   2. Попробуйте зарегистрировать пользователя")
        print()
        print("   3. Если нужны миграции Alembic:")
        print("      alembic upgrade head")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ОШИБКА ПРИ ИНИЦИАЛИЗАЦИИ БАЗЫ ДАННЫХ")
        print("=" * 80)
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")
        print()
        
        import traceback
        print("Traceback:")
        print(traceback.format_exc())
        print()
        
        print("🔧 Возможные причины:")
        print("   1. Неверная строка подключения DATABASE_URL")
        print("   2. База данных Neon недоступна")
        print("   3. Недостаточно прав доступа")
        print()
        
        return False
        
    finally:
        try:
            engine.dispose()
        except:
            pass

if __name__ == "__main__":
    print()
    success = init_database()
    print()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)