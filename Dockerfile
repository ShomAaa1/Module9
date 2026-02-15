# CRM — Django + Poetry + Gunicorn
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Системные зависимости + Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && curl -sSL https://install.python-poetry.org | POETRY_VERSION=2.3.2 python3 - \
    && apt-get purge -y curl gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /app

# Зависимости
COPY pyproject.toml poetry.lock* ./
RUN poetry lock && poetry install --without dev --no-root --no-directory

# Код приложения
COPY . .
RUN chmod +x /app/docker/entrypoint.sh

# Сбор статических файлов (Swagger UI, admin и т.д.)
RUN DJANGO_SECRET_KEY=build-placeholder python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "core.wsgi:application"]
