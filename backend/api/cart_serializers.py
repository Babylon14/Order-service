from rest_framework import serializers
from backend.models import Cart, CartItem


# --- СЕРИАЛИЗАТОРЫ ДЛЯ КОРЗИНЫ ---
class CartItemSerializer(serializers.ModelSerializer):
    """Сериализатор для позиции в корзине."""

    product_name = serializers.CharField(source="product_info.product.name", read_only=True)
    shop_name = serializers.CharField(source="product_info.shop.name", read_only=True)
    price = serializers.DecimalField(
        source='product_info.price', max_digits=10, decimal_places=2, read_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product_name", "shop_name", "price", "quantity", "total_price"]

    def get_total_price(self, obj):
        """Вычисляет и возвращает общую сумму для этой позиции."""
        return float(obj.get_total_price())


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для Корзины"""

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "updated_at"]

    def get_total_price(self, obj):
        """Вычисляет и возвращает общую сумму для этой позиции."""
        return float(obj.get_total_price())



