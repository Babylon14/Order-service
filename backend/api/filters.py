import django_filters
from backend.models import ProductInfo, Product


class ProductInfoFilter(django_filters.FilterSet):
    """Фильтр для информации о товарах."""

    # Фильтрация по названию товара (через связанную модель Product)
    product_name = django_filters.CharFilter(
        field_name='product__name', lookup_expr='icontains', label="Название товара")
    # Фильтрация по категории (по ID или имени)
    category_id = django_filters.NumberFilter(
        field_name="product__category__id", label="ID категории")
    category_name = django_filters.CharFilter(
        field_name="product__category__name", lookup_expr="icontains", label="Название категории")

   # Фильтрация по информации о товаре (напрямую к ProductInfo)
    shop_id = django_filters.NumberFilter(
        field_name="shop__id", label="ID поставщика (магазина)")
    shop_name = django_filters.CharFilter(
        field_name="shop__name", lookup_expr="icontains", label="Название поставщика (магазина)")
    price_min = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="Минимальная цена")
    price_max = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="Максимальная цена")
    quantity_min = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="gte", label="Минимальное количество")
    quantity_max = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="lte", label="Максимальное количество")

    # Фильтрация по параметрам (например, значение параметра)
    parameter_value = django_filters.CharFilter(
        field_name="product_parameters__value", lookup_expr="icontains", label="Значение параметра")
    parameter_name = django_filters.CharFilter(
        field_name="product_parameters__parameter__name", lookup_expr="icontains", label="Название параметра")

    class Meta:
        model = ProductInfo
        fields = [
            "product_name", "category_id", "category_name",
            "shop_id", "shop_name", "price_min", "price_max",
            "quantity_min", "quantity_max", "parameter_value", "parameter_name",
        ]

        