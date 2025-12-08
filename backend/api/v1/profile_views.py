from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from backend.api.profile_serializers import UserProfileUpdateSerializer


User = get_user_model()

class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    API для получения и обновления профиля текущего пользователя.
    GET /api/v1/profile/
    PUT /api/v1/profile/
    PATCH /api/v1/profile/
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Возвращает текущего аутентифицированного пользователя."""
        return self.request.user

