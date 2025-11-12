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
    total_price = serializers.SerializerMethodField() # Общая сумма заказа
    status_display = serializers.CharField(source="get_status_display", read_only=True) # Отображаемое имя статуса

    class Meta:
        model = Order
        fields = [
            "id",             # ID заказа
            "created_at",     # Дата создания заказа
            "status",         # Статус заказа
            "status_display", # Отображаемое имя статуса (например, "Новый")
            "items",          # Позиции заказа
            "total_price",    # Общая сумма заказа
        ]

    def get_total_price(self, obj):
        """Вычисляет и возвращает общую сумму заказа."""
        total = 0
        for item in obj.items.all():  # related_name="items" из OrderItem
            total += item.product_info.price * item.quantity
        return total

