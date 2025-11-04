import django_filters
from backend.models import Product


class ProductFilter(django_filters.FilterSet):
    """Фильтр для товаров по категории, наименованию и информации о товаре."""

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Название товара")
    category = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains", label="Название категории")
    
    shop_id = django_filters.NumberFilter(
        field_name="product_infos__shop__id", label="ID магазина")
    shop_name = django_filters.CharFilter(
        field_name="product_infos__shop__name", lookup_expr="icontains", label="Название магазина")
    price_min = django_filters.NumberFilter(
        field_name="product_infos__price", lookup_expr="gte", label="Минимальная цена")
    price_max = django_filters.NumberFilter(
        field_name="product_infos__price", lookup_expr="lte", label="Максимальная цена")
    quantity_min = django_filters.NumberFilter(
        field_name="product_infos__quantity", lookup_expr="gte", label="Минимальное количество")
    quantity_max = django_filters.NumberFilter(
        field_name="product_infos__quantity", lookup_expr="lte", label="Максимальное количество")


    class Meta:
        model = Product
        fields = [
            "name", "category", "shop_id", "shop_name",
            "price_min", "price_max", "quantity_min", "quantity_max"
        ]

        