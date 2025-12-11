# Order Service — управление заказами, импортом и каталогом

[![codecov](https://codecov.io/github/Babylon14/Order-service/graph/badge.svg?token=90POA6ZDCW)](https://codecov.io/github/Babylon14/Order-service)

**Order Service** — сервис заказов на Django 5 + DRF с JWT-аутентификацией, асинхронным импортом товаров через Celery/Redis, подтверждением e‑mail и поддержкой социальных логинов (Google/GitHub). Есть простое SPA на React с интеграцией Sentry и автосохранением токенов после OAuth.

## Что появилось недавно
- Асинхронный импорт YAML через Celery (`start-import-*`, `import-status`) и отдельная задача очистки кэша.
- Redis-кэш для списка товаров с автоматической инвалидацией сигналами и Celery-задачей.
- Загрузка изображений товаров и аватаров с генерацией миниатюр (ImageKit) в фоне.
- Социальная авторизация Google/GitHub с выдачей JWT через кастомный pipeline и редиректом на фронтенд.
- Интеграция Sentry и на бэкенде (Django + Celery), и на фронтенде (React Router, APM, ErrorBoundary).
- DRF throttling по умолчанию (10/min анонимно, 100/min авторизовано) и CORS для SPA на `127.0.0.1:3000`.

## Стек
- Python 3.13, Django 5.2, DRF 3.16, SimpleJWT, django-filter, drf-spectacular.
- PostgreSQL 16, Redis, Celery.
- Social auth: `social-auth-app-django` (Google/GitHub).
- Медиа: ImageKit (thumb/detail для товаров, avatar thumbnail).
- Почта: MailHog/SMTP; отправка писем и подтверждений через Celery.
- Observability: Sentry (backend DSN + frontend DSN).
- Frontend: React 19, axios, react-router-dom 7, Sentry SDK.

## Структура
```
order-service/
├── backend/                  # Django app + Celery задачи
│   ├── api/v1/               # Вся публичная API
│   ├── tasks.py              # email, импорт, кэш, генерация миниатюр
│   ├── redis_client.py       # прямое подключение и helper'ы кэша
│   ├── signals.py            # инвалидация кэша и генерация thumb'ов
│   └── utils.py              # импорт YAML → БД
├── data/                     # Примерные YAML (shop1..3)
├── frontend/                 # React SPA (social login + Sentry демо)
├── orders/settings.py        # Настройки Django (JWT, CORS, throttling, Sentry)
├── docker-compose.yml        # Postgres + pgAdmin + Redis
└── README.md
```

## Быстрый старт (backend)
1) Клонируйте репозиторий и создайте окружение
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt                      # или uv pip install -r requirements.txt
```

2) Поднимите инфраструктуру (Postgres + pgAdmin + Redis)
```bash
cp .env.example .env  # если ещё нет файла
docker-compose up -d
```
Postgres: `localhost:5434`, pgAdmin: `http://localhost:5050`, Redis: `6379`.

3) Примените миграции и создайте учётки
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_initial_shops   # создаст shop1..shop3
```

4) Запустите Celery worker (нужен Redis)
```bash
celery -A backend worker -l info
```

5) Запустите сервер разработки
```bash
python manage.py runserver  # http://127.0.0.1:8000
```

## Быстрый старт (frontend)
```bash
cd frontend
npm install
REACT_APP_SENTRY_DSN_FRONTEND=<dsn> npm start  # или задайте в .env
```
Маршруты SPA: `/login` (OAuth кнопки), `/social-login-success` (сохраняет access/refresh и редиректит), `/` (Dashboard с тестами Sentry).

## .env (минимальный пример)
```env
SECRET_KEY=dev-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=orders_db
POSTGRES_USER=orders_user
POSTGRES_PASSWORD=pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5434

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=<client_id>
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=<client_secret>
SOCIAL_AUTH_GITHUB_OAUTH2_KEY=<client_id>
SOCIAL_AUTH_GITHUB_OAUTH2_SECRET=<client_secret>
FRONTEND_SOCIAL_LOGIN_SUCCESS_URL=http://127.0.0.1:3000/social-login-success

SENTRY_DSN_BACKEND=<dsn или пусто>
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin_password
```
Frontend берёт `REACT_APP_SENTRY_DSN_FRONTEND` из своего `.env`.

## Основные возможности API (v1)
Базовый URL: `http://127.0.0.1:8000/api/v1/`

### Аутентификация
- `POST /register/` — регистрация, создаётся `EmailConfirmation`, отправляется письмо.
- `POST /login/` — выдача `access/refresh` по email+паролю.
- `POST /token/refresh/` — обновление access.
- `GET /confirm-email/<token>/` — активация учётки.
- Social OAuth: `GET /auth/login/google-oauth2/` или `/auth/login/github/` (standard social_django), далее бэкенд делает редирект на `FRONTEND_SOCIAL_LOGIN_SUCCESS_URL` с JWT.
- `GET /users/me/` — данные текущего пользователя.
- `GET/PUT/PATCH /profile/` — обновление профиля и аватара (thumb генерируется Celery).

### Каталог и кэширование
- `GET /product-infos/` — список цен/складов с фильтрами (django-filter: категория, магазин, цена/кол-во, параметры), search и ordering. Ответ кэшируется в Redis (db=1) с TTL 10 минут; кэш сбрасывается сигналами `post_save/post_delete` ProductInfo и задачей `clear_product_list_cache_task`.
- `GET /products/<id>/` — детальная карточка товара.
- `PUT /products/<id>/image-upload/` — загрузка оригинала, thumb/detail создаются ImageKit в Celery.

### Корзина и заказы
- `GET/DELETE /cart/` — получить/очистить корзину, `POST /cart/add/`, `PUT/DELETE /cart/item/<id>/`.
- `POST /confirm-order/` — формирует заказ из корзины и указанного контакта, валидирует остатки, уменьшает склад.
- `GET /orders/` и `GET /orders/<id>/` — история и детали.

### Контакты
- `GET/POST /contacts/`, `GET/PUT/PATCH/DELETE /contacts/<id>/`.
- `POST /send-contact-confirmation/` — создаёт токен и отправляет письмо через Celery.
- `GET /confirm-contact/<token>/` — подтверждение адреса.

### Импорт YAML
- `POST /start-import-all-shops/` — Celery-задача для всех активных магазинов.
- `POST /start-import-shop/<shop_id>/` — импорт конкретного магазина; можно передать `yaml_file_path`.
- `GET /import-status/<task_id>/` — статус Celery-задачи.
Формат YAML — как в примерах `data/shop*.yaml` (categories → products → product_infos с параметрами).

### Документация и лимиты
- Throttling: `anon 10/min`, `user 100/min`.
- OpenAPI: drf-spectacular настроен, схему можно включить `SERVE_INCLUDE_SCHEMA=True` при необходимости.
- CORS: разрешены `http://localhost:3000`, `http://127.0.0.1:3000`.

## Почта
По умолчанию отправка идёт через MailHog (`EMAIL_HOST=127.0.0.1`, `EMAIL_PORT=1025`). Для продакшена настройте SMTP в `.env` и `DEFAULT_FROM_EMAIL`. Все письма регистрации и подтверждения контактов отправляются Celery-задачами.

## Наблюдаемость (Sentry)
- Backend: задайте `SENTRY_DSN_BACKEND`, интеграции Django+Celery активируются автоматически.
- Frontend: `REACT_APP_SENTRY_DSN_FRONTEND`, `reactRouterTracingIntegration` уже подключён. На Dashboard есть две кнопки для теста ошибок (JS exception и React render crash).

## Работа с медиа
Медиа лежат в `media/`. Оригиналы товаров — `products/originals`, миниатюры и detail генерируются асинхронно. Для аватаров сохраняются оригинал и thumbnail.

## Запуск тестов
```bash
python manage.py test
```
При запуске тестов автоматически используется SQLite.

## Эксплуатация и безопасность
- Задайте реальный `SECRET_KEY`, включите `DEBUG=False`, заполните `ALLOWED_HOSTS`.
- Используйте HTTPS, настройте CORS под ваш домен.
- Защитите Redis/DB паролями, обновляйте зависимости.

## Полезные команды
- Создать миграции / применить: `python manage.py makemigrations && python manage.py migrate`
- Собрать статику: `python manage.py collectstatic`
- Очистить кэш списка товаров: `celery -A backend call backend.tasks.clear_product_list_cache_task`

