from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from backend.api.auth_serializers import UserRegistrationSerializer
from backend.models import User


class UserRegistrationAPIView(CreateAPIView):
    """
    API View для регистрации пользователя.
    POST /api/v1/register/
    """
    queryset = User.objects.all() # DRF использует это для операций, хотя мы переопределяем create
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Разрешаем всем (включая неавторизованных) пользователям регистрироваться

    def create(self, request):
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
        attrs["username"] = attrs.get("email")
        
        # Вызываем родительский метод для стандартной валидации и получения токенов
        data = super().validate(attrs)

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
    API View для аутентификации(входа) пользователя с использованием JWT.
    POST /api/v1/login/
    Ожидает 'email' и 'password'.
    Возвращает 'access' и 'refresh' токены.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]  # Разрешаем всем (включая неавторизованных) пользователям входить

