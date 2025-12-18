from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.mail import send_mail  # Для отправки письма
from django.conf import settings    # Для доступа к настройкам
from backend.models import User, EmailConfirmation


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
        """Создает нового пользователя, деактивирует его и отправляет письмо подтверждения."""

        user = User(
            username=validated_data["email"], # Используем email в качестве username
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data["email"],
            is_active=False, # Деактивируем пользователя до подтверждения
        )
        user.set_password(validated_data["password"]) # Хешируем пароль
        user.save() # Сохраняем пользователя

        # Создание токена подтверждения
        confirmation = EmailConfirmation.objects.create(user=user)
        # Отправляем письмо
        self.send_confirmation_email(user, confirmation.token)
        return user

    def send_confirmation_email(self, user, token):
        """Отправляет письмо с ссылкой для подтверждения."""
        
        # Ссылка для подтверждения (должна вести на ваш эндпоинт активации)
        confirmation_link = f"http://127.0.0.1:8000/api/v1/confirm-email/{token}/" # Пример URL
        # Отправляем письмо
        subject = "Подтверждение регистрации"
        message = f"""
        Здравствуйте, {user.first_name or user.username}!

        Спасибо за регистрацию! Пожалуйста, подтвердите свой email, перейдя по ссылке:

        {confirmation_link}

        Ссылка действительна в течение 24-х часов.

        С уважением,
        Администрация сервиса.
        """
        send_mail(
            subject,                     # Тема письма
            message,                     # Текст письма
            settings.DEFAULT_FROM_EMAIL, # Отправитель
            [user.email],                # Отправляем письмо на email пользователя
            fail_silently=False, # Не бросать исключение, если письмо не может быть отправлено
        )


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

