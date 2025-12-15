from django.contrib import admin

from .models import Shop, ProductInfo


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    search_fields = ("name",)
    ordering = ("-name",)


@admin.register(ProductInfo)
class ProductInfoModelAdmin(admin.ModelAdmin):
    # 1. Какие поля показывать в списке (вместо id и названия)
    list_display = (
        "id", "name", "price", "price_rrc", "quantity", "shop",)
    # 2. Поля, которые будут ссылками на страницу редактирования
    list_display_links = ("id", "name")

    # 3. Фильтры справа: по статусу, дате или внешнему ключу
    list_filter = ("price", "quantity", "shop")

    # 4. Поля для поиска (поиск по БД)
    search_fields = ("name", "price", "quantity", "shop__name__startswith", "shop__id")

    # 5. Количество объектов на странице, производительность
    list_per_page = 25



