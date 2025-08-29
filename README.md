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