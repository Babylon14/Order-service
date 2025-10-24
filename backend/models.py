from django.db import models


class Shop(models.Model):
    """Модель Магазина"""

    name = models.CharField(max_length=255, verbose_name="Название магазина")
    website = models.URLField(max_length=255, blank=True, verbose_name="URL магазина")

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    
class Category(models.Model):
    """Модель Категории товаров"""

    name = models.CharField(max_length=255, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    shops = models.ManyToManyField(Shop, related_name="categories", verbose_name="Магазины")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"
        ordering = ["name"]

    def __str__(self):
        return self.name




