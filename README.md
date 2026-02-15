# CRM — Django REST API с JWT

Веб-приложение CRM на Django + DRF с JWT-аутентификацией, компаниями и складами.

## Стек

- **Python 3.10+**
- **Poetry** — управление зависимостями
- **Django 5** + **Django REST Framework** + **SimpleJWT**
- **drf-yasg** — Swagger/OpenAPI документация
- **БД:** SQLite (локально) или **PostgreSQL** (Docker)
- **Docker** — контейнеризация приложения и БД

---

## Запуск через Docker (рекомендуется)

База данных — PostgreSQL в контейнере. Миграции применяются при старте контейнера `web`.

### 1. Переменные окружения (опционально)

Для старта достаточно значений по умолчанию в `docker-compose.yml`. Чтобы задать свои пароли и ключи:

```bash
cp .env.example .env
# Отредактируйте .env (POSTGRES_PASSWORD, DJANGO_SECRET_KEY и т.д.)
```

В `docker-compose.yml` при необходимости добавьте для сервиса `web`: `env_file: [.env]`.

### 2. Сборка и запуск

```bash
cd crm
docker compose up --build
```

Приложение: **http://127.0.0.1:8000/**  
Swagger: **http://127.0.0.1:8000/swagger/**

### 3. Миграции в Docker

Миграции выполняются автоматически при каждом старте сервиса `web` (скрипт `docker/entrypoint.sh`).  
Ручной запуск миграций:

```bash
docker compose run --rm web python manage.py migrate
```

### 4. Создание суперпользователя в Docker

```bash
docker compose run --rm web python manage.py createsuperuser
```

### 5. Получение JWT-токена (пример при работе через Docker)

```bash
# Регистрация
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"SecurePass123!","password_confirm":"SecurePass123!"}'

# Вход и получение токена
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"SecurePass123!"}'
```

В ответе прихода будут поля `access` и `refresh`. Для запросов к API используйте заголовок:  
`Authorization: Bearer <access>`.

### Остановка

```bash
docker compose down
# С удалением тома БД:
docker compose down -v
```

---

## Локальная установка (без Docker)

### 1. Установка зависимостей

```bash
cd crm
poetry install
```

### 2. Применение миграций

```bash
poetry run python manage.py migrate
```

### 3. Создание суперпользователя (опционально)

```bash
poetry run python manage.py createsuperuser
```

### 4. Запуск сервера

```bash
poetry run python manage.py runserver
```

Приложение будет доступно по адресу: **http://127.0.0.1:8000/**  
По умолчанию используется SQLite; для PostgreSQL задайте `DATABASE_URL` в окружении.

---

## Документация API (Swagger)

- **Swagger UI:** http://127.0.0.1:8000/swagger/
- **ReDoc:** http://127.0.0.1:8000/redoc/
- **Схема JSON:** http://127.0.0.1:8000/swagger.json

В Swagger нажмите **Authorize** и введите: `Bearer <ваш_access_токен>`.

---

## Получение JWT-токена

### Регистрация пользователя

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ivan",
    "email": "ivan@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Иван",
    "last_name": "Петров"
  }'
```

### Вход (получение access и refresh токенов)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "ivan", "password": "SecurePass123!"}'
```

Пример ответа:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "ivan",
    "email": "ivan@example.com",
    "first_name": "Иван",
    "last_name": "Петров"
  }
}
```

### Обновление access-токена

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

### Пример запроса с авторизацией (компании)

```bash
export ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://127.0.0.1:8000/api/v1/companies/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Структура проекта

```
crm/
├── manage.py
├── pyproject.toml
├── docker-compose.yml    # Сервисы web (Django) и db (PostgreSQL)
├── Dockerfile
├── .env.example
├── docker/
│   └── entrypoint.sh     # Ожидание БД, миграции, запуск gunicorn
├── core/                 # Настройки Django
│   ├── settings.py
│   ├── urls.py
│   ├── api_urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/                # Пользователи, JWT
│   ├── models.py         # User (AbstractUser)
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── companies/            # Компании
│   ├── models.py         # Company (owner OneToOne User)
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── urls.py
│   └── admin.py
└── storages/             # Склады
    ├── models.py         # Storage (ForeignKey Company)
    ├── serializers.py
    ├── views.py
    ├── permissions.py
    ├── urls.py
    └── admin.py
```

---

## API эндпоинты

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| POST | `/api/v1/auth/register/` | Регистрация | Все |
| POST | `/api/v1/auth/login/` | Вход (JWT) | Все |
| POST | `/api/v1/auth/token/refresh/` | Обновление токена | Все |
| GET  | `/api/v1/companies/` | Список компаний | Авторизованные |
| POST | `/api/v1/companies/` | Создать компанию | Авторизованные |
| GET  | `/api/v1/companies/<id>/` | Детали компании | Авторизованные |
| PUT/PATCH | `/api/v1/companies/<id>/` | Редактировать | Только владелец |
| DELETE | `/api/v1/companies/<id>/` | Удалить | Только владелец |
| GET  | `/api/v1/storages/` | Список складов | Владелец компании |
| POST | `/api/v1/storages/` | Создать склад | Владелец компании |
| GET  | `/api/v1/storages/<id>/` | Детали склада | Связанные с компанией |
| PUT/PATCH | `/api/v1/storages/<id>/` | Редактировать | Владелец компании |
| DELETE | `/api/v1/storages/<id>/` | Удалить | Владелец компании |

---

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `DATABASE_URL` | URL PostgreSQL (в Docker задаётся автоматически из `POSTGRES_*`) |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Параметры PostgreSQL для сервиса `db` |
| `DJANGO_SECRET_KEY` | Секретный ключ Django (обязательно сменить в production) |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Разделённые запятой хосты (в Docker: web,localhost,127.0.0.1) |

В Docker Compose `DATABASE_URL` для сервиса `web` формируется из `POSTGRES_*`. Для локального запуска с PostgreSQL:

```bash
export DATABASE_URL="postgres://user:password@localhost:5432/crm_db"
poetry run python manage.py migrate
poetry run python manage.py runserver
```

---

## Админка

После `createsuperuser` войдите в админку: http://127.0.0.1:8000/admin/

Доступны разделы: **Пользователи**, **Компании**, **Склады**.
