from rest_framework import serializers
from backend.models import Contact


# --- СЕРИАЛИЗАТОРЫ ДЛЯ КОНТАКТОВ ---
class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор для Контактов пользователя."""

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",   # Теперь берётся из модели Contact
            "last_name",    # Теперь берётся из модели Contact
            "email",        # Теперь берётся из модели Contact
            "phone",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
        ]

