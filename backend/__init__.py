from backend.celery import app as celery_app

# Проверка, импортируется ли Celery при запуске Django
__all__ = ("celery_app",)

