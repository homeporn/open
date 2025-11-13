# Покер Трекер

Веб-приложение для учета игроков в покер, их сумм и докупов с красивым интерфейсом и визуализацией статистики.

## Возможности

- ✅ **Веб-интерфейс** - современный и удобный UI
- ✅ Добавление и удаление игроков
- ✅ Учет бай-инов (взносов)
- ✅ Учет выигрышей и проигрышей
- ✅ Учет докупов (дополнительных взносов)
- ✅ Просмотр статистики по каждому игроку
- ✅ Общая статистика по всем игрокам
- ✅ Автоматический расчет баланса
- ✅ Визуализация статистики с графиками (Chart.js)
- ✅ Адаптивный дизайн для мобильных устройств

## Требования

- Python 3.6 или выше
- Flask (устанавливается через requirements.txt)
- SQLite3 (входит в стандартную поставку Python)

## Установка

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

## Использование

### Веб-интерфейс (рекомендуется)

Запустите веб-сервер:

```bash
python app.py
```

Откройте браузер и перейдите по адресу:
```
http://localhost:5000
```

Веб-интерфейс предоставляет:
- Удобное управление игроками через веб-формы
- Красивые карточки с информацией об игроках
- Интерактивные графики статистики
- Модальные окна для быстрого добавления данных
- Адаптивный дизайн

### Консольная версия

Также доступна консольная версия программы:

```bash
python poker_tracker.py
```

## Функционал

### 1. Добавить игрока
Добавляет нового игрока в базу данных.

### 2. Удалить игрока
Удаляет игрока и все связанные с ним данные.

### 3. Список игроков
Показывает всех игроков с их текущим балансом.

### 4. Добавить бай-ин
Записывает взнос игрока на игру.

### 5. Добавить выигрыш
Записывает сумму выигрыша игрока.

### 6. Добавить проигрыш
Записывает сумму проигрыша игрока.

### 7. Добавить докуп
Записывает дополнительный взнос (докуп) игрока.

### 8. Статистика игрока
Показывает детальную статистику по выбранному игроку:
- Общий бай-ин
- Общие выигрыши
- Общие проигрыши
- Общие докупы
- Количество докупов
- Текущий баланс

### 9. Общая статистика
Показывает статистику по всем игрокам в табличном виде.

## База данных

Программа создает файл `poker_tracker.db` в текущей директории для хранения всех данных.

## Формула расчета баланса

Баланс = (Выигрыши) - (Бай-ины) - (Проигрыши) - (Докупы)

## Структура проекта

```
open/
├── app.py                 # Flask веб-приложение
├── poker_tracker.py       # Консольная версия и класс PokerTracker
├── requirements.txt       # Зависимости Python
├── templates/            # HTML шаблоны
│   ├── base.html
│   ├── index.html
│   └── player.html
├── static/               # Статические файлы
│   ├── style.css        # Стили
│   └── app.js           # JavaScript
└── poker_tracker.db     # База данных SQLite (создается автоматически)
```

## Пример использования (веб-интерфейс)

1. Запустите веб-сервер: `python app.py`
2. Откройте браузер: `http://localhost:5000`
3. Нажмите "Добавить игрока" и введите имя
4. Для каждого игрока можно:
   - Просмотреть детальную статистику
   - Добавить транзакцию (бай-ин, выигрыш, проигрыш)
   - Добавить докуп
   - Удалить игрока
5. На странице статистики игрока отображаются графики и все данные

## API Endpoints

Веб-приложение также предоставляет REST API:

- `GET /api/players` - получить список игроков
- `POST /api/players` - добавить игрока
- `DELETE /api/players/<id>` - удалить игрока
- `GET /api/players/<id>/statistics` - статистика игрока
- `POST /api/transactions` - добавить транзакцию
- `POST /api/rebuys` - добавить докуп
- `GET /api/statistics` - статистика всех игроков

## Деплой на хостинг

### Подготовка к деплою

1. **Клонируйте репозиторий:**
```bash
git clone <ваш-репозиторий>
cd open
```

2. **Убедитесь, что все файлы на месте:**
   - `app.py` - Flask приложение
   - `poker_tracker.py` - класс для работы с БД
   - `requirements.txt` - зависимости
   - `runtime.txt` - версия Python
   - `.gitignore` - исключения для Git

### Деплой на Render (рекомендуется)

1. Создайте аккаунт на [Render.com](https://render.com)
2. Нажмите "New" → "Web Service"
3. Подключите ваш GitHub репозиторий
4. Настройки:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
5. Добавьте в `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```
6. Нажмите "Create Web Service"

### Деплой на Railway

1. Создайте аккаунт на [Railway.app](https://railway.app)
2. Нажмите "New Project" → "Deploy from GitHub repo"
3. Выберите ваш репозиторий
4. Railway автоматически определит Python приложение
5. Добавьте переменную окружения `PORT` (Railway установит автоматически)

### Деплой на Heroku

1. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Создайте файл `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Добавьте в `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```
4. Выполните:
```bash
heroku login
heroku create ваш-проект
git push heroku main
```

### Деплой на Netlify (через serverless)

Netlify не поддерживает Flask напрямую, но можно использовать адаптер:

1. Установите Netlify CLI:
```bash
npm install -g netlify-cli
```

2. Создайте файл `netlify/functions/server.py` (уже создан)

3. Установите serverless-wsgi:
```bash
pip install serverless-wsgi
```

4. Добавьте в `requirements.txt`:
   ```
   serverless-wsgi==0.8.2
   ```

5. Обновите `netlify.toml`:
```toml
[build]
  command = "pip install -r requirements.txt && pip install serverless-wsgi"
  functions = "netlify/functions"

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/server"
  status = 200
```

6. Деплой:
```bash
netlify deploy --prod
```

### Деплой на PythonAnywhere

1. Создайте аккаунт на [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Загрузите файлы через веб-интерфейс или Git
3. Настройте WSGI файл:
```python
import sys
path = '/home/ваш-username/poker-tracker'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```
4. Настройте статические файлы:
   - URL: `/static/`
   - Directory: `/home/ваш-username/poker-tracker/static`

### Локальная разработка

Для локальной разработки:

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите приложение
python app.py
```

Приложение будет доступно по адресу `http://localhost:5000`

## Структура проекта для деплоя

```
poker-tracker/
├── .gitignore              # Исключения для Git
├── README.md               # Документация
├── app.py                  # Flask приложение
├── poker_tracker.py        # Класс для работы с БД
├── requirements.txt        # Зависимости Python
├── runtime.txt            # Версия Python
├── netlify.toml           # Конфигурация Netlify
├── Procfile               # Конфигурация для Heroku (создать при необходимости)
├── templates/             # HTML шаблоны
│   ├── base.html
│   ├── index.html
│   ├── player.html
│   ├── sessions.html
│   └── session.html
├── static/                # Статические файлы
│   ├── style.css
│   └── app.js
└── netlify/               # Netlify functions (для деплоя на Netlify)
    └── functions/
        └── server.py
```

## Важные замечания

⚠️ **База данных SQLite:**
- SQLite файл создается автоматически при первом запуске
- Для продакшена рекомендуется использовать PostgreSQL или другую БД
- Файл БД не должен попадать в Git (уже в .gitignore)

⚠️ **Переменные окружения:**
- Для продакшена можно добавить `.env` файл для конфигурации
- Не коммитьте `.env` в Git

## Лицензия

Этот проект создан для личного использования.

