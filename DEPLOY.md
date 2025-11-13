# Инструкция по деплою

## Быстрый старт

### 1. Подготовка репозитория

```bash
# Инициализация Git (если еще не сделано)
git init
git add .
git commit -m "Initial commit"

# Добавление удаленного репозитория
git remote add origin https://github.com/ваш-username/poker-tracker.git
git branch -M main
git push -u origin main
```

### 2. Деплой на Render (самый простой способ)

1. Перейдите на [render.com](https://render.com) и зарегистрируйтесь
2. Нажмите "New" → "Web Service"
3. Подключите ваш GitHub репозиторий
4. Настройки:
   - **Name:** poker-tracker (или любое другое)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Нажмите "Create Web Service"
6. Дождитесь завершения деплоя (обычно 2-3 минуты)

### 3. Деплой на Railway

1. Перейдите на [railway.app](https://railway.app) и зарегистрируйтесь
2. Нажмите "New Project" → "Deploy from GitHub repo"
3. Выберите ваш репозиторий
4. Railway автоматически определит Python приложение
5. Дождитесь завершения деплоя

### 4. Деплой на Heroku

```bash
# Установите Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Войдите в Heroku
heroku login

# Создайте приложение
heroku create ваш-проект-name

# Деплой
git push heroku main

# Откройте приложение
heroku open
```

### 5. Деплой на Netlify

```bash
# Установите Netlify CLI
npm install -g netlify-cli

# Войдите в Netlify
netlify login

# Инициализация проекта
netlify init

# Деплой
netlify deploy --prod
```

**Важно:** Для Netlify нужно использовать serverless functions. См. README.md для подробностей.

## Переменные окружения

Для продакшена можно настроить переменные окружения:

- `FLASK_ENV=production`
- `DATABASE_URL` (если используете внешнюю БД)

## Проверка деплоя

После деплоя проверьте:

1. ✅ Приложение открывается в браузере
2. ✅ Можно добавить игрока
3. ✅ Можно добавить транзакцию
4. ✅ Статистика отображается корректно
5. ✅ Темная тема работает

## Решение проблем

### Проблема: Приложение не запускается

- Проверьте логи на платформе хостинга
- Убедитесь, что все зависимости в `requirements.txt`
- Проверьте версию Python в `runtime.txt`

### Проблема: База данных не сохраняется

- На некоторых платформах файловая система эфемерная
- Рассмотрите использование внешней БД (PostgreSQL)

### Проблема: Статические файлы не загружаются

- Проверьте настройки статических файлов на платформе
- Убедитесь, что папка `static/` в репозитории

## Обновление приложения

После внесения изменений:

```bash
git add .
git commit -m "Описание изменений"
git push origin main
```

Платформа автоматически пересоберет и задеплоит новую версию.

