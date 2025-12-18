# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Установка системных зависимостей для psycopg2 и Pillow
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev \
    libjpeg-dev zlib1g-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Копируем остальные файлы проекта
COPY . .

# Собираем статику
# RUN python manage.py collectstatic --noinput

# Запускаем сервер (используем gunicorn вместо runserver)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "orders.wsgi:application"]

