#!/usr/bin/env python3
"""
🔧 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С ALEMBIC
Синхронизирует строки подключения в alembic.ini и app/core/config.py
"""

import os
import re
import shutil
from datetime import datetime

# Цвета
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*80}")
    print(f"{text}")
    print(f"{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def backup_file(filepath):
    """Создать резервную копию файла"""
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{filepath}.backup_{timestamp}"
        shutil.copy2(filepath, backup_path)
        print_success(f"Создана резервная копия: {backup_path}")
        return backup_path
    return None

def extract_database_url(filepath):
    """Извлечь DATABASE_URL из файла"""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Паттерн для поиска DATABASE_URL
    patterns = [
        r'database_url[:\s]*str\s*=\s*["\']([^"\']+)["\']',  # Python config
        r'sqlalchemy\.url\s*=\s*(.+)',  # alembic.ini
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            url = match.group(1).strip()
            return url
    
    return None

def update_alembic_ini(new_database_url):
    """Обновить DATABASE_URL в alembic.ini"""
    if not os.path.exists('alembic.ini'):
        print_error("Файл alembic.ini не найден!")
        return False
    
    # Создать резервную копию
    backup_file('alembic.ini')
    
    # Прочитать содержимое
    with open('alembic.ini', 'r') as f:
        content = f.read()
    
    # Заменить строку подключения
    new_content = re.sub(
        r'(sqlalchemy\.url\s*=\s*)(.+)',
        f'\\1{new_database_url}',
        content
    )
    
    # Записать обратно
    with open('alembic.ini', 'w') as f:
        f.write(new_content)
    
    print_success("Файл alembic.ini обновлен!")
    return True

def update_config_py(new_database_url):
    """Обновить DATABASE_URL в app/core/config.py"""
    if not os.path.exists('app/core/config.py'):
        print_error("Файл app/core/config.py не найден!")
        return False
    
    # Создать резервную копию
    backup_file('app/core/config.py')
    
    # Прочитать содержимое
    with open('app/core/config.py', 'r') as f:
        content = f.read()
    
    # Заменить строку подключения
    new_content = re.sub(
        r'(database_url:\s*str\s*=\s*["\'])([^"\']+)(["\'])',
        f'\\1{new_database_url}\\3',
        content
    )
    
    # Записать обратно
    with open('app/core/config.py', 'w') as f:
        f.write(new_content)
    
    print_success("Файл app/core/config.py обновлен!")
    return True

def main():
    print_header("🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С ALEMBIC И NEON POSTGRESQL")
    
    print_info("Анализирую текущие настройки...\n")
    
    # 1. Извлечь DATABASE_URL из обоих файлов
    alembic_url = extract_database_url('alembic.ini')
    config_url = extract_database_url('app/core/config.py')
    
    print(f"{Colors.BLUE}📋 ТЕКУЩИЕ НАСТРОЙКИ:{Colors.END}")
    print(f"\n1️⃣  alembic.ini:")
    if alembic_url:
        print(f"   {alembic_url[:80]}...")
        if 'ep-proud-art' in alembic_url:
            print(f"   {Colors.RED}❌ СТАРАЯ БД (ep-proud-art){Colors.END}")
        elif 'ep-calm-dew' in alembic_url:
            print(f"   {Colors.GREEN}✅ НОВАЯ БД (ep-calm-dew){Colors.END}")
    else:
        print(f"   {Colors.RED}Не найдено{Colors.END}")
    
    print(f"\n2️⃣  app/core/config.py:")
    if config_url:
        print(f"   {config_url[:80]}...")
        if 'ep-proud-art' in config_url:
            print(f"   {Colors.RED}❌ СТАРАЯ БД (ep-proud-art){Colors.END}")
        elif 'ep-calm-dew' in config_url:
            print(f"   {Colors.GREEN}✅ НОВАЯ БД (ep-calm-dew){Colors.END}")
    else:
        print(f"   {Colors.RED}Не найдено{Colors.END}")
    
    # 2. Определить, какую БД использовать
    print(f"\n{Colors.YELLOW}{'='*80}{Colors.END}")
    
    if not alembic_url or not config_url:
        print_error("Не удалось найти строки подключения!")
        return
    
    # Проверка на несоответствие
    if alembic_url != config_url:
        print_warning("ОБНАРУЖЕНО НЕСООТВЕТСТВИЕ!")
        print_info("alembic.ini и app/core/config.py используют РАЗНЫЕ базы данных")
        print()
        
        # Определить, какую БД использовать
        print(f"{Colors.CYAN}Какую базу данных использовать?{Colors.END}")
        print(f"  1) НОВУЮ БД (ep-calm-dew) - рекомендуется")
        print(f"  2) СТАРУЮ БД (ep-proud-art)")
        print(f"  3) Ввести вручную")
        print(f"  4) Отмена")
        
        choice = input(f"\n{Colors.YELLOW}Ваш выбор (1-4): {Colors.END}").strip()
        
        if choice == '1':
            # Использовать новую БД
            if 'ep-calm-dew' in config_url:
                target_url = config_url
                print_info("Будет использована новая БД из app/core/config.py")
            else:
                target_url = "postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-calm-dew-a86c7qwq-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
                print_info("Будет использована новая БД (введена вручную)")
        
        elif choice == '2':
            # Использовать старую БД
            if 'ep-proud-art' in alembic_url:
                target_url = alembic_url
                print_info("Будет использована старая БД из alembic.ini")
            else:
                target_url = "postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-proud-art-a8xtxs9t-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
                print_info("Будет использована старая БД (введена вручную)")
        
        elif choice == '3':
            # Ввести вручную
            print()
            target_url = input(f"{Colors.YELLOW}Введите DATABASE_URL: {Colors.END}").strip()
            if not target_url:
                print_error("URL не введен. Отмена.")
                return
        
        else:
            print_info("Отмена операции")
            return
        
        # Обновить оба файла
        print()
        print_header("📝 ОБНОВЛЕНИЕ ФАЙЛОВ")
        
        update_alembic_ini(target_url)
        update_config_py(target_url)
        
        print()
        print_success("Файлы синхронизированы!")
        print_info(f"Используется: {target_url[:60]}...")
        
    else:
        print_success("Файлы уже синхронизированы!")
        print_info(f"Используется: {alembic_url[:60]}...")
    
    # 3. Показать следующие шаги
    print()
    print_header("📋 СЛЕДУЮЩИЕ ШАГИ")
    print("""
1️⃣  Проверьте изменения:
   git diff alembic.ini
   git diff app/core/config.py

2️⃣  Примените миграции:
   alembic upgrade head

3️⃣  Проверьте текущую версию:
   alembic current

4️⃣  Если нужно, создайте новую миграцию:
   alembic revision --autogenerate -m "описание"

5️⃣  Закоммитьте изменения:
   git add alembic.ini app/core/config.py
   git commit -m "Fix: sync database URLs in alembic.ini and config.py"
   git push origin main
    """)
    
    print_header("✅ ГОТОВО!")

if __name__ == "__main__":
    main()
