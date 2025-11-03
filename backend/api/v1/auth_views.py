from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import login

from backend.api.auth_serializers import UserRegistrationSerializer, UserLoginSerializer
from backend.models import User


class UserRegistrationAPIView(CreateAPIView):
    """
    API View для регистрации пользователя.
    POST /api/v1/register/
    """
    queryset = User.objects.all() # DRF использует это для операций, хотя мы переопределяем create
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Разрешаем всем (включая неавторизованных) пользователям регистрироваться

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"status": "успешно", "message": f"Пользователь {user.username} успешно зарегистрирован."},
            status=status.HTTP_201_CREATED
        )


class UserLoginAPIView(CreateAPIView):
    """
    API View для аутентификации(входа) пользователя.
    POST /api/v1/login/
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]  # Разрешаем всем (включая неавторизованных) пользователям входить

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Логиним пользователя (создаем сессию)
        login(request, user)

        return Response(
            {"status": "успешно", "message": f"Пользователь {user.username} успешно вошел в систему."},
            status=status.HTTP_200_OK
        )
        
