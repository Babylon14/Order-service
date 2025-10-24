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


class Product(models.Model):
    """Модель Товара"""

    name = models.CharField(max_length=255, verbose_name="Название товара")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Список товаров"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """Модель Информации о товаре"""

    name = models.CharField(max_length=255, verbose_name="Информация о товаре")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_infos", verbose_name="Товар")
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="product_infos", verbose_name="Магазин")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    price_rrc = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Рекомендуемая розничная цена")
    quantity = models.PositiveIntegerField(verbose_name="Количество на складе")

    class Meta:
        verbose_name = "Информация о товаре"
        verbose_name_plural = "Список информации о товарах"
        ordering = ["product__name", "shop__name", "price", "quantity"]

    def __str__(self):
        return f"{self.product.name} - {self.shop.name}"
    

class Parameter(models.Model):
    """Модель Параметра товара"""

    name = models.CharField(max_length=255, verbose_name="Название параметра")

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"
        ordering = ["name"]

    def __str__(self):
        return self.name
    

class ProductParameter(models.Model):
    """Модель Значения параметра товара"""

    product_info = models.ForeignKey(
        ProductInfo, on_delete=models.CASCADE, related_name="product_parameters", verbose_name="Информация о товаре")
    parameter = models.ForeignKey(
        Parameter, on_delete=models.CASCADE, related_name="product_parameters", verbose_name="Параметр")
    value = models.CharField(max_length=255, verbose_name="Значение параметра")

    class Meta:
        verbose_name = "Значение параметра товара"
        verbose_name_plural = "Список значений параметров товаров"
        ordering = ["product_info", "parameter"]

    def __str__(self):
        return f"{self.product_info.product.name} - {self.parameter.name}: {self.value}"

