# 🔍 Инструкция по добавлению логирования для отладки

## 📝 Что это даст?

После добавления логирования вы увидите в Vercel Logs **каждый шаг** процесса регистрации:
- ✅ Проверку username
- ✅ Проверку email
- ✅ Хеширование пароля
- ✅ Создание пользователя
- ✅ Сохранение в БД
- ✅ Создание токена
- ❌ **Точное место ошибки** с traceback

## 🔄 Вариант 1: Замена файлов (Рекомендуется)

### Шаг 1: Замените файлы

```bash
# Создайте резервные копии
cp app/routes/auth.py app/routes/auth.py.backup
cp app/core/security.py app/core/security.py.backup

# Замените на версии с логированием
cp app/routes/auth_with_logging.py app/routes/auth.py
cp app/core/security_with_logging.py app/core/security.py
```

### Шаг 2: Деплой

```bash
git add .
git commit -m "Add detailed logging for debugging registration"
git push origin main
```

### Шаг 3: Попробуйте зарегистрироваться

Отправьте запрос на регистрацию и сразу проверьте логи в Vercel.

### Шаг 4: Проверьте логи в Vercel

1. Зайдите в Vercel Dashboard
2. Выберите ваш проект
3. Перейдите в **Deployments** → выберите последний деплой
4. Нажмите **View Function Logs**
5. Найдите запись с регистрацией (будет начинаться с `🔵 НАЧАЛО РЕГИСТРАЦИИ`)

---

## 🔄 Вариант 2: Ручная вставка кода

Если хотите добавить логирование вручную, добавьте в начало каждого файла:

### В `app/routes/auth.py`:

```python
import logging
import traceback

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

Затем в функции `register` добавьте логирование на каждом шаге:

```python
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info("=" * 80)
        logger.info("🔵 НАЧАЛО РЕГИСТРАЦИИ")
        logger.info(f"Username: {user.username}")
        
        # ... ваш существующий код ...
        
        # После каждого шага добавьте:
        logger.info("✅ Шаг X выполнен")
        
    except Exception as e:
        logger.error(f"❌ ОШИБКА: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
```

---

## 📊 Что вы увидите в логах

### Успешная регистрация:

```
================================================================================
🔵 НАЧАЛО РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ
📝 Username: admin
📝 Email: admin@example.com
📝 Full name: Admin User
📝 Role: reception
📝 Password length: 10 chars
🔍 Шаг 1: Проверка существования username...
✅ Username свободен
🔍 Шаг 2: Проверка существования email...
✅ Email свободен
🔐 Шаг 3: Хеширование пароля...
   Password type: <class 'str'>
   Hashed password length: 97
✅ Пароль успешно захеширован
👤 Шаг 4: Создание объекта пользователя...
✅ Объект пользователя создан
💾 Шаг 5: Добавление пользователя в БД...
✅ Пользователь добавлен в сессию
💾 Шаг 6: Коммит изменений в БД...
✅ Изменения сохранены в БД
🔄 Шаг 7: Обновление объекта пользователя...
   User ID: 1
✅ Объект обновлен
🔑 Шаг 8: Создание access token...
✅ Токен создан
================================================================================
✅ РЕГИСТРАЦИЯ УСПЕШНО ЗАВЕРШЕНА
================================================================================
```

### При ошибке:

```
================================================================================
🔵 НАЧАЛО РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ
📝 Username: admin
🔍 Шаг 1: Проверка существования username...
✅ Username свободен
🔍 Шаг 2: Проверка существования email...
✅ Email свободен
🔐 Шаг 3: Хеширование пароля...
❌ Ошибка при хешировании пароля: 'NoneType' object has no attribute 'encode'
Traceback:
  File "/app/routes/auth.py", line 78, in register
    hashed_password = get_password_hash(user.password)
  File "/app/core/security.py", line 45, in get_password_hash
    return pwd_context.hash(pw)
  ...
================================================================================
❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ РЕГИСТРАЦИИ
Error type: AttributeError
Error message: 'NoneType' object has no attribute 'encode'
================================================================================
```

---

## 🎯 Что делать после просмотра логов

### Если ошибка на шаге хеширования пароля:
➡️ Проблема с передачей пароля в запросе

### Если ошибка на шаге коммита в БД:
➡️ Проблема с подключением к Neon PostgreSQL или constraint violation

### Если ошибка на шаге проверки username/email:
➡️ Проблема с подключением к БД или SQL запросом

### Если ошибка на шаге создания токена:
➡️ Проблема с SECRET_KEY или библиотекой jose

---

## 🔧 Дополнительная диагностика

### Проверка Environment Variables:

Добавьте в `app/main.py` временный endpoint для проверки:

```python
@app.get("/debug/env")
def debug_env():
    """УДАЛИТЕ ЭТОТ ENDPOINT ПОСЛЕ ОТЛАДКИ!"""
    import os
    return {
        "DATABASE_URL_exists": bool(os.getenv("DATABASE_URL")),
        "SECRET_KEY_exists": bool(os.getenv("SECRET_KEY")),
        "DATABASE_URL_length": len(os.getenv("DATABASE_URL", "")),
        "SECRET_KEY_length": len(os.getenv("SECRET_KEY", ""))
    }
```

Проверьте: `https://your-project.vercel.app/debug/env`

**⚠️ НЕ ЗАБУДЬТЕ УДАЛИТЬ ЭТОТ ENDPOINT!**

---

## 📞 После получения логов

Когда увидите ошибку в логах:
1. Сделайте скриншот или скопируйте текст ошибки
2. Найдите строку с `❌ ОШИБКА` или `❌ КРИТИЧЕСКАЯ ОШИБКА`
3. Посмотрите какой шаг не прошел
4. Traceback покажет точное место проблемы

---

## 🔄 Откат изменений

Если нужно вернуть исходные файлы:

```bash
cp app/routes/auth.py.backup app/routes/auth.py
cp app/core/security.py.backup app/core/security.py
git add .
git commit -m "Revert logging changes"
git push origin main
```

---

## 💡 Полезные команды

### Просмотр логов в реальном времени (Vercel CLI):

```bash
vercel logs --follow
```

### Просмотр последних 100 строк:

```bash
vercel logs --limit 100
```

### Фильтр по ошибкам:

```bash
vercel logs | grep "❌"
```

---

**После того как найдете проблему, обязательно отключите детальное логирование в продакшене!**
