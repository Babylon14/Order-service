from django.contrib import admin

from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "website")
    search_fields = ("name", "website")
    ordering = ("-name",)


