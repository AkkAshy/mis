#!/bin/bash

# 🔙 Скрипт для отката логирования
# Использование: ./disable_logging.sh

set -e

echo "🔙 Откат изменений (удаление детального логирования)"
echo "====================================================="
echo ""

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка наличия резервных копий
if [ ! -f "app/routes/auth.py.backup" ]; then
    echo -e "${RED}❌ Резервная копия app/routes/auth.py.backup не найдена${NC}"
    echo "   Возможно, логирование еще не было включено"
    exit 1
fi

if [ ! -f "app/core/security.py.backup" ]; then
    echo -e "${RED}❌ Резервная копия app/core/security.py.backup не найдена${NC}"
    echo "   Возможно, логирование еще не было включено"
    exit 1
fi

# Восстановление файлов
echo "🔄 Восстановление оригинальных файлов..."

cp app/routes/auth.py.backup app/routes/auth.py
echo -e "${GREEN}✓ Восстановлен: app/routes/auth.py${NC}"

cp app/core/security.py.backup app/core/security.py
echo -e "${GREEN}✓ Восстановлен: app/core/security.py${NC}"

echo ""

# Удаление резервных копий (опционально)
read -p "Удалить резервные копии? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm app/routes/auth.py.backup
    rm app/core/security.py.backup
    echo -e "${GREEN}✓ Резервные копии удалены${NC}"
fi

echo ""

# Git
echo "📝 Подготовка к коммиту..."
git add app/routes/auth.py app/core/security.py

echo ""
echo -e "${GREEN}✅ Оригинальные файлы восстановлены!${NC}"
echo ""
echo "📋 Следующие шаги:"
echo "  1. Закоммитьте изменения:"
echo "     ${YELLOW}git commit -m 'Remove detailed logging'${NC}"
echo ""
echo "  2. Задеплойте на Vercel:"
echo "     ${YELLOW}git push origin main${NC}"
echo ""
