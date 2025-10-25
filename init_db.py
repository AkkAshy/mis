#!/usr/bin/env python3
"""
Проверка что сохранено в базе данных
Показывает пользователей и их хеши
"""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-calm-dew-a86c7qwq-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"

def check_users():
    print("=" * 80)
    print("👥 ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ В БАЗЕ ДАННЫХ")
    print("=" * 80)
    print()
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Получаем всех пользователей
            result = conn.execute(text("""
                SELECT id, username, email, role, 
                       LENGTH(hashed_password) as hash_length,
                       LEFT(hashed_password, 30) as hash_start
                FROM users
                ORDER BY id
            """))
            
            users = result.fetchall()
            
            if not users:
                print("⚠️  База данных пустая - пользователей нет")
                print()
                print("Попробуйте зарегистрировать пользователя:")
                print()
                print('curl -X POST https://mis-pied.vercel.app/auth/register \\')
                print('  -H "Content-Type: application/json" \\')
                print('  -d \'{')
                print('    "username": "testuser",')
                print('    "full_name": "Test User",')
                print('    "email": "test@example.com",')
                print('    "password": "admin123",')
                print('    "role": "reception"')
                print('  }\'')
                print()
            else:
                print(f"✅ Найдено пользователей: {len(users)}")
                print()
                
                for user in users:
                    user_id, username, email, role, hash_len, hash_start = user
                    print(f"ID: {user_id}")
                    print(f"   Username: {username}")
                    print(f"   Email: {email}")
                    print(f"   Role: {role}")
                    print(f"   Hash length: {hash_len} символов")
                    print(f"   Hash (first 30): {hash_start}...")
                    print()
                
                print("=" * 80)
                print("🔍 АНАЛИЗ")
                print("=" * 80)
                print()
                
                # Проверяем длину хеша
                if users[0][4] < 50:
                    print("⚠️  ПРОБЛЕМА: Хеш слишком короткий!")
                    print("   Argon2 хеш должен быть ~90+ символов")
                    print("   У вас: {} символов".format(users[0][4]))
                    print()
                    print("❌ Возможно пароль не был захеширован правильно")
                    print()
                elif users[0][5].startswith("$argon2"):
                    print("✅ Хеш выглядит правильно (Argon2)")
                    print()
                    print("🔍 Если логин не работает, проблема может быть в:")
                    print("   1. Вы вводите неправильный пароль")
                    print("   2. Проблема с verify_password функцией")
                    print("   3. Проблема с передачей пароля в JSON")
                    print()
                else:
                    print("⚠️  Хеш не похож на Argon2")
                    print(f"   Начинается с: {users[0][5][:10]}")
                    print()
                
                print("📋 Для тестирования:")
                print(f"   Username: {users[0][1]}")
                print("   Password: [тот что вы использовали при регистрации]")
                print()
                print("Команда для логина:")
                print()
                print('curl -X POST https://mis-pied.vercel.app/auth/login \\')
                print('  -H "Content-Type: application/json" \\')
                print(f'  -d \'{{"username": "{users[0][1]}", "password": "YOUR_PASSWORD"}}\'')
                print()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print()
    check_users()
    print()