from django.contrib import admin

from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    search_fields = ("name",)
    ordering = ("-name",)


