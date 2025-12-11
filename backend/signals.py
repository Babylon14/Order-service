"""Здесь будут сигналы Django"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from backend.models import Product, ProductInfo
from backend.tasks import generate_thumbnails, clear_product_list_cache
from imagekit.models import ProcessedImageField


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
def invalidate_product_list_cache(sender, instance, **kwargs):
    """
    Запускает таску Celery для очистки кэша при сохранении/обновлении ProductInfo.
    """
    # Запускаем таску асинхронно
    clear_product_list_cache.delay(instance.id)

