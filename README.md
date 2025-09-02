# PriceAggregator 1.0

## Описание

SPA веб-приложение. Единый портал для сравнения цен для сегментов B2C.

- [Хостинг](Ссылка) пока нет
- [Сваггер](Ссылка) пока нет

## Фронтенд-стэк

- Typescript
- React 19
- Redux Toolkit: упраление состоянием
- React Router: клиентский роутинг
- React Hook Form: формы
- Vite
- shadcn/ui с Tailwind СSS
- см. другие зависимости в [`package.json`](package.json)

## Бэкенд-стек

- Python
- Django
- PostgreSQL
- Docker 
- GitHub Actions
- см. другие зависимости в [`package.json`](package.json)

## Требования


- NodeJS, NPM
- IDE
- Терминал для использования Git

## Локальная установка
Для запуска приложения на локальном сервере необходима настройка Django, Telegram (но по идее для запуска и работы с существующими данными не должен быть нужен Telegram - надо исправить).\
Для полноценной работы приложения на локальном сервере необходима настройка Redis, Celery (запускаются в отдельном терминале).

### Telegram
Настройка Telegram нужна для парсинга данных.
1. Авторизуйтесь на [My Telegram](https://my.telegram.org/apps) с помощью номера телефона вашего Telegram аккаунта.
2. В `.env` присвойте переменной "PHONE" 
3. Перейдите на [API development tools](https://my.telegram.org/apps).
4. Заполните поля "App configuration". Если поля уже заполнены, не меняйте их.
5. Сохраните настройки
6. В `.env` присвойте переменной "TELEGRAM_API_ID" значение "App api_id", "TELEGRAM_API_HASH" значение "App api_hash"
7. Запустите команду `set_telegram_session`: `uv run python manage.py set_telegram_session`

### Backend (локальный запуск через Make)

1. Примените миграции базы данных:
   ```sh
   make migrate
   ```

2. Соберите статические файлы (для локального запуска можно пропустить, для prod — требуется):
   ```sh
   make collectstatic
   ```

3. Запустите dev-сервер Django:
   ```sh
   make dev
   ```
   По умолчанию сервер доступен на http://127.0.0.1:8000. Порт задаётся переменной PORT в [`Makefile`](Makefile).

4. (Опционально) Запустите prod-сервер на Gunicorn:
   ```sh
   make prod-run
   ```
   Можно указать порт: `make prod-run PORT=8080`. См. настройки в [`config/settings.py`](config/settings.py).

### Фоновые задачи (Redis + Celery)

1. Запустите Redis (в отдельном терминале):
   ```sh
   make redis
   ```

2. Запустите Celery worker (в отдельном терминале):
   ```sh
   make celery
   ```

3. Запустите планировщик задач Celery Beat (в отдельном терминале):
   ```sh
   make celery-beat
   ```
   Плановые задачи настраиваются в [`config/settings.py`](config/settings.py) (CELERY_BEAT_SCHEDULE).

4. (Опционально) Откройте мониторинг задач (Flower):
   ```sh
   make flower
   ```

### Утилиты

1. Сгенерируйте/обновите Telegram session через management-команду:
   ```sh
   make s
   ```
   Команда: