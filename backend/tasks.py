"""Здесь будут Celery-задачи"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from backend.utils import load_shop_data_from_yaml


# --- АСИНХРОННЫЕ ЗАДАЧИ для отправки email-писем ---
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


@shared_task
def send_contact_confirmation_email_task(contact_id, token):
    """Асинхронная задача для отправки письма с подтверждением контакта."""
    from backend.models import Contact

    try:
        contact = Contact.objects.get(id=contact_id)
        # Ссылка для подтверждения
        confirmation_link = f"http://127.0.0.1:8000/api/v1/confirm-contact/{token}/"

        subject = "Подтверждение адреса доставки"
        message = f"""
        Здравствуйте, {contact.first_name or contact.user.username}!

        Вы указали этот email ({contact.email}) как адрес доставки.
        Пожалуйста, подтвердите его, перейдя по ссылке:

        {confirmation_link}

        Ссылка действительна в течение 24-х часов.

        С уважением,
        Администрация сервиса.
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [contact.email],
            fail_silently=False,
        )
        return f"Письмо с подтверждением отправлено на {contact.email} (Контакт ID: {contact_id})"
    except Contact.DoesNotExist:
        return f"Контакт с ID {contact_id} не был найден. Письмо не отправлено."


# --- АСИНХРОННЫЕ ЗАДАЧИ для импорта данных магазина ---
@shared_task
def import_shop_data_task(shop_id: int, yaml_file_path: str):
    """Асинхронная задача для импорта данных КОНКРЕТНОГО магазина."""
    return load_shop_data_from_yaml(shop_id, yaml_file_path)
    

