# Быстрый старт - Деплой на GitHub и Netlify

## Шаг 1: Загрузка на GitHub

```bash
# Если репозиторий еще не инициализирован
git init
git add .
git commit -m "Initial commit: Poker Tracker"

# Создайте репозиторий на GitHub, затем:
git remote add origin https://github.com/ВАШ-USERNAME/poker-tracker.git
git branch -M main
git push -u origin main
```

## Шаг 2: Деплой на Netlify

### Вариант A: Через веб-интерфейс (проще)

1. Перейдите на [netlify.com](https://www.netlify.com) и зарегистрируйтесь
2. Нажмите "Add new site" → "Import an existing project"
3. Выберите "GitHub" и авторизуйтесь
4. Выберите ваш репозиторий `poker-tracker`
5. Настройки:
   - **Build command:** `pip install -r requirements.txt && pip install serverless-wsgi`
   - **Publish directory:** `.` (точка)
   - **Functions directory:** `netlify/functions`
6. Нажмите "Deploy site"
7. Дождитесь завершения деплоя (2-3 минуты)

### Вариант B: Через CLI

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

## Шаг 3: Проверка

После деплоя:
1. Откройте URL вашего сайта (будет показан в Netlify)
2. Проверьте, что приложение работает
3. Попробуйте добавить игрока
4. Проверьте темную тему

## Альтернативные платформы

Если Netlify не подходит, используйте:

- **Render** (рекомендуется для Flask): [render.com](https://render.com)
- **Railway**: [railway.app](https://railway.app)
- **Heroku**: [heroku.com](https://heroku.com)

Подробные инструкции в `DEPLOY.md` и `README.md`

## Решение проблем

### Проблема: Build failed

- Проверьте логи в Netlify
- Убедитесь, что все файлы в репозитории
- Проверьте версию Python в `runtime.txt`

### Проблема: Функции не работают

- Убедитесь, что `serverless-wsgi` установлен
- Проверьте `netlify/functions/server.py`
- Проверьте `netlify.toml`

### Проблема: Статические файлы не загружаются

- Проверьте, что папка `static/` в репозитории
- Убедитесь, что пути в шаблонах правильные

## Обновление приложения

После изменений:

```bash
git add .
git commit -m "Описание изменений"
git push origin main
```

Netlify автоматически пересоберет и задеплоит новую версию.

