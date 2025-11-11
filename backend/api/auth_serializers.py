from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from backend.models import User


# --- СЕРИАЛИЗАТОРЫ ДЛЯ РЕГИСТРАЦИИ ---
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
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"]) # Хешируем пароль
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для аутентификации(входа) пользователя."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Проверяем, существует ли пользователь с таким email
        try:
            user = User.objects.get(email__iexact=email) # iexact - нечувствительно к регистру
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный email или пароль.")
        
        # Используем authenticate, чтобы проверить пароль
        user_auth = authenticate(username=email, password=password)
        if not user_auth:
            raise serializers.ValidationError("Неверный email или пароль.")

        # Сохраняем аутентифицированного пользователя для дальнейшего использования
        attrs["user"] = user_auth
        return attrs

