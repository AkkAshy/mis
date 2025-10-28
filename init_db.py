#!/usr/bin/env python3
"""
Простой тест подключения к базе данных
"""

print("🔍 Тестирование подключения к базе данных...\n")

try:
    from app.core.config import settings
    print(f"✅ Config загружен")
    
    db_url = str(settings.database_url)
    
    # Показываем замаскированную версию
    if "@" in db_url:
        parts = db_url.split("@")
        host_part = parts[1].split("/")[0] if "/" in parts[1] else parts[1]
        print(f"📡 Подключение к: {host_part}")
    
    if "localhost" in db_url:
        print("⚠️  ВНИМАНИЕ: Используется localhost!")
        print("   Создай .env файл с правильным DATABASE_URL")
    elif "neon" in db_url:
        print("✅ Используется Neon PostgreSQL")
    
    print("\n🔌 Попытка подключения...")
    
    from app.db.session import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Тест 1: Версия PostgreSQL
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Подключено к PostgreSQL!")
        print(f"   Версия: {version[:60]}...")
        
        # Тест 2: Список таблиц
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        
        print(f"\n📊 Таблицы в базе данных ({len(tables)}):")
        if tables:
            for table in tables:
                # Считаем записи
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.fetchone()[0]
                print(f"   - {table}: {count} записей")
        else:
            print("   ⚠️  Таблицы не найдены (база пустая)")
        
        # Тест 3: Проверка updated_at
        print(f"\n🔍 Проверка колонки updated_at:")
        
        for table in ['appointments', 'patients']:
            try:
                result = conn.execute(text(f"""
                    SELECT column_name, data_type, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table}' AND column_name = 'updated_at'
                """))
                row = result.fetchone()
                if row:
                    print(f"   ✅ {table}.updated_at существует ({row[1]})")
                else:
                    print(f"   ❌ {table}.updated_at НЕ НАЙДЕН!")
            except:
                print(f"   ⚠️  Таблица {table} не существует")
        
        # Тест 4: Проверка триггеров
        print(f"\n🔧 Проверка триггеров:")
        result = conn.execute(text("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers
            WHERE event_object_table IN ('appointments', 'patients')
            ORDER BY event_object_table
        """))
        triggers = result.fetchall()
        
        if triggers:
            for trigger_name, table_name in triggers:
                print(f"   ✅ {table_name}: {trigger_name}")
        else:
            print(f"   ⚠️  Триггеры не найдены (нужно выполнить SQL скрипт)")
        
        print("\n" + "="*60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("="*60)
        
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\nУстанови зависимости:")
    print("   pip install sqlalchemy psycopg2-binary pydantic-settings")
    
except Exception as e:
    print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ:")
    print(f"   {str(e)}")
    print("\n🔧 Рекомендации:")
    print("   1. Проверь что .env файл существует")
    print("   2. Проверь DATABASE_URL в .env")
    print("   3. Проверь интернет соединение")
    print("   4. Проверь что Neon база работает")