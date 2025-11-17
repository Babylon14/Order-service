import os
from celery import Celery


# Установка переменной окружения DJANGO_SETTINGS_MODULE для Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orders.settings")

# Инициализация Celery
app = Celery("backend")

# Настройка Celery из файла Django settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач
app.autodiscover_tasks()

# Установка очереди по умолчанию
app.conf.task_default_queue = "default"

