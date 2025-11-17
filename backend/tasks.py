"""Здесь будут Celery-задачи"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email_task(subject, message, recipient_list):
    """Отправка email-письма"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False
    )
    return f"Электронное письмо отправлено на {recipient_list}"




