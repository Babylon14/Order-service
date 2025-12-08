from rest_framework import serializers
from backend.models import ProductParameter, ProductInfo, Product


# --- СЕРИАЛИЗАТОРЫ ДЛЯ ПРОДУКТОВ ---
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
    # name из ProductInfo интерпретируется как "описание"
    description = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = ProductInfo
        fields = [
            "id", "shop_name", "price",
            "quantity", "product_parameters", "description"
        ]

class ProductListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка/деталей товаров (включает список ProductInfo)."""
    category_name = serializers.CharField(source="category.name", read_only=True)
    product_infos = ProductInfoSerializer(many=True, read_only=True) # Включаем информацию о товаре (цены, магазоны и т.д.)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category_name",
            "product_infos",
        ]


# --- СЕРИАЛИЗАТОР ДЛЯ СПИСКА ProductInfo (для ProductInfoListView) ---
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


# --- СЕРИАЛИЗАТОР ДЛЯ ЗАГРУЗКИ ИЗОБРАЖЕНИЙ ПРОДУКТОВ ---
class ProductImageUploadSerializer(serializers.ModelSerializer):
    """Сериализатор только для загрузки изображения товара."""
    
    class Meta:
        model = Product
        fields = ("original_image",)
        read_only_fields = ("thumb", "detail_view")

