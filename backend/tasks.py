"""Здесь будут Celery-задачи"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Shop
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


# --- СИНХРОННЫЕ ФУНКЦИИ ЛОГИКИ (перенесены из views.py) ---
def import_shop_data_logic(shop_id: int, yaml_file_path: str = None) -> dict:
    """
    Синхронная логика импорта данных КОНКРЕТНОГО магазина.
    Не зависит от Celery или DRF.
    """
    try:
        shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
        print(f"Ошибка: магазин с ID {shop_id} не существует.")
        return {"status": "error", "message": f"Магазин с ID {shop_id} не был найден."}

    # Если yaml_file_path не был предоставлен, получаем его из модели
    if yaml_file_path is None:
        yaml_file_path = shop.get_source_file_path()
    
    # Вызываем основную функцию импорта из utils
    return load_shop_data_from_yaml(shop_id=shop.id, yaml_file_path=yaml_file_path)


def import_all_shops_data_logic() -> dict:
    """
    Синхронная логика для импорта данных *ВСЕХ* активных магазинов.
    Не зависит от Celery или DRF.
    """
    shops = Shop.objects.filter(state=True) # Получаем список АКТИВНЫХ магазинов

    results_list = []
    success_count = 0
    error_count = 0

    for shop in shops:
        yaml_file_path = shop.get_source_file_path() # Получаем путь к YAML-файлу

        # Вызываем синхронную логику импорта для одного конкретного магазина
        result = import_shop_data_logic(shop.id, yaml_file_path)
        if result and result.get("status") == "success": # Если импорт прошел успешно
            success_count += 1
            results_list.append({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "status": "success",
                "details": result.get("message", "")
            })
        else:
            # Если импорт не прошел успешно
            error_count += 1
            error_message = result.get( 
                "message", "Ошибка при загрузке данных."
            ) if result else "Неизвестная ошибка при импорте данных." 
            results_list.append({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "status": "error",
                "details": error_message
            })
    ovarall_status = "Частично успешно" if success_count > 0 and error_count > 0 \
        else ("Успешно" if success_count > 0 else "Ошибка")

    return {
        "overall_status": ovarall_status,
        "summary": f"Загружено {success_count} магазинов из {len(shops)}, Ошибок: {error_count}",
        "results": results_list
    }


# --- CELERY ЗАДАЧИ для импорта данных магазина/магазинов (вызывают синхронную логику) ---
@shared_task
def import_shop_data_task(shop_id: int, yaml_file_path: str = None) -> dict:
    """Асинхронная Celery-задача для импорта данных ОДНОГО магазина."""
    return import_shop_data_logic(shop_id=shop_id, yaml_file_path=yaml_file_path)


@shared_task
def import_all_shops_data_task() -> dict:
    """Асинхронная Celery-задача для импорта данных *ВСЕХ* активных магазинов."""
    return import_all_shops_data_logic()

