# ✅ Чеклист деплоя на Vercel + Neon PostgreSQL

## 📋 Предварительная подготовка

- [ ] Python 3.9+ установлен
- [ ] Git установлен
- [ ] Аккаунт на Vercel создан (vercel.com)
- [ ] Аккаунт на Neon создан и БД готова
- [ ] Node.js и npm установлены (опционально, для Vercel CLI)

## 🗄️ Шаг 1: База данных

- [ ] Запущен `python init_db.py` - база инициализирована
- [ ] Запущен `alembic upgrade head` - миграции применены
- [ ] Проверено подключение к Neon PostgreSQL
- [ ] Таблицы созданы (users, patients, appointments)

## 📝 Шаг 2: Git репозиторий

- [ ] Выполнен `git init`
- [ ] Выполнен `git add .`
- [ ] Выполнен `git commit -m "Initial commit"`
- [ ] Создан репозиторий на GitHub
- [ ] Выполнен `git remote add origin <url>`
- [ ] Выполнен `git push -u origin main`

## ☁️ Шаг 3: Vercel

- [ ] Зайдён на vercel.com
- [ ] Нажата кнопка "New Project"
- [ ] Импортирован GitHub репозиторий
- [ ] Настроены Environment Variables:
  - [ ] `DATABASE_URL` добавлен
  - [ ] `SECRET_KEY` добавлен (новый, сгенерированный!)
  - [ ] `ALGORITHM` = HS256
  - [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` = 30
- [ ] Нажата кнопка "Deploy"
- [ ] Деплой завершён успешно

## 🔐 Шаг 4: Безопасность

- [ ] Сгенерирован новый SECRET_KEY для продакшена:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] SECRET_KEY добавлен в Vercel Environment Variables
- [ ] `.env` добавлен в `.gitignore`
- [ ] Проверено, что пароли не в коде

## 🧪 Шаг 5: Тестирование

- [ ] Открыт URL проекта: `https://your-project.vercel.app`
- [ ] Проверен эндпоинт `/` - возвращает корректный JSON
- [ ] Протестирован `/auth/register` - регистрация работает
- [ ] Протестирован `/auth/login` - логин работает
- [ ] Протестирован защищённый эндпоинт с токеном
- [ ] Проверены логи в Vercel Dashboard

## 🎯 Шаг 6: Финальная проверка

- [ ] Все эндпоинты отвечают
- [ ] База данных доступна
- [ ] Нет ошибок в логах
- [ ] CORS настроен правильно
- [ ] Документация обновлена с новым URL

## 📊 Опционально: Мониторинг

- [ ] Настроен Vercel Analytics
- [ ] Добавлен мониторинг в Neon Console
- [ ] Настроены алерты на критичные ошибки
- [ ] Документирован процесс деплоя для команды

## 🎉 Готово!

- [ ] URL задеплоенного API записан: `https://_________________.vercel.app`
- [ ] Команда уведомлена о новом деплое
- [ ] Документация обновлена
- [ ] Фронтенд обновлён с новым API URL

---

## 🚨 Если что-то пошло не так

### Проблема: Деплой не проходит
✅ Проверьте логи в Vercel Dashboard → Deployments → Function Logs

### Проблема: "Database connection failed"
✅ Проверьте:
1. DATABASE_URL в Environment Variables
2. Формат строки подключения (должен быть `postgresql://...`)
3. Доступность Neon БД в Neon Console

### Проблема: "Module not found"
✅ Проверьте, что все зависимости в requirements.txt

### Проблема: "Function timeout"
✅ Оптимизируйте запросы или рассмотрите Vercel Pro

---

**Время выполнения**: ~15-20 минут  
**Сложность**: Средняя  
**Требуется опыт**: Git, командная строка

**Удачи с деплоем!** 🚀
