from rest_framework import serializers
from backend.models import ProductParameter, ProductInfo


class ProductParameterSerializer(serializers.ModelSerializer):
    """Сериализатор для характеристик (параметров) товара."""
    parameter_name = serializers.CharField(source="parameter.name", read_only=True)

    class Meta:
        model = ProductParameter
        fields = ["parameter_name", "value"]  # Включаем имя параметра и его значение


class ProductInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для информации о товаре (цена, количество, магазин, параметры)."""
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    product_parameters = ProductParameterSerializer(
        source="product_parameters.all", many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = [
            "id", "shop_name", "price",
            "quantity", "product_parameters"
        ]  # Включаем магазин, цену, кол-во, параметры