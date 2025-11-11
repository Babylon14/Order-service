from rest_framework import serializers
from backend.models import Contact


# --- СЕРИАЛИЗАТОРЫ ДЛЯ КОНТАКТОВ ---
class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор для Контактов пользователя."""
    
    # Явно добавляем поля, которые берутся из связанного User
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",   # Из User
            "last_name",    # Из User
            "email",        # Из User
            "phone",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
        ]




