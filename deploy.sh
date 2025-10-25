#!/bin/bash

# 🚀 Quick Deploy Script для Vercel + Neon PostgreSQL
# Этот скрипт автоматизирует основные шаги деплоя

set -e  # Exit on error

echo "🚀 Medical Information System - Quick Deploy"
echo "=============================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода успеха
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Функция для вывода предупреждения
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Функция для вывода ошибки
error() {
    echo -e "${RED}✗ $1${NC}"
}

# Шаг 1: Проверка зависимостей
echo "📦 Шаг 1: Проверка зависимостей..."

if ! command -v python3 &> /dev/null; then
    error "Python3 не установлен"
    exit 1
fi
success "Python3 установлен"

if ! command -v git &> /dev/null; then
    error "Git не установлен"
    exit 1
fi
success "Git установлен"

if ! command -v npm &> /dev/null; then
    warning "NPM не установлен - установите для использования Vercel CLI"
else
    success "NPM установлен"
fi

echo ""

# Шаг 2: Установка Python зависимостей
echo "📦 Шаг 2: Установка Python зависимостей..."
pip install -r requirements.txt > /dev/null 2>&1
success "Зависимости установлены"
echo ""

# Шаг 3: Проверка подключения к базе данных
echo "🗄️ Шаг 3: Проверка подключения к Neon PostgreSQL..."
if python3 init_db.py; then
    success "База данных инициализирована"
else
    error "Не удалось подключиться к базе данных"
    echo ""
    echo "Проверьте:"
    echo "  1. Правильность строки подключения в alembic.ini"
    echo "  2. Доступность базы данных Neon"
    exit 1
fi
echo ""

# Шаг 4: Применение миграций
echo "🔄 Шаг 4: Применение миграций Alembic..."
if alembic upgrade head; then
    success "Миграции применены"
else
    warning "Возможно, миграции уже применены или произошла ошибка"
fi
echo ""

# Шаг 5: Инициализация Git (если нужно)
echo "📝 Шаг 5: Проверка Git репозитория..."
if [ -d .git ]; then
    success "Git репозиторий уже инициализирован"
else
    git init
    git add .
    git commit -m "Initial commit - Medical Information System"
    success "Git репозиторий инициализирован"
fi
echo ""

# Шаг 6: Vercel
echo "☁️ Шаг 6: Деплой на Vercel..."
if command -v vercel &> /dev/null; then
    echo "Выберите опцию:"
    echo "  1) Деплой через Vercel CLI (требуется vercel login)"
    echo "  2) Пропустить (задеплоить вручную через vercel.com)"
    read -p "Ваш выбор (1 или 2): " choice
    
    if [ "$choice" = "1" ]; then
        echo ""
        warning "Убедитесь, что вы залогинены: vercel login"
        echo ""
        echo "Не забудьте добавить Environment Variables в Vercel Dashboard:"
        echo "  - DATABASE_URL"
        echo "  - SECRET_KEY"
        echo "  - ALGORITHM"
        echo "  - ACCESS_TOKEN_EXPIRE_MINUTES"
        echo ""
        read -p "Продолжить деплой? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            vercel --prod
            success "Деплой запущен!"
        fi
    else
        echo ""
        echo "Для ручного деплоя:"
        echo "  1. Создайте репозиторий на GitHub"
        echo "  2. Push код: git remote add origin <your-repo-url>"
        echo "  3. Зайдите на vercel.com и импортируйте проект"
        echo "  4. Настройте Environment Variables"
    fi
else
    echo ""
    echo "Vercel CLI не установлен."
    echo ""
    echo "Для установки:"
    echo "  npm i -g vercel"
    echo ""
    echo "Или задеплойте вручную через vercel.com:"
    echo "  1. Создайте репозиторий на GitHub"
    echo "  2. Push код: git remote add origin <your-repo-url>"
    echo "  3. Импортируйте проект на vercel.com"
fi
echo ""

# Финальные инструкции
echo "🎉 Подготовка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "  1. ⚠️ Сгенерируйте новый SECRET_KEY для продакшена:"
echo "     python -c \"import secrets; print(secrets.token_urlsafe(32))\""
echo ""
echo "  2. 🔐 Добавьте Environment Variables в Vercel Dashboard:"
echo "     - DATABASE_URL: postgresql://neondb_owner:npg_...@ep-proud-art...neon.tech/neondb?sslmode=require"
echo "     - SECRET_KEY: <ваш новый секретный ключ>"
echo "     - ALGORITHM: HS256"
echo "     - ACCESS_TOKEN_EXPIRE_MINUTES: 30"
echo ""
echo "  3. 🚀 Push на GitHub (если еще не сделано):"
echo "     git remote add origin https://github.com/username/repo.git"
echo "     git push -u origin main"
echo ""
echo "  4. 🌐 Импортируйте проект на vercel.com"
echo ""
echo "📖 Полное руководство: см. DEPLOYMENT_GUIDE.md"
echo ""
success "Готово к деплою!"
