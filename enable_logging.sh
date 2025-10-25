#!/bin/bash

# 🔍 Скрипт для добавления логирования в проект
# Использование: ./enable_logging.sh

set -e

echo "🔍 Добавление детального логирования для отладки"
echo "=================================================="
echo ""

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка наличия исходных файлов
if [ ! -f "app/routes/auth_with_logging.py" ]; then
    echo -e "${RED}❌ Файл app/routes/auth_with_logging.py не найден${NC}"
    exit 1
fi

if [ ! -f "app/core/security_with_logging.py" ]; then
    echo -e "${RED}❌ Файл app/core/security_with_logging.py не найден${NC}"
    exit 1
fi

# Создание резервных копий
echo "📦 Создание резервных копий..."

if [ -f "app/routes/auth.py" ]; then
    cp app/routes/auth.py app/routes/auth.py.backup
    echo -e "${GREEN}✓ Создана резервная копия: app/routes/auth.py.backup${NC}"
else
    echo -e "${YELLOW}⚠ Файл app/routes/auth.py не найден${NC}"
fi

if [ -f "app/core/security.py" ]; then
    cp app/core/security.py app/core/security.py.backup
    echo -e "${GREEN}✓ Создана резервная копия: app/core/security.py.backup${NC}"
else
    echo -e "${YELLOW}⚠ Файл app/core/security.py не найден${NC}"
fi

echo ""

# Замена файлов
echo "🔄 Замена файлов на версии с логированием..."

cp app/routes/auth_with_logging.py app/routes/auth.py
echo -e "${GREEN}✓ Заменен: app/routes/auth.py${NC}"

cp app/core/security_with_logging.py app/core/security.py
echo -e "${GREEN}✓ Заменен: app/core/security.py${NC}"

echo ""

# Git
echo "📝 Подготовка к коммиту..."
git add app/routes/auth.py app/core/security.py

echo ""
echo -e "${GREEN}✅ Логирование успешно добавлено!${NC}"
echo ""
echo "📋 Следующие шаги:"
echo "  1. Закоммитьте изменения:"
echo "     ${YELLOW}git commit -m 'Add detailed logging for debugging'${NC}"
echo ""
echo "  2. Задеплойте на Vercel:"
echo "     ${YELLOW}git push origin main${NC}"
echo ""
echo "  3. Попробуйте зарегистрировать пользователя"
echo ""
echo "  4. Проверьте логи в Vercel Dashboard:"
echo "     Deployments → Latest → View Function Logs"
echo ""
echo "  5. Найдите строки с 🔵 и ❌ для отладки"
echo ""
echo "💡 Для отката изменений:"
echo "   ${YELLOW}./disable_logging.sh${NC}"
echo ""
