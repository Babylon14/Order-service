from rest_framework import serializers
from backend.models import ProductParameter, ProductInfo, Product


class ProductParameterSerializer(serializers.ModelSerializer):
    """Сериализатор для характеристик (параметров) товара."""
    parameter_name = serializers.CharField(source="parameter.name", read_only=True)

    class Meta:
        model = ProductParameter
        fields = ["parameter_name", "value"]  # Включаем имя параметра и его значение


class ProductInfoListSerializer(serializers.ModelSerializer):
    """Сериализатор для информации о товаре (цена, количество, магазин)."""
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_category_name = serializers.CharField(source="product.category.name", read_only=True)
    product_description = serializers.CharField(source="product.category.description", read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    product_parameters = ProductParameterSerializer(
        source="product_parameters.all", many=True, read_only=True) 

    class Meta:
        model = ProductInfo
        fields = [
            "id",
            "product_name", # Наименование товара
            "product_category_name",  # Категория
            "product_description", # Описание (из категории или ProductInfo.name)
            "shop_name", # Поставщик
            "product_parameters", # Характеристики товара
            "price", # Цена товара
            "price_rrc", # Рекомендуемая розничная цена
            "quantity", # Количество товара
        ]


  