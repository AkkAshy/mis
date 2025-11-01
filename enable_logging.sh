#!/bin/bash

# 🔧 Быстрое исправление ошибки Surgery updated_at
# Использование: ./quick_fix_surgery.sh

set -e

echo "🔧 ИСПРАВЛЕНИЕ ОШИБКИ: Surgery updated_at"
echo "========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Шаг 1: Бэкап
echo "📦 Шаг 1: Создание бэкапа..."
if [ -f "app/models/surgery.py" ]; then
    cp app/models/surgery.py app/models/surgery.py.backup
    echo -e "${GREEN}✓ Бэкап создан: app/models/surgery.py.backup${NC}"
else
    echo -e "${RED}✗ Файл app/models/surgery.py не найден${NC}"
    exit 1
fi
echo ""

# Шаг 2: Замена строки в файле
echo "🔄 Шаг 2: Обновление модели Surgery..."

# Используем sed для замены
sed -i.tmp 's/updated_at: Mapped\[DateTime\] = mapped_column(DateTime(timezone=True), onupdate=func.now())/updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())/' app/models/surgery.py

if [ $? -eq 0 ]; then
    rm app/models/surgery.py.tmp
    echo -e "${GREEN}✓ Модель обновлена${NC}"
else
    echo -e "${RED}✗ Не удалось обновить модель${NC}"
    exit 1
fi
echo ""

# Шаг 3: Применение миграции
echo "🗄️ Шаг 3: Применение миграции к БД..."

# Проверяем, есть ли миграция
if [ -f "alembic/versions/fix_surgery_updated_at.py" ]; then
    echo -e "${GREEN}✓ Миграция найдена${NC}"
    
    # Применяем миграцию
    alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Миграция применена${NC}"
    else
        echo -e "${YELLOW}⚠ Возможно, миграция уже применена${NC}"
    fi
else
    echo -e "${RED}✗ Миграция не найдена в alembic/versions/${NC}"
    echo "   Скопируйте файл fix_surgery_updated_at.py в alembic/versions/"
    exit 1
fi
echo ""

# Шаг 4: Git
echo "📝 Шаг 4: Подготовка к коммиту..."
git add app/models/surgery.py

echo ""
echo -e "${GREEN}✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!${NC}"
echo ""
echo "📋 Следующие шаги:"
echo "  1. Закоммитьте изменения:"
echo -e "     ${YELLOW}git commit -m 'Fix: surgery updated_at field with server_default'${NC}"
echo ""
echo "  2. Задеплойте на Vercel:"
echo -e "     ${YELLOW}git push origin main${NC}"
echo ""
echo "  3. Попробуйте создать операцию снова"
echo ""
echo "💡 Если нужно откатить изменения:"
echo -e "   ${YELLOW}cp app/models/surgery.py.backup app/models/surgery.py${NC}"
echo ""