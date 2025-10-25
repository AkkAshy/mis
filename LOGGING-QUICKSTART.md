# 🔍 Быстрая отладка регистрации

## 🎯 Проблема
Регистрация не работает и непонятно почему? Добавьте детальное логирование!

## ⚡ Быстрое решение (30 секунд)

### Вариант A: Автоматически (рекомендуется)

```bash
# 1. Включите логирование
chmod +x enable_logging.sh
./enable_logging.sh

# 2. Деплой
git commit -m "Add detailed logging"
git push origin main

# 3. Попробуйте зарегистрироваться

# 4. Смотрите логи в Vercel Dashboard:
#    Deployments → Latest → View Function Logs
```

### Вариант B: Вручную

```bash
# 1. Замените файлы
cp app/routes/auth_with_logging.py app/routes/auth.py
cp app/core/security_with_logging.py app/core/security.py

# 2. Деплой
git add .
git commit -m "Add detailed logging"
git push origin main
```

## 📊 Что покажут логи

```
================================================================================
🔵 НАЧАЛО РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ
📝 Username: admin
📝 Email: admin@example.com
🔍 Шаг 1: Проверка существования username...
✅ Username свободен
🔍 Шаг 2: Проверка существования email...
✅ Email свободен
🔐 Шаг 3: Хеширование пароля...
❌ Ошибка при хешировании пароля: 'NoneType' object has no attribute 'encode'
                                    ^^^^^^^^ ВОТ ПРОБЛЕМА!
================================================================================
```

## 🔍 Где смотреть логи

### В Vercel Dashboard:
1. Откройте https://vercel.com
2. Выберите проект → **Deployments**
3. Кликните на последний деплой
4. Нажмите **View Function Logs**
5. Ищите строки с 🔵 и ❌

### Через CLI:
```bash
# Реал-тайм логи
vercel logs --follow

# Последние 100 строк
vercel logs --limit 100
```

## 🎯 Типичные проблемы и их признаки

| Симптом в логах | Проблема | Решение |
|-----------------|----------|---------|
| `❌ Ошибка при хешировании пароля` | Пароль не передается | Проверьте JSON в запросе |
| `❌ Ошибка при коммите` | Проблема с БД | Проверьте DATABASE_URL |
| `❌ Username already registered` | Дубликат | Пользователь уже есть |
| `❌ Ошибка при создании токена` | Проблема с SECRET_KEY | Проверьте env vars |

## 🔄 Отключение логирования

После того как нашли проблему:

```bash
# Автоматически
./disable_logging.sh

# Вручную
cp app/routes/auth.py.backup app/routes/auth.py
cp app/core/security.py.backup app/core/security.py
git add .
git commit -m "Remove detailed logging"
git push origin main
```

## 💡 Тестовый запрос

```bash
curl -X POST https://your-project.vercel.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "role": "reception"
  }'
```

## 📞 Что делать дальше

1. **Получили логи?** 
   - Найдите строку с ❌
   - Посмотрите какой шаг упал
   - Traceback покажет причину

2. **Нашли проблему?**
   - Исправьте код
   - Задеплойте снова
   - Отключите детальное логирование

3. **Всё работает?**
   - Отключите логирование: `./disable_logging.sh`
   - Деплой: `git push origin main`

---

**Время диагностики: ~5 минут**
