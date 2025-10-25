# 🚀 Руководство по деплою на Vercel с Neon PostgreSQL

## 📋 Предварительные требования

- Аккаунт на [Vercel](https://vercel.com)
- Аккаунт на [Neon](https://neon.tech) (уже есть)
- Git установлен на компьютере
- Python 3.9+ установлен локально

## 🗄️ Шаг 1: Подготовка базы данных Neon

### 1.1 Обновите alembic.ini
Ваша строка подключения:
```
postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-proud-art-a8xtxs9t-pooler.eastus2.azure.neon.tech/neondb?sslmode=require
```

### 1.2 Инициализируйте базу данных локально

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите скрипт инициализации
python init_db.py
```

### 1.3 Примените миграции Alembic

```bash
# Проверьте текущую версию
alembic current

# Примените все миграции
alembic upgrade head
```

## 📁 Шаг 2: Подготовка проекта

### 2.1 Структура проекта для Vercel

Убедитесь, что у вас есть эти файлы:
```
your-project/
├── api/
│   └── index.py          # Vercel handler
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── routes/
│   └── schemas/
├── alembic/
├── vercel.json           # Конфигурация Vercel
├── requirements.txt
└── .env.example
```

### 2.2 Обновите .gitignore

```gitignore
# Существующие правила...

# Локальные файлы
.env
.vercel

# База данных
*.db
*.sqlite
*.sqlite3
```

## 🔧 Шаг 3: Настройка Vercel

### 3.1 Инициализация Git (если еще не сделано)

```bash
git init
git add .
git commit -m "Initial commit"
```

### 3.2 Подключение к GitHub

```bash
# Создайте новый репозиторий на GitHub
# Затем:
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

### 3.3 Деплой на Vercel

**Вариант А: Через веб-интерфейс Vercel**

1. Зайдите на https://vercel.com
2. Нажмите "New Project"
3. Импортируйте ваш GitHub репозиторий
4. Настройте Environment Variables (см. ниже)
5. Нажмите "Deploy"

**Вариант Б: Через Vercel CLI**

```bash
# Установите Vercel CLI
npm i -g vercel

# Войдите в аккаунт
vercel login

# Деплой
vercel
```

### 3.4 Настройка Environment Variables в Vercel

В настройках проекта на Vercel добавьте:

```
DATABASE_URL = postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-proud-art-a8xtxs9t-pooler.eastus2.azure.neon.tech/neondb?sslmode=require

SECRET_KEY = your-super-secret-key-generate-a-new-one

ALGORITHM = HS256

ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

⚠️ **ВАЖНО**: Сгенерируйте новый SECRET_KEY для продакшена:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🧪 Шаг 4: Тестирование

### 4.1 Проверьте деплой

После успешного деплоя откройте URL проекта (например: `https://your-project.vercel.app`)

### 4.2 Тестовые запросы

```bash
# Проверка главной страницы
curl https://your-project.vercel.app/

# Регистрация пользователя
curl -X POST https://your-project.vercel.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "reception1",
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "role": "reception"
  }'
```

## 🔍 Шаг 5: Устранение проблем

### Проблема: "Module not found"
**Решение**: Проверьте, что все зависимости в `requirements.txt`

### Проблема: "Database connection failed"
**Решение**: 
1. Проверьте, что DATABASE_URL правильно настроен в Vercel
2. Убедитесь, что IP Vercel не заблокирован в Neon (обычно не требуется)

### Проблема: "Function timeout"
**Решение**: Vercel имеет лимит 10 секунд для бесплатных аккаунтов. Оптимизируйте запросы.

### Просмотр логов

```bash
# Через CLI
vercel logs

# Или в веб-интерфейсе:
# Dashboard → Your Project → Deployments → View Function Logs
```

## 📊 Шаг 6: Мониторинг Neon Database

1. Зайдите в [Neon Console](https://console.neon.tech)
2. Выберите ваш проект
3. Мониторьте:
   - Использование storage
   - Количество соединений
   - Производительность запросов

## 🔒 Шаг 7: Безопасность

### Рекомендации:

1. **Никогда не коммитьте .env файлы**
2. **Используйте разные SECRET_KEY для разных окружений**
3. **Настройте CORS правильно**:
   ```python
   # В app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],  # Укажите конкретные домены
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Ограничьте rate limiting** на критичных эндпоинтах

## 🔄 Шаг 8: Continuous Deployment

После настройки, каждый push в main ветку будет автоматически деплоиться на Vercel.

```bash
# Внесите изменения
git add .
git commit -m "Update feature"
git push origin main

# Vercel автоматически задеплоит изменения
```

## 📱 Шаг 9: Подключение фронтенда

Используйте ваш Vercel URL в качестве API endpoint:

```javascript
// В вашем фронтенде
const API_URL = 'https://your-project.vercel.app';

// Пример запроса
fetch(`${API_URL}/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'user',
    password: 'pass'
  })
})
```

## 🎉 Готово!

Ваше приложение теперь работает на:
- **Backend**: Vercel (Serverless Functions)
- **Database**: Neon PostgreSQL (Serverless)

### Полезные ссылки:
- 📖 [Vercel Documentation](https://vercel.com/docs)
- 📖 [Neon Documentation](https://neon.tech/docs)
- 🐛 [Vercel Community](https://github.com/vercel/vercel/discussions)

## 💡 Дополнительные советы

### Локальная разработка

Для локальной разработки создайте `.env` файл:

```bash
cp .env.example .env
# Отредактируйте .env с вашими локальными настройками
```

Запуск локально:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Best Practices

1. **Используйте connection pooling** - Neon уже предоставляет pooler
2. **Настройте мониторинг** - используйте Vercel Analytics
3. **Backup базы данных** - Neon делает автоматические бэкапы
4. **Rate Limiting** - добавьте middleware для защиты от DDoS

---

**Нужна помощь?** Проверьте логи или создайте issue в репозитории проекта.
