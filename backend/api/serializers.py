from rest_framework import serializers
from backend.models import User
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя с валидацией пароля."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password", "password_confirm")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        """Создает нового пользователя с хешированным паролем."""

        user = User(
            username=validated_data["email"], # Используем email в качестве username
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
        )
        user.set_password(validated_data["password"]) # Хешируем пароль
        user.save()
        return user

