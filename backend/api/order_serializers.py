from rest_framework import serializers
from backend.models import Order, OrderItem


# --- СЕРИАЛИЗАТОРЫ ДЛЯ ЗАКАЗА ---
class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для позиции в заказе."""
    product_name = serializers.CharField(source="product_info.product.name", read_only=True)
    shop_name = serializers.CharField(source="product_info.shop.name", read_only=True)
    price = serializers.DecimalField(
        source="product_info.price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "shop_name", "price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для заказа."""
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "status", "items"]

