from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404
import logging

from backend.api.auth_serializers import UserRegistrationSerializer
from backend.models import User, EmailConfirmation


# Настройка логгера
logger = logging.getLogger(__name__)

class UserRegistrationAPIView(CreateAPIView):
    """
    API View для РЕГИСТРАЦИИ пользователя.
    POST /api/v1/register/
    """
    queryset = User.objects.all()  # Все пользователи
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Разрешаем ВСЕМ пользователям регистрироваться

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"status": "успешно", "message": f"Пользователь {user.username} успешно зарегистрирован."},
            status=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для получения JWT, чтобы при ВХОДЕ использовать email вместо username"""
    username_field = "email" # Поле для входа

    def validate(self, attrs):
        """Переопределяем метод validate, чтобы использовать email и пароль для аутентификации"""
        email_provided = attrs.get("email")
        logger.info(f"Попытка входа с email: {email_provided}")
        
        # ВНИМАНИЕ!!! TokenObtainPairSerializer САМ ОБРАБОТАЕТ username_field = 'email'
        # и вызовет authenticate с правильными аргументами.

        try:
            # Вызов родительской валидации (аутентификации)
            data = super().validate(attrs)
            logger.info(f"Аутентификация успешна для пользователя ID: {self.user.id}")
        except Exception as err:
            logger.error(f"Ошибка валидации/аутентификации в super().validate: {err}")
            raise # Переподнимаем исключение

        # Добавляем дополнительную информацию в ответ
        user = self.user
        data["user_info"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return data
    

class UserLoginAPIView(TokenObtainPairView):
    """
    API View для аутентификации/ВХОДА пользователя с использованием JWT.
    POST /api/v1/login/
    Ожидает 'email' и 'password'.
    Возвращает 'access' и 'refresh' токены.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]  # Разрешаем ВСЕМ пользователям входить


class ConfirmEmailView(APIView):
    """
    API View для подтверждения email по токену.
    GET /api/v1/confirm-email/<uuid:token>/
    """
    permission_classes = [AllowAny]

    def get(self, request, token, format=None):
        # Получаем подтверждение по токену
        confirmation = get_object_or_404(EmailConfirmation, token=token)

        # Проверяем, истек ли срок действия подтверждения
        if confirmation.is_expired():
            confirmation.delete()  # Удаляем подтверждение, если срок действия истек
            return Response(
                {"error": "Срок действия подтверждения истек"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Активируем пользователя
        confirmation.user.is_active = True
        confirmation.user.save()

        # Отмечаем подтверждение как выполненное
        confirmation.is_confirmed = True
        confirmation.save()

        return Response(
            {
                "status": "успешно",
                "message": "Email успешно подтверждён. Вы можете войти."
            },
            status=status.HTTP_200_OK
        )



