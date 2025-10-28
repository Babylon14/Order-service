from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    """Модель Пользователя"""

    USER_TYPE_CHOICES = [
        ("client", "Клиент"),
        ("supplier", "Поставщик"),
    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default="client")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"
        ordering = ["username"]

    def __str__(self):
        return self.username


class Shop(models.Model):
    """Модель Магазина"""

    name = models.CharField(max_length=255, verbose_name="Название магазина")
    source_file = models.CharField(max_length=500, blank=True, null=True,
                                   verbose_name="Путь к файлу источника",
                                   help_text="Относительный путь к файлу (например, data/shop1.yaml)")
    state = models.BooleanField(default=True, verbose_name="Статус получения заказов")
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="shop",
        verbose_name="Пользователь магазина",
        null=True,
        blank=True,
        help_text="Пользователь, связанный с этим магазином (только для поставщиков)",
    )

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def is_supplier(self, user):
        """Проверяет, является ли пользователь поставщиком этого магазина."""
        return self.user and user.user_type == "supplier" and self.user == user

    def get_source_file_path(self):
        """Формирует путь к файлу источника данных магазина."""
        return self.source_file if self.source_file else f"data/{self.name}.yaml"


class Category(models.Model):
    """Модель Категории товаров"""

    name = models.CharField(max_length=255, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    shops = models.ManyToManyField(Shop, related_name="categories", verbose_name="Магазин")

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


class Order(models.Model):
    """Модель Заказа"""

    STATUS_CHOICES = [
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Пользователь (Клиент)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заказа")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус заказа")

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, "Неизвестно")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказов"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} - {self.get_status_display()} - Клиент: {self.user.username}"

    def is_client(self, user):
        return user.user_type == "client" and self.user == user


class OrderItem(models.Model):
    """Модель позиции в заказе"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product_info = models.ForeignKey(
        ProductInfo, on_delete=models.CASCADE, related_name="order_items", verbose_name="Информация о товаре")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Список позиций заказов"
        ordering = ["order", "product_info"]

    def __str__(self):
        return f"{self.product_info.product.name} x {self.quantity} (Заказ #{self.order.id})"


class Contact(models.Model):
    """Модель Контакта пользователя"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="contacts",
        verbose_name="Пользователь"
    )
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=100, verbose_name="Адрес")

    class Meta:
        verbose_name = "Контакт пользователя"
        verbose_name_plural = "Список контактов пользователя"
        ordering = ["user"]

    def __str__(self):
        return f"{self.user.username} - {self.phone} - {self.address}"

