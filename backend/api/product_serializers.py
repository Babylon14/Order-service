from rest_framework import serializers
from backend.models import ProductParameter, ProductInfo, Product


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


class ProductListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка товаров."""
    category_name = serializers.CharField(source="category.name", read_only=True)
    product_infos = ProductInfoSerializer(many=True, read_only=True)  # Информация о товаре

    class Meta:
        model = Product
        fields = ["id", "name", "category_name", "product_infos"]  


class ProductInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для информации о товаре (цена, количество, магазин)."""
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    product_parameters = ProductParameterSerializer(
        source="product_parameters.all", many=True, read_only=True)
    description = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = ProductInfo
        fields = ["id", "shop_name", "price", "quantity", "product_parameters", "description"]


  