from rest_framework import serializers
from backend.models import ProductParameter


class ProductParameterSerializer(serializers.ModelSerializer):
    """Сериализатор для характеристик (параметров) товара."""
    parameter_name = serializers.CharField(source="parameter.name", read_only=True)

    class Meta:
        model = ProductParameter
        fields = ["parameter_name", "value"]  # Включаем имя параметра и его значение

