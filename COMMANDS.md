# 📝 Команды для деплоя (копируй и вставляй)

## 🔧 1. Подготовка окружения

```bash
# Установка зависимостей
pip install -r requirements.txt

# Или если нужно обновить
pip install --upgrade -r requirements.txt
```

## 🗄️ 2. Инициализация базы данных

```bash
# Инициализация БД
python init_db.py

# Применение миграций
alembic upgrade head

# Проверка текущей версии БД
alembic current

# Если нужно откатить миграцию
alembic downgrade -1
```

## 🔐 3. Генерация SECRET_KEY

```bash
# Генерация нового секретного ключа
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Или более длинного
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 📂 4. Git команды

```bash
# Инициализация репозитория
git init

# Добавление всех файлов
git add .

# Коммит
git commit -m "Initial commit - Medical Information System"

# Создание ветки main
git branch -M main

# Добавление remote (замените на ваш URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push на GitHub
git push -u origin main
```

## ☁️ 5. Vercel CLI (опционально)

```bash
# Установка Vercel CLI
npm i -g vercel

# Логин в Vercel
vercel login

# Деплой (первый раз)
vercel

# Деплой в production
vercel --prod

# Просмотр логов
vercel logs

# Просмотр информации о проекте
vercel ls
```

## 🧪 6. Тестовые запросы (после деплоя)

Замените `YOUR_PROJECT_URL` на ваш Vercel URL.

```bash
# Проверка главной страницы
curl https://YOUR_PROJECT_URL.vercel.app/

# Регистрация администратора
curl -X POST https://YOUR_PROJECT_URL.vercel.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "full_name": "System Administrator",
    "email": "admin@hospital.uz",
    "password": "SecurePassword123!",
    "role": "reception"
  }'

# Регистрация врача
curl -X POST https://YOUR_PROJECT_URL.vercel.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "doctor1",
    "full_name": "Dr. John Smith",
    "email": "doctor@hospital.uz",
    "password": "DoctorPass123!",
    "role": "doctor"
  }'

# Логин
curl -X POST https://YOUR_PROJECT_URL.vercel.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecurePassword123!"
  }'

# Сохраните полученный токен в переменную
export TOKEN="your_token_here"

# Создание пациента (требуется токен)
curl -X POST https://YOUR_PROJECT_URL.vercel.app/patients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "full_name": "John Doe",
    "birth_date": "1990-01-15",
    "gender": "male",
    "phone": "+998901234567",
    "passport": "AB1234567",
    "address": "Tashkent, Amir Temur 15",
    "email": "john.doe@example.com"
  }'

# Получение списка пациентов
curl -X GET https://YOUR_PROJECT_URL.vercel.app/patients/ \
  -H "Authorization: Bearer $TOKEN"

# Общая статистика
curl -X GET https://YOUR_PROJECT_URL.vercel.app/stats/general \
  -H "Authorization: Bearer $TOKEN"

# Финансовая статистика
curl -X GET https://YOUR_PROJECT_URL.vercel.app/stats/financial \
  -H "Authorization: Bearer $TOKEN"
```

## 🔄 7. Обновление деплоя

```bash
# После изменений в коде
git add .
git commit -m "Description of changes"
git push origin main

# Vercel автоматически задеплоит изменения
```

## 🔍 8. Отладка

```bash
# Просмотр логов Vercel
vercel logs --follow

# Или через веб-интерфейс:
# https://vercel.com/your-username/your-project/deployments

# Проверка подключения к БД
python -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-proud-art-a8xtxs9t-pooler.eastus2.azure.neon.tech/neondb?sslmode=require')
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print(result.fetchone()[0])
"

# Локальный запуск для тестирования
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 9. Neon PostgreSQL команды

```bash
# Подключение к БД через psql
psql 'postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-proud-art-a8xtxs9t-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require'

# После подключения можно выполнять SQL запросы:
# \dt                    - показать все таблицы
# \d users               - описание таблицы users
# SELECT * FROM users;   - выбрать всех пользователей
# \q                     - выход
```

## 🎯 10. Environment Variables для Vercel

Скопируйте эти значения в Vercel Dashboard → Settings → Environment Variables:

```env
DATABASE_URL
postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-proud-art-a8xtxs9t-pooler.eastus2.azure.neon.tech/neondb?sslmode=require

SECRET_KEY
[Вставьте сгенерированный ключ из команды выше]

ALGORITHM
HS256

ACCESS_TOKEN_EXPIRE_MINUTES
30
```

## 🚀 11. Быстрый деплой (всё в одном)

```bash
# Полный автоматический процесс
pip install -r requirements.txt && \
python init_db.py && \
alembic upgrade head && \
git init && \
git add . && \
git commit -m "Initial commit" && \
echo "✅ Готово! Теперь:"
echo "1. Создайте репозиторий на GitHub"
echo "2. git remote add origin YOUR_REPO_URL"
echo "3. git push -u origin main"
echo "4. Импортируйте на vercel.com"
echo "5. Добавьте Environment Variables"
```

---

## 💡 Полезные советы

### Как узнать URL проекта на Vercel:
```bash
vercel ls
```

### Как посмотреть все environment variables:
```bash
vercel env ls
```

### Как добавить environment variable через CLI:
```bash
vercel env add SECRET_KEY production
# Затем введите значение
```

### Локальное тестирование с Vercel:
```bash
vercel dev
```

---

**Эти команды покрывают весь процесс от установки до деплоя!**
