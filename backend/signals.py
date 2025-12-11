"""Здесь будут сигналы Django"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from backend.models import Product, ProductInfo
from backend.tasks import generate_thumbnails
from imagekit.models import ProcessedImageField
from backend.redis_client import clear_product_list_cache


@receiver(post_save, sender=Product)
def process_product_image_async(sender, instance, created, **kwargs):
    """"
    Получает сигнал после сохранения объекта Product и асинхронно запускает
    задачу Celery для генерации миниатюр.
    """
    if created and instance.original_image:  # Проверяем, что изображение было загружено

        # Итерируемся по всем ProcessedImageField в модели
        for field in sender._meta.fields:
            if isinstance(field, ProcessedImageField):  

                # Вызываем Celery-задачу
                generate_thumbnails.delay(
                    app_label=sender._meta.app_label,
                    model_name=sender._meta.model_name,
                    pk=instance.pk,
                    field_name=field.name,
                )


@receiver(post_save, sender=ProductInfo)
def invalidate_product_list_cache_on_save(sender, instance, created, **kwargs):
    """
    Очищает кэш списка продуктов после сохранения (создания или обновления) 
    объекта ProductInfo.
    """
    print("--- SIGNAL: ProductInfo.post_save сработал. Очистка кэша... ---")
    
    # Прямой вызов функции очистки Redis
    deleted_count = clear_product_list_cache()
    
    if deleted_count > 0:
        print(f"--- INFO: Кэш списка продуктов очищен. Удалено ключей: {deleted_count} ---")
    else:
        print("--- INFO: Кэш списка продуктов очищен (ключи не найдены). ---")


@receiver(post_delete, sender=ProductInfo)
def invalidate_product_list_cache_on_delete(sender, instance, **kwargs):
    """
    Очищает кэш списка продуктов после удаления объекта ProductInfo.
    """
    print("--- SIGNAL: ProductInfo.post_delete сработал. Очистка кэша... ---")
    
    # Прямой вызов функции очистки Redis
    deleted_count = clear_product_list_cache()
    
    if deleted_count > 0:
        print(f"--- INFO: Кэш списка продуктов очищен. Удалено ключей: {deleted_count} ---")
    else:
        print("--- INFO: Кэш списка продуктов очищен (ключи не найдены). ---")

