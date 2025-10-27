#!/usr/bin/env python3
"""
Быстрое создание таблиц в Neon PostgreSQL
Запустите: python create_tables_quick.py
"""

from sqlalchemy import create_engine, text

# Ваша строка подключения к Neon
DATABASE_URL = "postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-calm-dew-a86c7qwq-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"

def create_tables():
    print("🔧 Создание таблиц в Neon PostgreSQL...")
    print("=" * 80)
    
    engine = create_engine(DATABASE_URL)
    
    sql_commands = [
        # Таблица users
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL
        );
        """,
        "CREATE INDEX IF NOT EXISTS ix_users_id ON users(id);",
        "CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);",
        "CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);",
        
        # Таблица patients
        """
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            patient_uid VARCHAR(255) NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            birth_date DATE NOT NULL,
            gender VARCHAR(20) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            passport VARCHAR(50),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        "CREATE INDEX IF NOT EXISTS ix_patients_id ON patients(id);",
        "CREATE INDEX IF NOT EXISTS ix_patients_patient_uid ON patients(patient_uid);",
        "CREATE INDEX IF NOT EXISTS ix_patients_full_name ON patients(full_name);",
        "CREATE INDEX IF NOT EXISTS ix_patients_phone ON patients(phone);",
        
        # Таблица appointments
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            doctor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
            date TIMESTAMP WITH TIME ZONE,
            status VARCHAR(50) DEFAULT 'scheduled',
            notes TEXT,
            cost NUMERIC(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """,
        "CREATE INDEX IF NOT EXISTS ix_appointments_id ON appointments(id);",
        "CREATE INDEX IF NOT EXISTS ix_appointments_doctor_id ON appointments(doctor_id);",
        "CREATE INDEX IF NOT EXISTS ix_appointments_patient_id ON appointments(patient_id);",
    ]
    
    try:
        with engine.connect() as conn:
            # Проверка подключения
            print("📡 Проверка подключения к базе данных...")
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Подключено! PostgreSQL: {version[:60]}...")
            print()
            
            # Создание таблиц
            print("🔨 Создание таблиц...")
            for i, sql in enumerate(sql_commands, 1):
                conn.execute(text(sql))
                conn.commit()
                print(f"   ✓ Команда {i}/{len(sql_commands)} выполнена")
            
            print()
            print("✅ Все таблицы созданы!")
            print()
            
            # Проверка
            print("📋 Проверка созданных таблиц:")
            result = conn.execute(text("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns 
                        WHERE table_name = t.table_name) as columns
                FROM information_schema.tables t
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            for table, cols in tables:
                print(f"   ✓ {table} ({cols} колонок)")
            
            print()
            print("=" * 80)
            print("✅ ГОТОВО! Теперь попробуйте регистрацию на Vercel")
            print("=" * 80)
            
    except Exception as e:
        print()
        print("❌ ОШИБКА:")
        print(f"   {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print()
    success = create_tables()
    print()
    
    if not success:
        exit(1)