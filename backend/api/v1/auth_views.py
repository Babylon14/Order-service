from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from backend.api.serializers import UserRegistrationSerializer
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



